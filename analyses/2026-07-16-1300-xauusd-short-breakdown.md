# XAUUSD — kill zone-run NY, 2026-07-16 13:00 UTC (15:00 NL) — post-databreakdown

**Data**: Swissquote spot 3986,7/3987,4 (mid 3987,0) · GC=F future 4000,8 → spread ~13,8 (niveaus in spot). Candles 15m (2d) vers.

## Marktanalyse

Het 12:30 UTC-datavenster bracht ditmaal een **dump**: van ~4035 naar **3980,4 spot** (future low 3994,2) in 45 minuten. Daarmee is de meerdaagse range-onderkant (4016/4004) **gebroken** en is de **juli-low 3981 getest/marginaal geveegd**. Prijs veert licht op naar 3987.

- **D1-bias bearish** (momentum <100, onder dalende 50-MA) en nu ook een verse intraday BOS omlaag — HTF en LTF wijzen dezelfde kant op.
- **Rule 12 werkte exact zoals bedoeld**: de flip-short 4052 is om 12:00 UTC geëxpireerd (nooit gevuld — ochtend-high was ~4038 spot) en er stond géén order in het venster toen de dump kwam.
- Boven ons: **4004** (gebroken base = eerste flip), **4014–4019** (oude demand → supply + 0.618/0.65-cluster), **4029** (0.886). Onder ons: **3981/3980** (juli-low, nu decision point), **3962**, en D1-ruimte richting **3910/3812**.

**Fib (multi-leg incl. 0.65) op de verse down-leg 4034,9 → 3980,4 (spot)**:
0.618 = **4014,1** · 0.65 = **4015,8** · 0.705 = 4018,8 · 0.786 = 4023,2 · 0.886 = 4028,7
Cluster **4014–4019** = exact de oude demand-zone die nu supply wordt.

**Momentum (Rule 8)**: 15m veert op van de low (UP) — levert de retracement; entry mét de D1-bias. NY kill zone actief ✓. Datavenster: de release is geweest; de zone ligt ~30 pt boven de markt, fill-kans vóór 14:00 UTC is klein.

## Setup

```
SETUP — XAUUSD 1H short (breakdown-retest)

Bias:         Short — D1 bearish + verse BOS door de range-onderkant (4016/4004)
              richting de juli-low; alle timeframes aligned
Zone:         4014 – 4020 — oude demand 4016-4019 wordt supply + 0.618/0.65-cluster
Confluences:  0.618 = 4014,1 · 0.65 = 4015,8 op de leg 4034,9→3980,4 + S/R-flip van
              de gebroken range-onderkant + 4004-flip als extra deksel eronder +
              NY kill zone; 15m-momentum UP levert de entry

Entry:        4016
Stop Loss:    4030 — achter 0.886 (4028,7) én boven de 4029-schouder
Take Profit 1:3981 — juli-low (eerste liquidity)
Take Profit 2:3962 — extensie onder de low
Take Profit 3:3910 — D1-niveau (runner)

Risk:Reward:  2,5 (TP1) / 3,9 (TP2)
Invalidatie:  H1-close boven 4030 — dan was de breakdown een sweep en is de
              dubbele bodem 3981 het frame (long-scenario activeert)
Conviction:   B — volledige HTF-alignment + kill zone + sterk cluster; geen A
              vanwege de dubbele bodem 3981 direct onder de markt (squeeze-risico)
              en verse post-data volatiliteit
```

**Long-scenario (alleen mét bevestiging, Rule 13)**: 15m bullish CHoCH op de 3980–3985-zone → dubbele-bodem-long richting 4004/4016. Wordt pas een signaal als de bevestiging er staat.

## Alertniveaus

- **4004** — eerste flip; acceptatie erboven verzwakt het short-scenario
- **4016** — zone-touch (entry actief)
- **4030** — H1-close erboven = setup dood, dubbele bodem-frame
- **3980** — juli-low; H1-close eronder = D1-territorium open (3962/3910)

## Orders & posities

| Item | Status |
|---|---|
| Breakdown-short 4016 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: SHORT LIMIT 4016 / SL 4030 / TP 3981 |
| Flip-short 4052 | `expired` om 12:00 UTC — nooit gevuld (ochtend-high ~4038); Rule 12 hield het venster schoon, precies zoals bedoeld |
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC — 145 pt boven markt, alleen relevant bij een monsterrally; blijft staan met de cancel-discipline |
| Open posities | geen |

**Executie**: dry-run (geen CTRADER-credentials). Run gelogd in `signals/execution_log.jsonl`. WhatsApp verstuurd (B-setup).
