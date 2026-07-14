# XAUUSD — kill zone-run NY, 2026-07-14 13:00 UTC (15:00 NL) — post-CPI

**Data**: Swissquote spot 4079,5/4080,2 (mid 4079,8) · GC=F future 4082,4–4086,4 → spread ~4–6 (niveaus in spot, gekalibreerd op spread ~5,5). Candles 15m (2d) + 1h (5d) vers; 4h van de ochtendrun als HTF-referentie.

## Marktanalyse

**CPI (12:30 UTC) kwam goud-bullish binnen**: spike van ~4030 naar **4107 spot** (future 4112,5) in één 15m-candle, daarna scherpe rejection naar 4071 en consolidatie rond **4080**. De candle sloot mid-range — beide kanten zijn geraakt, klassiek event-sweep.

**Structuur na de spike**:
- **H1: CHoCH omhoog** — de hele 13-jul down-leg (4093 → 3981 spot) is in één beweging geretraced; de korte-termijn bearish structuur is gebroken.
- **H4: bias blijft bearish maar staat onder druk** — lower highs 4394 → 4206 → 4143 intact, máár prijs test nu de OTE van de laatste H4 down-leg. Pas boven 4143 (spot) is de H4-structuur echt om.
- De CPI-spike tagde **exact de 0.786 (4109) en de liquidity boven de 13-jul high** en werd verworpen — een sweep, geen acceptatie. Zolang H1 niet boven 4113 sluit is dit een fade-scenario.

**Fib-cluster multi-leg (spot, incl. 0.65)**:
- H4-leg 4142,9 → 3984,9: 0.618 = 4082,5 · 0.65 = 4087,6 · **0.705 = 4096,3** · **0.786 = 4109,1** · 0.886 = 4124,9
- Grote leg 4210 → 3984,9: **0.5 = 4097,5** · 0.618 = 4124,0
- **Cluster: 4096,3–4097,5** (0.705 H4-leg + 0.5 grote leg), met de CPI-high 4107 en 0.786 op 4109 er vlak boven — entry-zone 4096–4108.

**Momentum (Rule 8)**: H1/15m-momentum staat **UP** (post-CPI impuls) — deze short gaat daar tegenin en is daarom expliciet een fade met lagere conviction; de trigger is de al gemaakte rejection van 4107, niet hoop op een top. Supply/demand-boxen uit de chart-layout (Rule 7) niet beschikbaar in de feed.

## Setup

```
SETUP — XAUUSD 1H short (CPI-fade)

Bias:         Short — H4 bearish (lower highs 4394→4206→4143 intact); CPI-spike = sweep van
              de 13-jul high met rejection op de H4-OTE, geen acceptatie boven 4100
Zone:         4096 – 4108 — OTE-cluster + CPI-high liquidity
Confluences:  0.705 H4-leg (4096,3) + 0.5 grote leg (4097,5) cluster + CPI-high sweep 4107 +
              0.786 op 4109 als deksel + verse supply van de rejection-candle

Entry:        4098
Stop Loss:    4113 — achter 0.786 (4109,1) én boven de CPI-high (4107)
Take Profit 1:4052 — S/R-flip: supply-zone van de 13-jul breakdown wordt eerste target
Take Profit 2:4030 — pre-CPI shelf (top van de ochtend-range)
Take Profit 3:4000 — psych + overnight base (runner)

Risk:Reward:  3,1 (TP1) / 4,5 (TP2)
Invalidatie:  H1-close boven 4113 spot — dan is de rejection gefaald en is 4125–4143 het volgende doel
Conviction:   B — sterk cluster + gemaakte sweep/rejection, maar tegen post-CPI momentum in
              (Rule 8) en event-volatiliteit nog vers
```

Bullish scenario (geen signaal): H1-close boven 4113 → long-bias richting 4125 (0.886/0.618-cluster) en 4143; boven 4143 klapt de H4-bias om — dan wordt ook de swing-short 4133 geïnvalideerd vóór fill.

## Alertniveaus

- **4107** — CPI-high; break + H1-close erboven = fade dood
- **4096** — zone-touch (entry actief)
- **4052** — TP1 / S-R flip
- **4030** — pre-CPI shelf; verlies heropent 4000
- **4143** — H4-omslagpunt (invalidatie swing-short)

## Orders & posities

| Item | Status |
|---|---|
| CPI-fade-short 4098 (B, nieuw) | `active`; executor dry-run: SHORT LIMIT 4098 / SL 4113 / TP 4052 — geldig t/m 20:00 UTC |
| Swing-short 4133 (B) | `active` t/m 17-07; door de CPI-spike weer relevant — invalidatie (H1-close > 4143) nog niet geraakt |
| Pullback-short 4052 (ochtendrun) | `expired` om 12:00 UTC — precies volgens plan vóór CPI geannuleerd; de spike blies er dwars doorheen, de tijds-vangrail voorkwam een fill in de squeeze |
| Fade-short 4026 (13-07) | blijft `rejected` (RR-vangrail) |
| Open posities | geen |

**Executie**: dry-run (CTRADER_*-credentials nog niet ingesteld). Run gelogd in `signals/execution_log.jsonl`.
