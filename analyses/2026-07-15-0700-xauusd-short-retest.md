# XAUUSD — kill zone-run London open, 2026-07-15 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4030,0/4030,6 (mid 4030,3) · GC=F future 4036,4 → spread ~6,1 (niveaus in spot). Candles 15m (2d) vers; 1h/4h-structuur uit de runs van gisteren als HTF-kader.

## Marktanalyse

De hele CPI-spike is teruggegeven. Na de rejection op 4107 maakte de markt de hele avond lower highs (4102 → 4062 → 4048 → 4042) en overnight is de **flip-trigger van gisteravond (15m-close onder 4040) geraakt**: doorzak naar **4021 spot** (future 4027,1), gevolgd door een matte bounce naar 4030. De H1 bullish CHoCH van na CPI is daarmee dood; **H4-bias bearish is volledig terug in controle** — de markt handelt weer ónder het pre-CPI niveau.

**Structuur**: boven ons de S/R-flip **4040–4042** (overnight bounce-high + de gebroken shelf) en daarboven de supply 4052–4062. Onder ons: **4021** (overnight low), **4004** (base van 14-07) en **3981** (13-jul low). Klassiek bearish patroon: verkopers verdedigen elke retracement lager.

**Fib (multi-leg, incl. 0.65) op de verse down-leg 4062,5 → 4021,0 (spot)**:
0.618 = **4046,6** · 0.65 = **4048,0** · 0.705 = 4050,3 · 0.786 = 4053,6 · 0.886 = 4057,8
De 0.618/0.65 clusteren met de S/R-flip 4040-4042→4048-zone en de onderkant van de 4052-supply — retest-short-zone **4046–4052**.

**Momentum (Rule 8)**: 15m-momentum staat UP (bounce van 4021) — die levert de retracement richting de zone; de entry is mét de H4-richting. London kill zone actief ✓.

## Setup

```
SETUP — XAUUSD 15m short (retest van de flip)

Bias:         Short — H4 bearish weer in controle: CPI-spike volledig unwound,
              flip-trigger 4040 gespeeld, lower highs sinds 4107
Zone:         4046 – 4052 — S/R-flip + 0.618/0.65-cluster + onderkant 4052-supply
Confluences:  0.618 (4046,6) + 0.65 (4048,0) op de verse leg + gebroken shelf
              4040-4042 als flip + supply 4052-4062 erboven + kill zone-timing;
              15m-momentum UP levert de entry aan

Entry:        4048
Stop Loss:    4058 — achter 0.886 (4057,8) én boven de flip-zone
Take Profit 1:4021 — overnight low (eerste liquidity)
Take Profit 2:4004 — base 14-07
Take Profit 3:3981 — 13-jul low (runner)

Risk:Reward:  2,7 (TP1) / 4,4 (TP2)
Invalidatie:  H1-close boven 4058 spot — dan is de flip-retest gefaald en is
              4080/4100 weer in beeld
Conviction:   B — HTF-aligned, kill zone, net cluster; geen A omdat de zone al
              één keer als support is gebruikt (4048-bounce overnight)
```

## Journal (sectie 7) — dry-run resultaten t/m nu

```
14-07 XAUUSD Short 4052 | 4052 / 4070 / 4005 | n.v.t. (expired 12:00 pre-CPI) | tijds-vangrail voorkwam CPI-squeeze-stopout
14-07 XAUUSD Short 4098 | 4098 / 4113 / 4052 | n.v.t. (expired, nooit gevuld) | fade-zone was goed, markt kwam er net niet
14-07 XAUUSD Long  4046 | 4046 / 4036 / 4080 | -1R (dry-run) | counter-HTF long niet blind als limit in OTE — wacht op 15m-CHoCH-bevestiging
```

## Alertniveaus

- **4048** — zone-touch (entry actief)
- **4058** — H1-close erboven = setup dood
- **4021** — TP1 / overnight low; break = weg naar 4004 open
- **4004** — base; daaronder 3981

## Orders & posities

| Item | Status |
|---|---|
| Retest-short 4048 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: SHORT LIMIT 4048 / SL 4058 / TP 4021 |
| Swing-short 4133 (B) | `active` t/m 17-07; ver boven markt, cancel-discipline blijft H1-close > 4143 |
| OTE-long 4046 (14-07) | `stopped` — dry-run -1R, les gelogd |
| CPI-fade-short 4098 | `expired` (nooit gevuld) |
| Open positie gebruiker | BUY 0.2 @ 4004,33 — als SL naar 4038-4040 is opgetrokken (advies gisteravond): overnight uitgestopt op ~+$680-700; zo niet, dan nu ~+$500 en is 4021 het niveau dat móét houden |

**Executie**: dry-run (CTRADER_*-credentials nog niet ingesteld). Run gelogd in `signals/execution_log.jsonl`.
