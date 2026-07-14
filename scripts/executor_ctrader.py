#!/usr/bin/env python3
"""Executor: plaatst setups uit signals/active_setups.json als limit orders
(met SL + TP) op een FP Markets cTrader-account via de Spotware Open API.

Vereist (pip): ctrader-open-api  (officiële Spotware SDK, twisted-based)
Vereist (env vars — zet ze in de omgeving, NOOIT in code of repo):
  CTRADER_CLIENT_ID      app client-id       (openapi.ctrader.com)
  CTRADER_CLIENT_SECRET  app secret
  CTRADER_ACCESS_TOKEN   OAuth access token  (scope: trading)
  CTRADER_ACCOUNT_ID     ctidTraderAccountId (numeriek)
  CTRADER_ENV            "demo" | "live"     (default: demo)

Vangrails (hard, niet configureerbaar zonder code-wijziging):
  - alleen setups met conviction A of B en status "active"
  - kill_switch=true in het signaalbestand => alles annuleren, niets plaatsen
  - verlopen setups (valid_until_utc) worden geannuleerd, niet geplaatst
  - elke order krijgt ALTIJD SL en TP1 mee (geen SL = geen order, regel 5)
  - MAX_RISK_POINTS begrenst de afstand entry->SL; groter = order geweigerd
  - MAX_OPEN_SETUPS begrenst het aantal gelijktijdige executor-orders
  - order-label bevat het setup-id zodat orders idempotent gesynct worden
    (bestaat de order al, dan wordt hij niet dubbel geplaatst)

Draaien: python3 scripts/executor_ctrader.py [--dry-run]
  --dry-run: print wat er zou gebeuren zonder te verbinden/plaatsen.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SIGNALS = Path(__file__).resolve().parent.parent / "signals" / "active_setups.json"

VOLUME_LOTS = float(os.environ.get("EXECUTOR_VOLUME_LOTS", "0.01"))  # microlot default
MAX_RISK_POINTS = 30.0   # entry->SL afstand; groter = weigeren
MAX_OPEN_SETUPS = 3
LABEL_PREFIX = "claude-trader:"
SYMBOL_NAME = "XAUUSD"

HOSTS = {"demo": "demo.ctraderapi.com", "live": "live.ctraderapi.com"}
PORT = 5035


def load_signals():
    data = json.loads(SIGNALS.read_text())
    now = datetime.now(timezone.utc)
    actionable, expired = [], []
    for s in data.get("setups", []):
        valid_until = datetime.fromisoformat(s["valid_until_utc"].replace("Z", "+00:00"))
        if s.get("status") != "active" or valid_until <= now:
            expired.append(s)
            continue
        if s.get("conviction") not in ("A", "B"):
            continue  # C = advies, geen order (vangrail)
        risk = abs(s["entry"] - s["stop_loss"])
        if risk > MAX_RISK_POINTS or risk <= 0:
            print(f"WEIGER {s['id']}: risico {risk:.1f} pt buiten limiet", file=sys.stderr)
            continue
        if not s.get("take_profits"):
            print(f"WEIGER {s['id']}: geen TP", file=sys.stderr)
            continue
        actionable.append(s)
    return data, actionable[:MAX_OPEN_SETUPS], expired


def main():
    dry = "--dry-run" in sys.argv
    data, setups, expired = load_signals()

    if data.get("kill_switch"):
        print("KILL SWITCH ACTIEF: alle executor-orders annuleren, niets plaatsen.")
        if dry:
            return
    if dry:
        for s in setups:
            print(
                f"[DRY] {s['direction'].upper()} LIMIT {SYMBOL_NAME} @ {s['entry']} "
                f"SL {s['stop_loss']} TP {s['take_profits'][0]} "
                f"({VOLUME_LOTS} lots, label {LABEL_PREFIX}{s['id']})"
            )
        for s in expired:
            print(f"[DRY] CANCEL indien open: {LABEL_PREFIX}{s['id']}")
        return

    env = os.environ.get("CTRADER_ENV", "demo")
    missing = [k for k in ("CTRADER_CLIENT_ID", "CTRADER_CLIENT_SECRET",
                           "CTRADER_ACCESS_TOKEN", "CTRADER_ACCOUNT_ID")
               if not os.environ.get(k)]
    if missing:
        sys.exit(f"Ontbrekende env vars: {', '.join(missing)} — zet ze in de omgeving.")

    # Spotware Open API (protobuf over TLS). Import hier zodat --dry-run
    # zonder dependency werkt.
    from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints, Auth  # noqa: F401
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (  # noqa: F401
        ProtoOAApplicationAuthReq, ProtoOAAccountAuthReq, ProtoOANewOrderReq,
        ProtoOACancelOrderReq, ProtoOAReconcileReq, ProtoOASymbolsListReq,
    )
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import (  # noqa: F401
        ProtoOAOrderType, ProtoOATradeSide,
    )
    from twisted.internet import reactor

    host = HOSTS[env]
    client = Client(host, PORT, TcpProtocol)
    account_id = int(os.environ["CTRADER_ACCOUNT_ID"])
    state = {"symbol_id": None, "existing_labels": set()}

    def fail(reason):
        print(f"FOUT: {reason}", file=sys.stderr)
        if reactor.running:
            reactor.stop()

    def on_connected(_):
        req = ProtoOAApplicationAuthReq()
        req.clientId = os.environ["CTRADER_CLIENT_ID"]
        req.clientSecret = os.environ["CTRADER_CLIENT_SECRET"]
        d = client.send(req)
        d.addCallback(auth_account).addErrback(fail)

    def auth_account(_):
        req = ProtoOAAccountAuthReq()
        req.ctidTraderAccountId = account_id
        req.accessToken = os.environ["CTRADER_ACCESS_TOKEN"]
        d = client.send(req)
        d.addCallback(get_symbols).addErrback(fail)

    def get_symbols(_):
        req = ProtoOASymbolsListReq()
        req.ctidTraderAccountId = account_id
        d = client.send(req)
        d.addCallback(reconcile).addErrback(fail)

    def reconcile(msg):
        res = Protobuf.extract(msg)
        for sym in res.symbol:
            if sym.symbolName.upper().replace(".", "") == SYMBOL_NAME:
                state["symbol_id"] = sym.symbolId
                break
        if state["symbol_id"] is None:
            return fail(f"symbool {SYMBOL_NAME} niet gevonden op account")
        req = ProtoOAReconcileReq()
        req.ctidTraderAccountId = account_id
        d = client.send(req)
        d.addCallback(place_orders).addErrback(fail)

    def place_orders(msg):
        res = Protobuf.extract(msg)
        for order in getattr(res, "order", []):
            label = getattr(order.tradeData, "label", "")
            if label.startswith(LABEL_PREFIX):
                state["existing_labels"].add(label)
        wanted = {LABEL_PREFIX + s["id"] for s in setups}

        # kill switch of verlopen: annuleer executor-orders die niet meer horen
        for order in getattr(res, "order", []):
            label = getattr(order.tradeData, "label", "")
            if label.startswith(LABEL_PREFIX) and (
                data.get("kill_switch") or label not in wanted
            ):
                creq = ProtoOACancelOrderReq()
                creq.ctidTraderAccountId = account_id
                creq.orderId = order.orderId
                client.send(creq)
                print(f"CANCEL {label}")

        if not data.get("kill_switch"):
            for s in setups:
                label = LABEL_PREFIX + s["id"]
                if label in state["existing_labels"]:
                    print(f"SKIP {label}: staat al open")
                    continue
                req = ProtoOANewOrderReq()
                req.ctidTraderAccountId = account_id
                req.symbolId = state["symbol_id"]
                req.orderType = ProtoOAOrderType.LIMIT
                req.tradeSide = (
                    ProtoOATradeSide.SELL if s["direction"] == "short"
                    else ProtoOATradeSide.BUY
                )
                # cTrader volume: 1 lot = 100 (in units van 0.01 lot), *100 => centilots
                req.volume = int(VOLUME_LOTS * 10000000 / 100)  # lots -> volume units
                req.limitPrice = float(s["entry"])
                req.stopLoss = float(s["stop_loss"])
                req.takeProfit = float(s["take_profits"][0])
                req.label = label
                req.comment = s.get("invalidation", "")[:100]
                client.send(req)
                print(
                    f"PLAATS {s['direction'].upper()} LIMIT @ {s['entry']} "
                    f"SL {s['stop_loss']} TP {s['take_profits'][0]} ({label})"
                )
        reactor.callLater(3, reactor.stop)

    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(lambda _, reason: None)
    client.startService()
    reactor.run()


if __name__ == "__main__":
    main()
