#!/usr/bin/env python3
"""Haal XAUUSD-data op en print een compacte structuur-samenvatting.

Dependency-vrij (alleen stdlib). Probeert meerdere gratis bronnen in volgorde:
  1. Swissquote public quotes (live spot bid/ask)
  2. Yahoo Finance chart API, GC=F futures (15m / 1h / 4h OHLC)
  3. Stooq CSV (daily fallback)

Output:
  - data/snapshot.json  — ruwe candles + spot per timeframe
  - stdout              — samenvatting: laatste prijs, 24h high/low, recente
                          swings (fractals) en auto-fib (OTE) op de laatste leg

De analyse zelf (bias, OB/FVG, setup-template) blijft discretionair werk
volgens CLAUDE_TRADE.md — dit script levert alleen de data.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "snapshot.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; trader-data-fetch/1.0)"}


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def fetch_spot():
    """Swissquote live spot XAU/USD."""
    data = get_json(
        "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD"
    )
    best = data[0]["spreadProfilePrices"][0]
    return {"bid": best["bid"], "ask": best["ask"], "source": "swissquote"}


def fetch_yahoo(interval, range_):
    """Yahoo GC=F OHLC-candles voor een timeframe."""
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF"
        f"?interval={interval}&range={range_}"
    )
    res = get_json(url)["chart"]["result"][0]
    quote = res["indicators"]["quote"][0]
    candles = []
    for i, ts in enumerate(res["timestamp"]):
        o, h, l, c = (quote[k][i] for k in ("open", "high", "low", "close"))
        if None in (o, h, l, c):
            continue
        candles.append(
            {
                "time": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
                "open": round(o, 2),
                "high": round(h, 2),
                "low": round(l, 2),
                "close": round(c, 2),
            }
        )
    return candles


def fetch_stooq_daily():
    url = "https://stooq.com/q/d/l/?s=xauusd&i=d"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        lines = r.read().decode().strip().splitlines()
    candles = []
    for line in lines[-30:]:
        parts = line.split(",")
        if len(parts) < 5 or parts[0] == "Date":
            continue
        candles.append(
            {
                "time": parts[0],
                "open": float(parts[1]),
                "high": float(parts[2]),
                "low": float(parts[3]),
                "close": float(parts[4]),
            }
        )
    return candles


def swings(candles, width=3):
    """Simpele fractal-swings: hoogste high / laagste low binnen +/- width."""
    highs, lows = [], []
    for i in range(width, len(candles) - width):
        window = candles[i - width : i + width + 1]
        c = candles[i]
        if c["high"] == max(w["high"] for w in window):
            highs.append({"time": c["time"], "price": c["high"]})
        if c["low"] == min(w["low"] for w in window):
            lows.append({"time": c["time"], "price": c["low"]})
    return highs, lows


def auto_fib(candles):
    """Fib-niveaus (retracement) op de laatste duidelijke leg: van de meest
    recente swing naar het meest recente uiterste erna."""
    highs, lows = swings(candles)
    if not highs or not lows:
        return None
    last_high, last_low = highs[-1], lows[-1]
    # richting van de laatste leg bepalen op volgorde in de tijd
    if last_high["time"] > last_low["time"]:
        # laatste leg omhoog -> retracement voor longs
        lo, hi, direction = last_low["price"], last_high["price"], "up"
    else:
        lo, hi, direction = last_low["price"], last_high["price"], "down"
    rng = hi - lo
    if rng <= 0:
        return None
    levels = {}
    for f in (0.618, 0.705, 0.786, 0.886):
        # retracement gemeten vanaf het eind van de leg terug de leg in
        price = lo + f * rng if direction == "down" else hi - f * rng
        levels[str(f)] = round(price, 2)
    return {
        "direction": direction,
        "leg_high": hi,
        "leg_low": lo,
        "ote_levels": levels,
    }


def main():
    snapshot = {"fetched_at": datetime.now(timezone.utc).isoformat(), "timeframes": {}}
    errors = []

    try:
        snapshot["spot"] = fetch_spot()
    except Exception as e:  # noqa: BLE001
        errors.append(f"spot: {e}")

    for interval, range_ in (("15m", "5d"), ("1h", "1mo"), ("4h", "3mo")):
        try:
            candles = fetch_yahoo(interval, range_)
            highs, lows = swings(candles)
            snapshot["timeframes"][interval] = {
                "candles": candles[-120:],
                "swing_highs": highs[-6:],
                "swing_lows": lows[-6:],
                "auto_fib": auto_fib(candles[-80:]),
            }
        except Exception as e:  # noqa: BLE001
            errors.append(f"yahoo {interval}: {e}")

    if not snapshot["timeframes"]:
        try:
            candles = fetch_stooq_daily()
            snapshot["timeframes"]["1d"] = {"candles": candles, "source": "stooq"}
        except Exception as e:  # noqa: BLE001
            errors.append(f"stooq: {e}")

    if errors:
        snapshot["errors"] = errors

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, indent=2))

    # --- samenvatting naar stdout ---
    if "spot" in snapshot:
        s = snapshot["spot"]
        print(f"XAUUSD spot: bid {s['bid']} / ask {s['ask']} ({s['source']})")
    for tf, d in snapshot["timeframes"].items():
        candles = d.get("candles", [])
        if not candles:
            continue
        last = candles[-1]
        day = candles[-min(len(candles), 96 if tf == "15m" else 24) :]
        print(
            f"[{tf}] laatste close {last['close']} | "
            f"recent high {max(c['high'] for c in day)} / "
            f"low {min(c['low'] for c in day)}"
        )
        fib = d.get("auto_fib")
        if fib:
            print(
                f"      laatste leg {fib['direction']}: "
                f"{fib['leg_low']} – {fib['leg_high']} | OTE: {fib['ote_levels']}"
            )
    if errors:
        print("FOUTEN: " + "; ".join(errors), file=sys.stderr)
        if not snapshot["timeframes"] and "spot" not in snapshot:
            sys.exit(1)
    print(f"Snapshot: {OUT}")


if __name__ == "__main__":
    main()
