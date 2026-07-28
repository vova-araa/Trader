#!/usr/bin/env python3
"""Backtest-analyse van alle dry-run trades t/m nu.

Leest het trade-grootboek (hieronder, afgeleid uit signals/active_setups.json
+ de analyse-logs), berekent edge-statistiek en breekt de resultaten uit naar
richting / trend-alignment / verliesoorzaak, zodat we zien wat beter kan.

Draaien: python3 scripts/backtest.py
"""

# Grootboek: alleen GEVULDE trades (expired/rejected orders = geen fill, geen R).
# R = resultaat in risk-multiples. trend = 'mee' (met HTF/weekly) of 'tegen'.
LEDGER = [
    # id                         dir     R     trend    setup            oorzaak/notitie
    ("14-07 ote-long-4046",     "long", -1.0, "tegen", "OTE-limit",     "blinde counter-HTF limit; flip-trigger ging pas na fill af"),
    ("15-07 retest-short-4048", "short",-1.0, "mee",   "flip-retest",   "news-spike 12:45 door datavenster (geen event-check)"),
    ("16-07 breakdown-short-4016","short",2.5,"mee",   "breakdown-retest","TP1; bracket-winnaar"),
    ("16-07 sweep-long-3984",   "long", -1.0, "tegen", "sweep-reclaim", "reclaim juli-low faalde, acceptatie eronder"),
    ("17-07 lowflip-short-4000","short", 2.3, "mee",   "flip-retest",   "TP1 in de datadump"),
    ("17-07 fridayflip-3984",   "short",-1.0, "mee",   "flip-retest",   "vrijdagmiddag short-covering-squeeze (V-reversal)"),
    ("20-07 supply-short-4030", "short", 0.0, "mee",   "supply-retest", "BE-stop redde +24 van de reversal = 0R"),
    ("27-07 gap-retest-4105",   "short", 2.4, "mee",   "gap-retest",    "TP1; gap-fill trend-mee"),
]


def stats(rows):
    n = len(rows)
    if not n:
        return None
    rs = [r for _, r in rows]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r < 0]
    be = [r for r in rs if r == 0]
    total = sum(rs)
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    return {
        "n": n, "wins": len(wins), "losses": len(losses), "be": len(be),
        "total_R": total,
        "winrate": len(wins) / n * 100,
        "winrate_ex_be": (len(wins) / (n - len(be)) * 100) if n - len(be) else 0,
        "avg_win": (gross_win / len(wins)) if wins else 0,
        "avg_loss": (-gross_loss / len(losses)) if losses else 0,
        "expectancy": total / n,
        "profit_factor": (gross_win / gross_loss) if gross_loss else float("inf"),
    }


def show(title, rows):
    s = stats(rows)
    if not s:
        print(f"\n{title}: (geen trades)")
        return
    pf = "∞" if s["profit_factor"] == float("inf") else f"{s['profit_factor']:.2f}"
    print(f"\n=== {title} ===")
    print(f"  Trades: {s['n']}  ({s['wins']}W / {s['losses']}L / {s['be']}BE)")
    print(f"  Totaal: {s['total_R']:+.1f}R   Expectancy: {s['expectancy']:+.2f}R/trade")
    print(f"  Winrate: {s['winrate']:.0f}% ({s['winrate_ex_be']:.0f}% ex-BE)")
    print(f"  Gem. winnaar: {s['avg_win']:+.2f}R   Gem. verliezer: {s['avg_loss']:+.2f}R")
    print(f"  Profit factor: {pf}")


rows_all = [(x[0], x[2]) for x in LEDGER]
rows_long = [(x[0], x[2]) for x in LEDGER if x[1] == "long"]
rows_short = [(x[0], x[2]) for x in LEDGER if x[1] == "short"]
rows_mee = [(x[0], x[2]) for x in LEDGER if x[3] == "mee"]
rows_tegen = [(x[0], x[2]) for x in LEDGER if x[3] == "tegen"]

print("BACKTEST — XAUUSD dry-run (2 weken)")
show("ALLE GEVULDE TRADES", rows_all)
show("LONGS (counter-trend)", rows_long)
show("SHORTS (trend-mee)", rows_short)
show("TREND-MEE (met weekly/HTF)", rows_mee)
show("COUNTER-TREND (tegen HTF)", rows_tegen)

print("\n=== VERLIEZERS — oorzaak-analyse ===")
for name, d, r, t, setup, note in LEDGER:
    if r < 0:
        print(f"  {name:26} ({t:5}) {r:+.0f}R — {note}")

print("\n=== WAT-ALS: counter-trend longs overgeslagen ===")
s_no_long = stats(rows_short)
print(f"  Zonder de 2 counter-trend longs: {s_no_long['total_R']:+.1f}R over "
      f"{s_no_long['n']} shorts ({s_no_long['wins']}W/{s_no_long['losses']}L/"
      f"{s_no_long['be']}BE), expectancy {s_no_long['expectancy']:+.2f}R/trade")
print(f"  vs werkelijk {stats(rows_all)['total_R']:+.1f}R met alles erin.")
