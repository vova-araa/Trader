# XAUUSD — kill zone-run London open, 2026-07-14 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4022,8/4023,4 (mid 4023,1) · GC=F future 4032,4 → spread ~9,3 (alle niveaus hieronder in spot). Candles 15m/1h/4h via Yahoo GC=F.

## Marktanalyse

**H4 (bias)**: bearish. Lower highs 4394 → 4206 → 4139 (spot); op 13 juli verse impuls omlaag van 4093 naar **3981** — een duidelijke BOS onder de juli-lows. Het overnight herstel (3981 → 4031) is tot nu toe corrective: drie golven, afnemend momentum tegen de vorige S/R-flip.

**H1/15m (structuur)**: de sell-off-leg 4080 → 3981 is de actieve leg. Overnight base 3991–4000 (psych 4000 hield als support), herstel-high 4031, prijs nu 4023 — net onder de 0.382 van de leg. Boven ons ligt de breakdown-zone: de pre-drop consolidatie 4052–4062 is nu supply, met daarboven de origin van de laatste impuls rond 4070–4080.

**Fib-cluster (multi-leg, incl. 0.65)** op de down-legs (spot):
- Grote leg 4092,9 → 3981,1: 0.618 = 4050,2 · 0.65 = 4053,8 · 0.705 = 4059,9 · 0.786 = 4068,9
- Kleine leg 4079,8 → 3981,1: 0.618 = 4042,1 · 0.65 = 4045,3 · 0.705 = 4050,7 · 0.786 = 4058,7 · 0.886 = 4068,6
- **Cluster 1: 4050,2–4050,7** (0.618 groot + 0.705 klein) — sweet spot
- **Cluster 2: 4058,7–4059,9** (0.786 klein + 0.705 groot) — bovenkant zone

**Momentum (Learned Rule 8)**: 15m-momentum staat UP (herstel-leg) — dat is de motor die de retracement naar de short-zone moet brengen; de entry zelf is mét de H4-richting. Geen oscillator-data in de feed; beoordeeld op candle-structuur. Supply/demand-boxen uit de chart-layout (Rule 7) niet beschikbaar in deze datafeed.

**Event-risico**: **CPI vandaag 12:30 UTC (14:30 NL)** — alle pending orders gaan er om 12:00 UTC uit (zelfde speelboek als gisteren).

## Setup

```
SETUP — XAUUSD 1H short (pullback)

Bias:         Short — H4 bearish (lower highs 4394→4206→4139, verse BOS naar 3981); herstel is corrective
Zone:         4050 – 4060 — OTE-cluster + supply van de 13-jul breakdown (pre-drop consolidatie 4052–4062)
Confluences:  fib-cluster multi-leg (0.618 groot 4050,2 + 0.705 klein 4050,7; 0.786 klein 4058,7 + 0.705 groot 4059,9) + supply/OB breakdown-zone + psych 4050 + 15m-momentum UP levert de retracement aan

Entry:        4052
Stop Loss:    4070 — achter 0.886 (4068,6) én boven de supply-top
Take Profit 1:4005 — overnight base + psych 4000 (eerste liquidity)
Take Profit 2:3982 — sessie-low / sweep-target
Take Profit 3:3962 — runner, extensie onder de low

Risk:Reward:  2,6 (TP1) / 3,9 (TP2)
Invalidatie:  H1-close boven 4070 spot; hard cancel 12:00 UTC (CPI 12:30 UTC)
Conviction:   B — HTF-aligned met sterk fib-cluster, maar vereist diepe retracement en het CPI-window beperkt de geldigheid
```

Alternatief scenario (geen signaal, alleen alert): directe continuation vanaf huidige prijs (4023) bij 15m-CHoCH omlaag richting 4000 haalt maar ~RR 2,1 vanaf een mid-range entry zonder OTE — C, niet geforceerd (Rule 4). Bullish scenario: H1-close boven 4031 opent 4042–4050 (speelt de short-zone juist aan); pas boven 4070 is het herstel structureel en is de short-bias voor vandaag dood.

## Alertniveaus

- **4031** — overnight high; break = retracement-extensie richting de zone
- **4050** — zone-touch (entry-gebied actief)
- **4000** — psych + base; verlies = directe continuation omlaag
- **3981** — low; break = volgende markdown-leg

## Orders & posities

| Item | Status |
|---|---|
| Pullback-short 4052 (B, nieuw) | `active` in signaalbestand; executor dry-run: SHORT LIMIT 4052 / SL 4070 / TP 4005 — cancel 12:00 UTC |
| Swing-short 4133 (B) | `active`, geldig t/m 17-07 20:00 UTC; ver boven markt, blijft staan |
| Fade-short 4026 (13-07) | `rejected` door RR-vangrail (1,91 < 2,0) — geen order geweest; NB: had gisteren tijdens het herstel wél gevuld, vangrail deed zijn werk |
| Open posities | geen (long 13-07 eerder gesloten op -1R) |

**Executie**: dry-run (CTRADER_*-credentials nog niet ingesteld door gebruiker). Run gelogd in `signals/execution_log.jsonl`.
