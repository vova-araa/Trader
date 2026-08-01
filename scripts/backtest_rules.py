#!/usr/bin/env python3
"""Regel-backtester: speelt de MECHANISCHE regels uit risk_guard.py terug op
historische XAUUSD-candles, zodat we kunnen VERIFIËREN dat de aangescherpte regels
(range-rand + min-stop + RR + circuit breaker) daadwerkelijk beter presteren dan de
-551-week — i.p.v. het alleen in docs te beweren.

(Anders dan scripts/backtest.py, dat de handmatige trade-ledger analyseert, draait
deze de regels zelf over een candle-reeks — de "run backtests"-stap uit de
TradingView-MCP-workflow, maar op ónze regels en zonder externe MCP.)

Deze backtester importeert `risk_guard.structural_reject_reason`, dus hij gebruikt
EXACT dezelfde vangrails als de live-executor en de trade-cycle. Geen aparte logica
die uit de pas kan lopen.

Data-invoer (zonder netwerk in de sandbox — draai lokaal of geef een bestand):
  - Yahoo v8 chart-JSON  (zoals scripts/fetch_xauusd.py / query1.finance.yahoo.com):
      python3 scripts/backtest_rules.py --yahoo data/candles_1h.json
  - Simpele candle-lijst  [{"t":..,"o":..,"h":..,"l":..,"c":..}, ...]:
      python3 scripts/backtest_rules.py --candles data/candles.json

Strategie (range-modus, zelfde als strategies/xauusd_range_ote.pine):
  - range_high/low = hoogste high / laagste low over de laatste --range-len bars
  - short alleen in de top-band (>= range_high - EDGE_BUFFER) met ruimte omlaag
  - long  alleen in de low-band  (<= range_low  + EDGE_BUFFER) met ruimte omhoog
  - stop buiten de rand, minimaal MIN_STOP_POINTS; TP1 op RR>=--rr
  - circuit breaker: na MAX_CONSECUTIVE_LOSSES verliezen op rij of <= -MAX_WEEKLY_LOSS_R
    per ISO-week worden nieuwe entries geblokkeerd (reset op de weekrol)

Uitvoer: aantal trades, win%, som R, gemiddelde R, max drawdown (in R) en hoeveel
kandidaat-entries de circuit breaker heeft tegengehouden.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import risk_guard  # noqa: E402  (zelfde structurele vangrails als live)

MIN_STOP = risk_guard.MIN_STOP_POINTS
EDGE = risk_guard.EDGE_BUFFER
ROOM = risk_guard.MIN_ROOM
MAX_CONSEC = risk_guard.MAX_CONSECUTIVE_LOSSES
MAX_WEEK_R = risk_guard.MAX_WEEKLY_LOSS_R


def load_yahoo(path):
    """Yahoo v8 chart-JSON -> lijst candles [{t,o,h,l,c}]."""
    doc = json.loads(Path(path).read_text())
    res = doc["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    out = []
    for i, t in enumerate(ts):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        out.append({"t": t, "o": o, "h": h, "l": l, "c": c})
    return out


def load_candles(path):
    data = json.loads(Path(path).read_text())
    out = []
    for r in data:
        out.append({"t": r.get("t"), "o": float(r["o"]), "h": float(r["h"]),
                    "l": float(r["l"]), "c": float(r["c"])})
    return out


def _week_key(t):
    """ISO-weeksleutel voor de weekrol-reset van de circuit breaker."""
    if t is None:
        return None
    if isinstance(t, (int, float)):
        dt = datetime.fromtimestamp(t, tz=timezone.utc)
    else:
        dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    iso = dt.isocalendar()
    return (iso[0], iso[1])


def backtest(candles, range_len=96, rr=2.0):
    trades = []
    blocked = 0
    consec = 0
    week = None
    week_r = 0.0
    equity_r = 0.0
    peak_r = 0.0
    max_dd = 0.0
    open_pos = None  # dict met direction, entry, stop, tp

    for i in range(range_len, len(candles)):
        bar = candles[i]
        wk = _week_key(bar["t"])
        if wk != week:
            week, week_r, consec = wk, 0.0, 0  # weekrol: breaker reset

        # 1) lopende positie afwikkelen op deze bar
        if open_pos:
            hit = None
            if open_pos["direction"] == "short":
                # conservatief: stop vóór TP als beide in dezelfde bar raken
                if bar["h"] >= open_pos["stop"]:
                    hit = -1.0
                elif bar["l"] <= open_pos["tp"]:
                    hit = rr
            else:
                if bar["l"] <= open_pos["stop"]:
                    hit = -1.0
                elif bar["h"] >= open_pos["tp"]:
                    hit = rr
            if hit is not None:
                trades.append({**open_pos, "r": hit, "exit_i": i})
                equity_r += hit
                week_r += hit
                consec = consec + 1 if hit < 0 else 0
                peak_r = max(peak_r, equity_r)
                max_dd = min(max_dd, equity_r - peak_r)
                open_pos = None

        if open_pos:
            continue  # nog in trade, geen nieuwe entry

        # 2) range bepalen uit de vorige range_len bars
        window = candles[i - range_len:i]
        rh = max(c["h"] for c in window)
        rl = min(c["l"] for c in window)
        price = bar["c"]

        # 3) kandidaat-setups (short top-band / long low-band) opstellen en
        #    door DEZELFDE structurele guard halen als live
        for direction in ("short", "long"):
            if direction == "short":
                stop = max(rh + 2, price + MIN_STOP)
                risk = stop - price
                tp = price - rr * risk
            else:
                stop = min(rl - 2, price - MIN_STOP)
                risk = price - stop
                tp = price + rr * risk
            if risk <= 0:
                continue
            setup = {
                "direction": direction, "entry": price, "stop_loss": stop,
                "regime": "range", "range_low": rl, "range_high": rh,
            }
            if risk_guard.structural_reject_reason(setup):
                continue  # geen rand / te krap / midden — overslaan
            # setup is structureel geldig -> zou de breaker 'm blokkeren?
            if consec >= MAX_CONSEC or week_r <= -MAX_WEEK_R:
                blocked += 1
                continue
            open_pos = {"direction": direction, "entry": price,
                        "stop": stop, "tp": tp, "entry_i": i}
            break  # max één positie tegelijk

    wins = [t for t in trades if t["r"] > 0]
    n = len(trades)
    total_r = round(sum(t["r"] for t in trades), 2)
    return {
        "candles": len(candles),
        "trades": n,
        "wins": len(wins),
        "win_pct": round(100 * len(wins) / n, 1) if n else 0.0,
        "total_r": total_r,
        "avg_r": round(total_r / n, 3) if n else 0.0,
        "max_drawdown_r": round(max_dd, 2),
        "blocked_by_breaker": blocked,
        "range_len": range_len,
        "rr": rr,
        "rules": {
            "min_stop": MIN_STOP, "edge_buffer": EDGE, "min_room": ROOM,
            "max_consec_losses": MAX_CONSEC, "max_weekly_loss_r": MAX_WEEK_R,
        },
    }


def main():
    p = argparse.ArgumentParser(description="XAUUSD range-regel backtester")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--yahoo", help="Yahoo v8 chart-JSON bestand")
    src.add_argument("--candles", help="Simpele candle-lijst JSON [{t,o,h,l,c}]")
    p.add_argument("--range-len", type=int, default=96)
    p.add_argument("--rr", type=float, default=2.0)
    args = p.parse_args()

    candles = load_yahoo(args.yahoo) if args.yahoo else load_candles(args.candles)
    if len(candles) <= args.range_len:
        sys.exit(f"Te weinig candles ({len(candles)}) voor range-len {args.range_len}")
    stats = backtest(candles, args.range_len, args.rr)
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
