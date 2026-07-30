#!/usr/bin/env python3
"""Risk-guard: mechanische vangrails die de verliespatronen van week 27-30/07
(6 shorts, -551 realised) in de toekomst blokkeren — afgedwongen in code,
niet afhankelijk van discipline.

Twee lagen:

1. STRUCTUREEL (per setup) — `structural_reject_reason(setup)`:
   - MIN_STOP_POINTS: geen stop binnen de intraday-ruis (Rule 18).
   - regime verplicht (range|trend) — je moet de markt éérst classificeren (Rule 16).
   - regime=range: alleen aan een RAND traden (Rule 16/17):
       short alleen in de top-band (entry >= range_high - EDGE_BUFFER),
       long  alleen in de low-band (entry <= range_low + EDGE_BUFFER),
       plus MIN_ROOM ruimte naar de overkant. Geen trades in het midden.
   - regime=trend: alleen trend-mee (htf_bias moet met de richting matchen, Rule 14).

2. PORTFOLIO (circuit breaker) — `can_trade()`:
   - MAX_CONSECUTIVE_LOSSES: na N verliezen op rij stopt de bot met plaatsen.
   - MAX_WEEKLY_LOSS_R: onder -X R deze week => geen nieuwe orders tot de week
     rolt of de gebruiker expliciet hervat.
   Bron van waarheid: signals/trade_results.jsonl (elke gesloten trade: {t, r, pnl}).

CLI:
  python3 scripts/risk_guard.py status
  python3 scripts/risk_guard.py record --r -1 --pnl -66.30 --note "range-short 4033"
  python3 scripts/risk_guard.py resume   # override de halt bewust (deze week)
  python3 scripts/risk_guard.py reset     # override wissen
"""

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "signals" / "trade_results.jsonl"
STATE = ROOT / "signals" / "risk_state.json"

# --- structurele drempels (env-overschrijfbaar) ---
MIN_STOP_POINTS = float(os.environ.get("MIN_STOP_POINTS", "12"))
EDGE_BUFFER = float(os.environ.get("EDGE_BUFFER", "30"))     # afstand tot de rand
MIN_ROOM = float(os.environ.get("MIN_ROOM", "30"))           # ruimte naar de overkant

# --- circuit breaker (env-overschrijfbaar) ---
MAX_CONSECUTIVE_LOSSES = int(os.environ.get("MAX_CONSECUTIVE_LOSSES", "2"))
MAX_WEEKLY_LOSS_R = float(os.environ.get("MAX_WEEKLY_LOSS_R", "3.0"))


def structural_reject_reason(s):
    """Geef een reden-string als de setup structureel geweigerd moet worden,
    anders None. Puur mechanisch — geen discretie."""
    d = s.get("direction")
    entry = s.get("entry")
    sl = s.get("stop_loss")
    if entry is None or sl is None:
        return "geen entry/stop_loss"
    risk = abs(entry - sl)
    if risk < MIN_STOP_POINTS:
        return (f"stop {risk:.1f}pt < {MIN_STOP_POINTS:.0f}pt minimum — binnen de "
                f"intraday-ruis [Rule 18]")
    regime = s.get("regime")
    if regime not in ("range", "trend"):
        return "geen 'regime' (range|trend) opgegeven — classificeer eerst [Rule 16]"
    if regime == "range":
        rl, rh = s.get("range_low"), s.get("range_high")
        if rl is None or rh is None:
            return "regime=range vereist range_low én range_high [Rule 16]"
        if rh - rl < 2 * EDGE_BUFFER:
            return (f"range {rl:g}-{rh:g} te smal (<{2*EDGE_BUFFER:.0f}pt) om aan een "
                    f"rand te traden [Rule 16]")
        if d == "short":
            if entry < rh - EDGE_BUFFER:
                return (f"short niet aan de range-top (entry {entry:g} < "
                        f"{rh:g}-{EDGE_BUFFER:.0f}) — geen midden-trades [Rule 17]")
            if entry - rl < MIN_ROOM:
                return (f"short te weinig ruimte omlaag naar {rl:g} "
                        f"(<{MIN_ROOM:.0f}pt) [Rule 17]")
        elif d == "long":
            if entry > rl + EDGE_BUFFER:
                return (f"long niet aan de range-low (entry {entry:g} > "
                        f"{rl:g}+{EDGE_BUFFER:.0f}) — geen midden-trades [Rule 17]")
            if rh - entry < MIN_ROOM:
                return (f"long te weinig ruimte omhoog naar {rh:g} "
                        f"(<{MIN_ROOM:.0f}pt) [Rule 17]")
    else:  # trend
        bias = s.get("htf_bias")
        if bias not in ("bearish", "bullish"):
            return "regime=trend vereist htf_bias (bearish|bullish) [Rule 16]"
        if d == "short" and bias != "bearish":
            return "short tegen een bullish HTF-trend — niet toegestaan [Rule 14]"
        if d == "long" and bias != "bullish":
            return "long tegen een bearish HTF-trend — niet toegestaan [Rule 14]"
    return None


def _load_results():
    if not RESULTS.exists():
        return []
    out = []
    for line in RESULTS.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _week_start(dt):
    monday = dt - timedelta(days=dt.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _override():
    if not STATE.exists():
        return None
    try:
        return json.loads(STATE.read_text())
    except json.JSONDecodeError:
        return None


def compute_state(now=None):
    now = now or datetime.now(timezone.utc)
    ws = _week_start(now)
    results = _load_results()

    consec = 0
    for r in reversed(results):
        if float(r.get("r", 0)) < 0:
            consec += 1
        else:
            break

    week_r = 0.0
    week_pnl = 0.0
    for r in results:
        try:
            t = datetime.fromisoformat(r["t"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        if t >= ws:
            week_r += float(r.get("r", 0))
            week_pnl += float(r.get("pnl", 0) or 0)

    reasons = []
    if consec >= MAX_CONSECUTIVE_LOSSES:
        reasons.append(f"{consec} verliezen op rij (limiet {MAX_CONSECUTIVE_LOSSES})")
    if week_r <= -MAX_WEEKLY_LOSS_R:
        reasons.append(f"week {week_r:+.2f}R (limiet -{MAX_WEEKLY_LOSS_R:.1f}R)")

    # manueel override geldt alleen binnen dezelfde week
    ov = _override()
    override_active = bool(
        ov and ov.get("resume_override")
        and ov.get("override_week") == ws.strftime("%Y-%m-%d"))

    return {
        "week_start": ws.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "week_r": round(week_r, 2),
        "week_pnl": round(week_pnl, 2),
        "consecutive_losses": consec,
        "n_results": len(results),
        "halted": bool(reasons) and not override_active,
        "raw_halt": bool(reasons),
        "reasons": reasons,
        "override_active": override_active,
    }


def can_trade(now=None):
    st = compute_state(now)
    if st["halted"]:
        return False, "; ".join(st["reasons"]), st
    return True, "", st


def record_result(r, pnl=None, note="", t=None):
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "t": (t or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "r": round(float(r), 2),
    }
    if pnl is not None:
        rec["pnl"] = round(float(pnl), 2)
    if note:
        rec["note"] = note
    with RESULTS.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    # een winst wist een bewust override (schone lei)
    if rec["r"] > 0 and STATE.exists():
        STATE.unlink()
    return rec


def _set_override(active: bool):
    if not active:
        if STATE.exists():
            STATE.unlink()
        return
    ws = _week_start(datetime.now(timezone.utc))
    STATE.write_text(json.dumps({
        "resume_override": True,
        "override_week": ws.strftime("%Y-%m-%d"),
        "set_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }, indent=2) + "\n")


def main():
    p = argparse.ArgumentParser(description="Risk-guard circuit breaker")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status")
    rec = sub.add_parser("record")
    rec.add_argument("--r", type=float, required=True, help="resultaat in R")
    rec.add_argument("--pnl", type=float, default=None, help="realised P&L in valuta")
    rec.add_argument("--note", default="")
    sub.add_parser("resume")
    sub.add_parser("reset")
    args = p.parse_args()

    if args.cmd == "record":
        r = record_result(args.r, args.pnl, args.note)
        print(f"Genoteerd: {r}")
        st = compute_state()
        print(f"Status: week {st['week_r']:+.2f}R, {st['consecutive_losses']} "
              f"verlies op rij, halted={st['halted']}")
    elif args.cmd == "resume":
        _set_override(True)
        print("Override AAN — halt genegeerd voor deze week (tot een winst of reset).")
    elif args.cmd == "reset":
        _set_override(False)
        print("Override gewist.")
    else:  # status
        st = compute_state()
        print(json.dumps(st, indent=2, ensure_ascii=False))
        if st["halted"]:
            print(f"\n>>> RISICO-HALT ACTIEF: {'; '.join(st['reasons'])}")
            print(">>> Geen nieuwe orders. Hervat bewust met: "
                  "python3 scripts/risk_guard.py resume")


if __name__ == "__main__":
    main()
