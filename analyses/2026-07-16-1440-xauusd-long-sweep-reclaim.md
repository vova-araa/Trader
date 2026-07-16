# XAUUSD — on-demand analyse (screenshot D1), 2026-07-16 14:40 UTC (16:40 NL)

**Bron**: screenshot broker-app D1 + verse GC=F 15m. Broker 4001,20/4001,77 · future 4002,8 — de future-spread is ingeklapt naar ~1,5 (was vanmiddag nog ~14 vs Swissquote); niveaus hieronder in broker-prijzen. D1-indicatoren: Momentum(14) 98,17 · RSI(7) 36,9.

## Marktanalyse

**De dump kreeg een staart**: na de 13:00-低 maakte de markt een **sweep van de juli-low** (future 3977,1 ≈ broker ~3975,5 — onder de dubbelbodem) en werd die **direct gereclaimd**: higher low 3984 (13:30), tweede push naar **4011** (14:00) = **15m bullish CHoCH bevestigd**. Prijs nu 4001, net onder de 4004-flip.

**Daily-plaatje (screenshot)**: vandaag vormt zich een candle met een lange onderwiek exact op de juli-dubbelbodem — bij een close rond/boven 4000 (21:00 UTC, over ~6u) is dat een hammer op support: het sterkste omkeersignaal dat de daily deze maand heeft laten zien. D1-momentum (98,2) en RSI (36,9) blijven bearish — de long hieronder is dus expliciet counter-D1, maar mét de vereiste intraday-bevestiging (Rule 13 voldaan: sweep + reclaim + CHoCH).

**Frame**: rotatie 3975–4030. Boven: 4004 (flip), **4014–4020** (supply, onze short-zone), 4030 (0.886-schouder), 4052. Onder: 3984 (higher low), **3975,5 (sweep-low — de lijn in het zand)**, daaronder 3962/3910.

**Fib OTE op de reclaim-leg 3975,5 → 4011,0 (broker)**:
0.618 = 3989,1 · 0.65 = 3987,9 · 0.705 = 3986,0 · 0.786 = 3983,1 · 0.886 = 3979,5

## Setup

```
SETUP — XAUUSD 15m long (sweep & reclaim van de juli-low)

Bias:         Long intraday — liquidity grab onder de dubbelbodem + reclaim +
              15m-CHoCH (higher low 3984, break van 4009); counter-D1
              (momentum 98,2) dus bevestiging was verplicht en die staat
Zone:         3983 – 3990 — OTE van de reclaim-leg (0.618–0.786) + higher-low-zone
Confluences:  sweep-low als gedefinieerd invalidatiepunt + OTE-cluster (0.705 =
              3986,0 · 0.65 = 3987,9) + dubbelbodem-daily-wick + potentiële
              D1-hammer bij close ≥ 4000; 15m-momentum UP, D1-momentum DOWN
              (Rule 8: expliciet benoemd — daarom B en geen A)

Entry:        3984 (limit in de 0.786-zone)
Stop Loss:    3972 — onder de sweep-low (3975,5): daar is de these aantoonbaar dood
Take Profit 1:4013 — net onder de 4014-4020 supply (eerste liquidity)
Take Profit 2:4030 — 0.886-schouder van de down-leg
Take Profit 3:4052 — de oude flip (runner, alleen bij daily-hammer-bevestiging)

Risk:Reward:  2,4 (TP1) / 3,8 (TP2)
Invalidatie:  15m-close onder 3975 — sweep-low terugverloren = reclaim gefaald
Conviction:   B — trigger + confluence compleet, maar counter-D1 en het is dag 1
              van een mogelijke bodem
```

**Rotatie-bracket**: de breakdown-short 4016 blijft actief — long-TP1 (4013) ligt bewust nét onder de short-entry. Speelboek: reclaim runt naar de supply → long eruit op 4013 → faalt de supply, dan neemt de short 4016 het over richting 3981. Eén van de twee wint de rotatie; de sweep-low en 4030 zijn de harde randen.

**Daily close 21:00 UTC als beslispunt**: close ≥ 4000 = hammer op dubbelbodem → morgen long-bias boven 3984; close < 3990 = zwakke bounce → short-scenario's prevaleren weer.

## Alertniveaus

- **3990** — onderkant OTE (entry-gebied nadert)
- **3975** — 15m-close eronder = long dood, D1-continuation
- **4013/4016** — supply-test: long eruit, short-decision
- **4030** — H1-close erboven = ook de short dood, frame draait volledig

## Orders & posities

| Item | Status |
|---|---|
| Sweep-long 3984 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: LONG LIMIT 3984 / SL 3972 / TP 4013 |
| Breakdown-short 4016 (B) | `active` t/m 20:00 UTC — rotatie-bracket met de long |
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC |
| Open posities | geen |

**Executie**: dry-run (geen CTRADER-credentials). Run gelogd in `signals/execution_log.jsonl`.
