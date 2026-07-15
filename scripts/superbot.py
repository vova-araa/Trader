#!/usr/bin/env python3
"""Superbot: één persistent proces dat op FP Markets/IC Markets (cTrader Open
API) tegelijk twee dingen doet op hetzelfde account:

  1. SMC/ICT-executie — plaatst/annuleert de limit-orders uit
     signals/active_setups.json (zoals scripts/executor_ctrader.py), maar
     leest dat bestand elke cyclus opnieuw zodat een losse Claude-Routine
     (kill zone-analyse, een paar keer per dag) er gewoon overheen kan
     blijven schrijven.
  2. HFT/scalp-strategie — een deterministische, in code vastgelegde
     mean-reversion-scalp op M1 (Bollinger + RSI), volledig los van de
     Claude-Routine omdat die maar een paar keer per dag draait en HFT juist
     continu moet reageren.

BELANGRIJK — dit moet 24/5 doorlopen op JOUW infrastructuur (VPS o.i.d.).
Deze cloud-sessie stopt na inactiviteit en is niet geschikt om de bot zelf
te hosten; hij is wel geschikt om de code te schrijven/testen (--dry-run).

Nog niet live-geverifieerd: ik heb geen cTrader-credentials in deze sandbox
en kan dus geen echte orders/marge/volume-berekening tegen de server
verifiëren. De volume-conversie (lots -> API-eenheden) en geld/prijs-scaling
zijn gebaseerd op de officiële protobuf-veldtypes (DOUBLE = echte waarde,
INT64/UINT64 = geschaald met symbol.digits / trader.moneyDigits) — controleer
de EERSTE paar orders handmatig in de cTrader-UI voor je de bot onbeheerd
laat draaien.

Env vars (nooit in code/repo, alleen als omgevingsvariabele):
  CTRADER_CLIENT_ID / CTRADER_CLIENT_SECRET / CTRADER_ACCESS_TOKEN /
  CTRADER_ACCOUNT_ID   — cTrader Open API app + account (zie openapi.ctrader.com)
  CTRADER_ENV           demo|live (default demo)
  EXECUTOR_ARMED         moet "yes" zijn om live te mogen plaatsen (extra
                         vangrail bovenop credentials + CTRADER_ENV=live)

  RISK_PCT_PER_TRADE     risico als fractie van equity per trade, bv 0.01 = 1%
                         (default 0.01; fallback op EXECUTOR_VOLUME_LOTS als
                         equity niet bekend is)
  EXECUTOR_VOLUME_LOTS   vaste fallback-lotgrootte (default 0.01)
  MAX_MARGIN_UTILIZATION max fractie van equity die als marge gebruikt mag
                         worden, over alle open bot-posities samen (default 0.5)
  CONSECUTIVE_LOSS_LIMIT aantal verlies-trades op rij (per strategie) voor
                         een pauze (default 3)
  PAUSE_HOURS             pauzeduur na circuit-breaker trigger (default 4)
  MAX_DAILY_LOSS_PCT      dagverlies (fractie van dag-start-equity) waarbij
                         kill_switch automatisch aangaat (default 0.05 = 5%)

  HFT_ENABLED             1/0, scalper aan/uit (default 1)
  HFT_SL_POINTS           default 10.0
  HFT_TP_POINTS           default 18.0  (RR 1.8)
  HFT_MAX_SPREAD_POINTS   skip entry als spread hoger is (default 5.0)
  HFT_SESSION_START_UTC / HFT_SESSION_END_UTC  handelsvenster (default 7-20,
                         Londen-open t/m NY-sluit)

Draaien:
  python3 scripts/superbot.py --dry-run   # geen netwerk, test de pure logica
  python3 scripts/superbot.py             # live/demo naargelang env vars
"""

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "signals" / "active_setups.json"
EXEC_LOG = ROOT / "signals" / "execution_log.jsonl"

SYMBOL_NAME = "XAUUSD"
SMC_LABEL_PREFIX = "claude-trader:"
HFT_LABEL_PREFIX = "claude-hft:"

# ---------------------------------------------------------------- config ---

def _f(name, default):
    v = os.environ.get(name)
    return float(v) if v not in (None, "") else default


def _i(name, default):
    v = os.environ.get(name)
    return int(v) if v not in (None, "") else default


def _b(name, default):
    v = os.environ.get(name)
    if v in (None, ""):
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


CFG = {
    "risk_pct_per_trade": _f("RISK_PCT_PER_TRADE", 0.01),
    "fallback_lots": _f("EXECUTOR_VOLUME_LOTS", 0.01),
    "max_margin_utilization": _f("MAX_MARGIN_UTILIZATION", 0.5),
    "consecutive_loss_limit": _i("CONSECUTIVE_LOSS_LIMIT", 3),
    "pause_hours": _f("PAUSE_HOURS", 4),
    "max_daily_loss_pct": _f("MAX_DAILY_LOSS_PCT", 0.05),
    "hft_enabled": _b("HFT_ENABLED", True),
    "hft_sl_points": _f("HFT_SL_POINTS", 10.0),
    "hft_tp_points": _f("HFT_TP_POINTS", 18.0),
    "hft_max_spread_points": _f("HFT_MAX_SPREAD_POINTS", 5.0),
    "hft_session_start_utc": _i("HFT_SESSION_START_UTC", 7),
    "hft_session_end_utc": _i("HFT_SESSION_END_UTC", 20),
    "hft_cooldown_seconds": _i("HFT_COOLDOWN_SECONDS", 300),
    "hft_bb_period": _i("HFT_BB_PERIOD", 20),
    "hft_bb_stddev": _f("HFT_BB_STDDEV", 2.0),
    "hft_rsi_period": _i("HFT_RSI_PERIOD", 14),
    "hft_rsi_overbought": _f("HFT_RSI_OVERBOUGHT", 70.0),
    "hft_rsi_oversold": _f("HFT_RSI_OVERSOLD", 30.0),
    "min_volume_lots": _f("MIN_VOLUME_LOTS", 0.01),
    "lot_step": _f("LOT_STEP", 0.01),
}

MAX_OPEN_SMC_SETUPS = 3  # ongewijzigde vangrail uit executor_ctrader.py
MAX_RISK_POINTS_SMC = 30.0

HOSTS = {"demo": "demo.ctraderapi.com", "live": "live.ctraderapi.com"}
PORT = 5035


def now_utc():
    return datetime.now(timezone.utc)


# ----------------------------------------------------- pure indicator fns --

def sma(values):
    return sum(values) / len(values)


def stddev(values, mean=None):
    m = mean if mean is not None else sma(values)
    var = sum((v - m) ** 2 for v in values) / len(values)
    return math.sqrt(var)


def bollinger_bands(closes, period, n_std):
    window = closes[-period:]
    mid = sma(window)
    sd = stddev(window, mid)
    return mid - n_std * sd, mid, mid + n_std * sd


def rsi(closes, period):
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(-period, 0):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain, avg_loss = sma(gains), sma(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def hft_signal(closes, cfg=CFG):
    """Mean-reversion op Bollinger-extreem + RSI-bevestiging. closes oplopend
    in tijd (oudste eerst). Retourneert 'long', 'short' of None.
    Dit is een bewust gekozen, verdedigbare default-strategie (geen bewezen
    edge) — bedoeld om op demo te valideren voor er ooit live geld op staat.
    """
    period = cfg["hft_bb_period"]
    if len(closes) < max(period, cfg["hft_rsi_period"] + 1):
        return None
    lower, mid, upper = bollinger_bands(closes, period, cfg["hft_bb_stddev"])
    r = rsi(closes, cfg["hft_rsi_period"])
    if r is None:
        return None
    last = closes[-1]
    if last >= upper and r >= cfg["hft_rsi_overbought"]:
        return "short"
    if last <= lower and r <= cfg["hft_rsi_oversold"]:
        return "long"
    return None


def in_session(dt_utc, cfg=CFG):
    return cfg["hft_session_start_utc"] <= dt_utc.hour < cfg["hft_session_end_utc"]


# -------------------------------------------------------- risk pure logic --

def calc_volume_lots(equity, risk_points, cfg=CFG):
    """Risk-based sizing: risk_pct_per_trade van equity, omgerekend naar lots
    gegeven de SL-afstand in punten (1 lot XAUUSD = 100 oz => $100/punt)."""
    if equity is None or equity <= 0 or risk_points <= 0:
        return cfg["fallback_lots"]
    dollar_risk = equity * cfg["risk_pct_per_trade"]
    dollars_per_point_per_lot = 100.0  # 1.00 lot = 100 oz
    lots = dollar_risk / (risk_points * dollars_per_point_per_lot)
    step = cfg["lot_step"]
    lots = math.floor(lots / step) * step
    return max(lots, cfg["min_volume_lots"])


def lots_to_volume(lots, lot_size_units):
    """cTrader volume-eenheid = units * 100 (centi-units). lot_size_units komt
    live van ProtoOASymbol.lotSize. NIET geverifieerd tegen een live server —
    controleer de eerste order handmatig in de cTrader-UI."""
    return int(round(lots * lot_size_units * 100))


def scaled(raw, digits):
    return raw / (10 ** digits) if digits else float(raw)


def count_consecutive_losses(deals_desc, label_prefix):
    """deals_desc: lijst dicts {label, net_pnl}, nieuwste eerst, alleen
    closing deals (met closePositionDetail). Telt verliezen vanaf de meest
    recente trade van deze strategie tot de eerste winst of het einde."""
    n = 0
    for d in deals_desc:
        if not d["label"].startswith(label_prefix):
            continue
        if d["net_pnl"] < 0:
            n += 1
        else:
            break
    return n


def sum_realized_pnl_since(deals, label_prefix, since_ts):
    return sum(
        d["net_pnl"] for d in deals
        if d["label"].startswith(label_prefix) and d["execution_ts"] >= since_ts
    )


def day_start_ts(dt_utc):
    start = dt_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.timestamp()


# ------------------------------------------------------------ signal I/O ---

def load_signals():
    return json.loads(SIGNALS.read_text())


def save_signals(data):
    data["updated_utc"] = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    SIGNALS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def get_risk_state(data):
    return data.setdefault("risk_state", {
        "smc_paused_until_utc": None,
        "hft_paused_until_utc": None,
        "daily_loss_halt_date": None,
    })


def is_paused(risk_state, key):
    ts = risk_state.get(key)
    if not ts:
        return False
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) > now_utc()


def log_event(record):
    EXEC_LOG.parent.mkdir(parents=True, exist_ok=True)
    record.setdefault("time_utc", now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"))
    with EXEC_LOG.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False))


# --------------------------------------------------------------- dry-run ---

def self_test():
    """Draait de pure logica tegen synthetische data, zonder netwerk. Dient
    als smoke-test omdat de echte cTrader-verbinding hier niet getest kan
    worden (geen credentials/netwerktoegang in deze sandbox)."""
    print("== self-test: indicatoren ==")
    closes = [4000 + math.sin(i / 3) * 5 + i * 0.05 for i in range(40)]
    lower, mid, upper = bollinger_bands(closes, CFG["hft_bb_period"], CFG["hft_bb_stddev"])
    r = rsi(closes, CFG["hft_rsi_period"])
    sig = hft_signal(closes)
    print(f"  bollinger lower/mid/upper = {lower:.2f}/{mid:.2f}/{upper:.2f}, rsi={r:.1f}, signal={sig}")

    print("== self-test: position sizing ==")
    for equity, risk_points in [(1000, 11), (1000, 30), (200, 24)]:
        lots = calc_volume_lots(equity, risk_points)
        print(f"  equity={equity} risk_points={risk_points} -> lots={lots:.2f} "
              f"(~${lots*100*risk_points:.2f} risico)")

    print("== self-test: circuit breaker ==")
    fake_deals = [
        {"label": "claude-hft:x1", "net_pnl": -5, "execution_ts": time.time() - 100},
        {"label": "claude-hft:x2", "net_pnl": -4, "execution_ts": time.time() - 200},
        {"label": "claude-hft:x3", "net_pnl": -3, "execution_ts": time.time() - 300},
        {"label": "claude-hft:x4", "net_pnl": 6, "execution_ts": time.time() - 400},
    ]
    n = count_consecutive_losses(fake_deals, HFT_LABEL_PREFIX)
    print(f"  consecutive losses (hft) = {n} (verwacht 3)")
    assert n == 3, "consecutive-loss telling klopt niet"

    print("== self-test: session filter ==")
    in_ = in_session(datetime(2026, 7, 15, 10, 0, tzinfo=timezone.utc))
    out_ = in_session(datetime(2026, 7, 15, 2, 0, tzinfo=timezone.utc))
    print(f"  10:00 UTC in_session={in_} (verwacht True), 02:00 UTC in_session={out_} (verwacht False)")
    assert in_ and not out_

    print("\nAlle pure-logica self-tests geslaagd. Dit test GEEN live orderplaatsing,")
    print("marge- of volume-scaling tegen de echte server — verifieer de eerste")
    print("orders handmatig in de cTrader-UI voordat de bot onbeheerd draait.")


# --------------------------------------------------------------- live bot --

def run_live():
    env = os.environ.get("CTRADER_ENV", "demo")
    creds = ("CTRADER_CLIENT_ID", "CTRADER_CLIENT_SECRET",
             "CTRADER_ACCESS_TOKEN", "CTRADER_ACCOUNT_ID")
    missing = [k for k in creds if not os.environ.get(k)]
    if missing:
        sys.exit(f"Ontbrekende env vars: {', '.join(missing)} — zet ze in de omgeving "
                  f"(nooit in code/repo). Gebruik --dry-run om de logica zonder "
                  f"netwerk te testen.")
    if env == "live" and not _b("EXECUTOR_ARMED", False):
        sys.exit("CTRADER_ENV=live maar EXECUTOR_ARMED is niet 'yes' — extra "
                 "vangrail, zet EXECUTOR_ARMED=yes expliciet om live te plaatsen.")

    from ctrader_open_api import Client, Protobuf, TcpProtocol
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq, ProtoOAAccountAuthReq, ProtoOANewOrderReq,
        ProtoOACancelOrderReq, ProtoOAReconcileReq, ProtoOASymbolsListReq,
        ProtoOATraderReq, ProtoOADealListReq, ProtoOAGetTrendbarsReq,
        ProtoOASubscribeSpotsReq, ProtoOAClosePositionReq,
    )
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import (
        ProtoOAOrderType, ProtoOATradeSide, ProtoOATrendbarPeriod,
    )
    from twisted.internet import reactor, task

    host = HOSTS[env]
    client = Client(host, PORT, TcpProtocol)
    account_id = int(os.environ["CTRADER_ACCOUNT_ID"])

    state = {
        "symbol_id": None, "digits": 2, "lot_size": 100,
        "closes": deque(maxlen=200),
        "last_bid": None, "last_ask": None,
        "last_hft_trade_ts": 0.0,
        "position_labels": {},
    }

    def fail(reason):
        log_event({"event": "fatal_error", "reason": str(reason)})
        if reactor.running:
            reactor.stop()

    def fetch_trader_and_deals(cb):
        req = ProtoOATraderReq()
        req.ctidTraderAccountId = account_id
        d = client.send(req)

        def got_trader(msg):
            trader = Protobuf.extract(msg).trader
            equity = scaled(trader.balance, trader.moneyDigits or 2)
            since = now_utc() - timedelta(hours=48)
            dreq = ProtoOADealListReq()
            dreq.ctidTraderAccountId = account_id
            dreq.fromTimestamp = int(since.timestamp() * 1000)
            dreq.toTimestamp = int(now_utc().timestamp() * 1000)
            dreq.maxRows = 200
            d2 = client.send(dreq)

            def got_deals(msg2):
                res = Protobuf.extract(msg2)
                deals = []
                for deal in res.deal:
                    if not deal.HasField("closePositionDetail"):
                        continue
                    cpd = deal.closePositionDetail
                    md = cpd.moneyDigits or trader.moneyDigits or 2
                    net = scaled(cpd.grossProfit - cpd.commission - cpd.swap, md)
                    deals.append({
                        # label komt uit de lokale cache (reconcile_positions
                        # vult 'm bij elke SMC/HFT-cyclus); onbekend -> "" en
                        # telt dus nergens mee (fail-closed, geen misattributie)
                        "label": state["position_labels"].get(deal.positionId, ""),
                        "net_pnl": net,
                        "execution_ts": deal.executionTimestamp / 1000.0,
                        "position_id": deal.positionId,
                    })
                cb(equity, deals)

            d2.addCallback(got_deals).addErrback(fail)

        d.addCallback(got_trader).addErrback(fail)

    def reconcile_positions(cb):
        req = ProtoOAReconcileReq()
        req.ctidTraderAccountId = account_id
        d = client.send(req)

        def got(msg):
            res = Protobuf.extract(msg)
            positions = list(res.position)
            orders = list(res.order)
            used_margin = sum(scaled(p.usedMargin, p.moneyDigits or 2) for p in positions)
            # Labels zitten alleen op open posities/orders, niet op deals —
            # cache positionId->label zodat gesloten deals later hun strategie
            # (SMC vs HFT) kunnen terugvinden voor de circuit breaker.
            for p in positions:
                lbl = getattr(p.tradeData, "label", "")
                if lbl:
                    state["position_labels"][p.positionId] = lbl
            if len(state["position_labels"]) > 1000:
                for k in list(state["position_labels"])[:500]:
                    del state["position_labels"][k]
            cb(positions, orders, used_margin)

        d.addCallback(got).addErrback(fail)

    def place_order(direction, entry_type, price, sl, stop_dist_points,
                     tp, label, comment=""):
        def with_margin_check(equity, deals):
            reconcile_positions(lambda positions, orders, used_margin: _place(
                equity, used_margin))

        def _place(equity, used_margin):
            if equity and (used_margin / equity) > CFG["max_margin_utilization"]:
                log_event({"event": "order_rejected", "reason": "margin_utilization",
                           "used_margin": used_margin, "equity": equity, "label": label})
                return
            lots = calc_volume_lots(equity, stop_dist_points)
            volume = lots_to_volume(lots, state["lot_size"])
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = account_id
            req.symbolId = state["symbol_id"]
            req.orderType = ProtoOAOrderType.LIMIT if entry_type == "limit" else ProtoOAOrderType.MARKET
            req.tradeSide = ProtoOATradeSide.SELL if direction == "short" else ProtoOATradeSide.BUY
            req.volume = volume
            if entry_type == "limit":
                req.limitPrice = float(price)
            req.stopLoss = float(sl)
            req.takeProfit = float(tp)
            req.label = label
            req.comment = comment[:100]
            client.send(req)
            log_event({"event": "order_placed", "label": label, "direction": direction,
                       "entry_type": entry_type, "price": price, "sl": sl, "tp": tp,
                       "lots": lots, "volume": volume, "equity": equity})

        fetch_trader_and_deals(with_margin_check)

    # ---------------- SMC/ICT reconcile-cyclus (elke 60s) ----------------
    def smc_cycle():
        try:
            data = load_signals()
        except Exception as e:  # noqa: BLE001
            log_event({"event": "smc_cycle_error", "reason": str(e)})
            return
        risk_state = get_risk_state(data)
        if data.get("kill_switch"):
            enforce_kill_switch()
            log_event({"event": "kill_switch_active"})
            return
        if is_paused(risk_state, "smc_paused_until_utc"):
            log_event({"event": "smc_paused", "until": risk_state["smc_paused_until_utc"]})
            return

        now = now_utc()
        actionable = []
        for s in data.get("setups", []):
            if s.get("status") != "active" or s.get("conviction") not in ("A", "B"):
                continue
            valid_until = datetime.fromisoformat(s["valid_until_utc"].replace("Z", "+00:00"))
            if valid_until <= now:
                continue
            risk_points = abs(s["entry"] - s["stop_loss"])
            if risk_points <= 0 or risk_points > MAX_RISK_POINTS_SMC or not s.get("take_profits"):
                continue
            actionable.append(s)
        actionable = actionable[:MAX_OPEN_SMC_SETUPS]

        def with_positions(positions, orders, used_margin):
            existing = {getattr(o.tradeData, "label", "") for o in orders
                        if getattr(o.tradeData, "label", "").startswith(SMC_LABEL_PREFIX)}
            for s in actionable:
                label = SMC_LABEL_PREFIX + s["id"]
                if label in existing:
                    continue
                risk_points = abs(s["entry"] - s["stop_loss"])
                place_order(s["direction"], "limit", s["entry"], s["stop_loss"],
                            risk_points, s["take_profits"][0], label,
                            s.get("invalidation", ""))

        reconcile_positions(with_positions)

    def _cancel(order_id):
        req = ProtoOACancelOrderReq()
        req.ctidTraderAccountId = account_id
        req.orderId = order_id
        return req

    def _close(position_id, volume):
        req = ProtoOAClosePositionReq()
        req.ctidTraderAccountId = account_id
        req.positionId = position_id
        req.volume = volume
        return req

    def enforce_kill_switch():
        """Annuleert ALLE pending bot-orders én sluit ALLE open bot-posities
        (SMC + HFT). 'stop trading' moet echt alles platgooien, niet alleen
        nieuwe orders blokkeren."""
        def with_positions(positions, orders, used_margin):
            for o in orders:
                label = getattr(o.tradeData, "label", "")
                if label.startswith(SMC_LABEL_PREFIX) or label.startswith(HFT_LABEL_PREFIX):
                    client.send(_cancel(o.orderId))
                    log_event({"event": "kill_switch_cancel_order", "label": label})
            for p in positions:
                label = getattr(p.tradeData, "label", "")
                if label.startswith(SMC_LABEL_PREFIX) or label.startswith(HFT_LABEL_PREFIX):
                    client.send(_close(p.positionId, p.tradeData.volume))
                    log_event({"event": "kill_switch_close_position", "label": label})

        reconcile_positions(with_positions)

    # ---------------- HFT-scalp-cyclus (elke 20s) ----------------
    def hft_cycle():
        if not CFG["hft_enabled"]:
            return
        try:
            data = load_signals()
        except Exception as e:  # noqa: BLE001
            log_event({"event": "hft_cycle_error", "reason": str(e)})
            return
        risk_state = get_risk_state(data)
        if data.get("kill_switch"):
            return
        if is_paused(risk_state, "hft_paused_until_utc"):
            return
        if not in_session(now_utc()):
            return
        if time.time() - state["last_hft_trade_ts"] < CFG["hft_cooldown_seconds"]:
            return
        if state["last_bid"] is None or state["last_ask"] is None:
            return
        spread = state["last_ask"] - state["last_bid"]
        if spread > CFG["hft_max_spread_points"]:
            log_event({"event": "hft_skip_spread", "spread": spread})
            return
        if len(state["closes"]) < max(CFG["hft_bb_period"], CFG["hft_rsi_period"] + 1):
            return

        sig = hft_signal(list(state["closes"]))
        if sig is None:
            return

        def with_positions(positions, orders, used_margin):
            open_hft = [p for p in positions
                        if getattr(p.tradeData, "label", "").startswith(HFT_LABEL_PREFIX)]
            if open_hft:
                return  # max 1 gelijktijdige scalp-positie, bewust simpel gehouden
            price = state["last_ask"] if sig == "long" else state["last_bid"]
            sl = price - CFG["hft_sl_points"] if sig == "long" else price + CFG["hft_sl_points"]
            tp = price + CFG["hft_tp_points"] if sig == "long" else price - CFG["hft_tp_points"]
            label = f"{HFT_LABEL_PREFIX}{int(time.time())}"
            place_order(sig, "market", price, sl, CFG["hft_sl_points"], tp, label,
                        "bollinger+rsi mean-reversion scalp")
            state["last_hft_trade_ts"] = time.time()

        reconcile_positions(with_positions)

    def refresh_trendbars():
        req = ProtoOAGetTrendbarsReq()
        req.ctidTraderAccountId = account_id
        req.symbolId = state["symbol_id"]
        req.period = ProtoOATrendbarPeriod.M1
        req.count = 100

        def got(msg):
            res = Protobuf.extract(msg)
            closes = []
            for tb in res.trendbar:
                low = scaled(tb.low, state["digits"])
                close = low + scaled(tb.deltaClose, state["digits"])
                closes.append(close)
            if closes:
                state["closes"] = deque(closes, maxlen=200)

        d = client.send(req)
        d.addCallback(got).addErrback(fail)

    # ---------------- risk-gate-cyclus (elke 5 min) ----------------
    def risk_gate_cycle():
        def with_data(equity, deals):
            data = load_signals()
            risk_state = get_risk_state(data)
            changed = False

            deals_desc = sorted(deals, key=lambda d: -d["execution_ts"])
            for prefix, key in ((SMC_LABEL_PREFIX, "smc_paused_until_utc"),
                                 (HFT_LABEL_PREFIX, "hft_paused_until_utc")):
                n_loss = count_consecutive_losses(deals_desc, prefix)
                if n_loss >= CFG["consecutive_loss_limit"] and not is_paused(risk_state, key):
                    until = now_utc() + timedelta(hours=CFG["pause_hours"])
                    risk_state[key] = until.strftime("%Y-%m-%dT%H:%M:%SZ")
                    changed = True
                    log_event({"event": "circuit_breaker_paused", "strategy": prefix,
                               "consecutive_losses": n_loss, "until": risk_state[key]})

            day_pnl = sum_realized_pnl_since(deals, "", day_start_ts(now_utc()))
            if equity and day_pnl < 0 and abs(day_pnl) / equity >= CFG["max_daily_loss_pct"]:
                if not data.get("kill_switch"):
                    data["kill_switch"] = True
                    changed = True
                    log_event({"event": "daily_loss_kill_switch", "day_pnl": day_pnl,
                               "equity": equity})

            if changed:
                save_signals(data)

        fetch_trader_and_deals(with_data)

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
        d.addCallback(resolve_symbol).addErrback(fail)

    def resolve_symbol(msg):
        res = Protobuf.extract(msg)
        for sym in res.symbol:
            if sym.symbolName.upper().replace(".", "") == SYMBOL_NAME:
                state["symbol_id"] = sym.symbolId
                break
        if state["symbol_id"] is None:
            return fail(f"symbool {SYMBOL_NAME} niet gevonden")

        from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASymbolByIdReq
        req = ProtoOASymbolByIdReq()
        req.ctidTraderAccountId = account_id
        req.symbolId.append(state["symbol_id"])
        d = client.send(req)
        d.addCallback(got_symbol_details).addErrback(fail)

    def got_symbol_details(msg):
        res = Protobuf.extract(msg)
        sym = res.symbol[0]
        state["digits"] = sym.digits
        state["lot_size"] = sym.lotSize
        log_event({"event": "startup", "symbol_id": state["symbol_id"],
                   "digits": state["digits"], "lot_size": state["lot_size"],
                   "env": env, "cfg": CFG})

        sub = ProtoOASubscribeSpotsReq()
        sub.ctidTraderAccountId = account_id
        sub.symbolId.append(state["symbol_id"])
        client.send(sub)

        refresh_trendbars()
        task.LoopingCall(refresh_trendbars).start(20, now=False)
        task.LoopingCall(smc_cycle).start(60, now=True)
        task.LoopingCall(hft_cycle).start(20, now=False)
        task.LoopingCall(risk_gate_cycle).start(300, now=True)

    def on_message(msg):
        from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASpotEvent
        if msg.payloadType == ProtoOASpotEvent().payloadType:
            ev = Protobuf.extract(msg)
            if ev.bid:
                state["last_bid"] = scaled(ev.bid, state["digits"])
            if ev.ask:
                state["last_ask"] = scaled(ev.ask, state["digits"])

    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(lambda _, reason: log_event(
        {"event": "disconnected", "reason": str(reason)}))
    client.setMessageReceivedCallback(lambda _, msg: on_message(msg))
    client.startService()
    reactor.run()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                     help="test alleen de pure logica, geen netwerk/orders")
    args = ap.parse_args()
    if args.dry_run:
        self_test()
        return
    run_live()


if __name__ == "__main__":
    main()
