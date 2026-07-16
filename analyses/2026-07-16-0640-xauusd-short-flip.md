# XAUUSD — on-demand analyse (screenshots H4 + D1), 2026-07-16 06:40 UTC (08:38 NL)

**Bron**: screenshots broker-app (H4 + D1) + verse GC=F candles via Zapier. Broker-spot 4023,98/4024,66 · future 4034,7 → spread ~10,7 (niveaus in broker-spot). Indicatoren gebruiker: H4 Momentum(14) 100,49 / RSI(7) 41,3; **D1 Momentum(14) 98,72 / RSI(7) 39,6**.

## Marktanalyse

**D1 (macro, nieuw in beeld)**: de daily is onmiskenbaar bearish — top 5450 (dec '25), lower highs sindsdien, prijs onder de dalende 50-MA (~4200) en het daily momentum onder 100. De juli-lows rond 3980 zijn de laatste verdediging vóór 3812.

**Overnight**: vierde rejection van de **4070-deksel** (~01:00 UTC), daarna brak de triangle-base 4028: doorzak naar **4018,7**, bounce naar **4041** — precies de flip-retest van onderaf — en daar direct weer verkocht. De user-long 4028,4 is op de opgetrokken SL 4024,6 uitgestopt: **-$77** na een piek van +$577. Zuur, maar dit is exact waarvoor de SL-lock dient.

**Frame**: meerdaagse compressie 4004/4016 – 4070, maar mét bearish D1, vier gefaalde pogingen op de deksel en een gebroken intraday-base. De weg van de minste weerstand voor vandaag is naar de onderkant van de range.

**Fib (multi-leg incl. 0.65) op de verse down-leg 4070,0 → 4018,7 (broker-spot)**:
0.618 = **4050,4** · 0.65 = **4052,0** · 0.705 = 4054,9 · 0.786 = 4059,0 · 0.886 = 4064,1
Het 0.618/0.65-cluster valt exact samen met de **4052-flip** (de zone die al drie dagen elke kant-wissel markeert) en de onderkant van de supply.

**Momentum (Rule 8)**: 15m veert op vanaf 4019 (UP) — levert de retracement naar de zone; de entry is mét de D1-bias. London kill zone actief ✓. **Event-check (Rule 12)**: 12:30 UTC US-datavenster (donderdag = o.a. jobless claims) → order hard eruit om 12:00 UTC.

## Setup

```
SETUP — XAUUSD 1H short (flip-retest na base-break)

Bias:         Short — D1 bearish (momentum 98,7, onder dalende 50-MA), 4× rejection
              van de 4070-deksel, intraday base 4028 gebroken
Zone:         4050 – 4059 — 0.618/0.65-cluster + de 4052-flip + supply-onderkant
Confluences:  fib-cluster (0.618 = 4050,4 · 0.65 = 4052,0) + flip-zone 4052 die al
              drie dagen de kantelzone is + 4041-rejection van vanochtend als eerste
              bevestiging + D1-bias + London kill zone; 15m-momentum UP levert de entry

Entry:        4052
Stop Loss:    4066 — achter 0.886 (4064,1) én boven de laatste supply-schouder
Take Profit 1:4019 — overnight low (eerste liquidity)
Take Profit 2:4004 — range-onderkant / 14-jul base
Take Profit 3:3981 — juli-low (runner; daaronder is D1-ruimte naar 3910)

Risk:Reward:  2,4 (TP1) / 3,4 (TP2)
Invalidatie:  H1-close boven 4066 — dan is de vijfde poging op 4070 kansrijk en
              flipt het speelboek; hard cancel 12:00 UTC (Rule 12, US-data 12:30)
Conviction:   B — HTF-aligned + kill zone + sterk cluster; geen A omdat de
              range-onderkant al 3× is verdedigd (mean-reversion-risico)
```

**Long-scenario (alleen mét bevestiging, Rule 13)**: 15m bullish CHoCH op **4016–4019** of **4004** → long terug de range in richting 4041/4052. Geen blinde limit.

## Alertniveaus

- **4052** — zone-touch (entry actief)
- **4066** — H1-close erboven = setup dood
- **4019** — TP1; break = 4004 open
- **4004** — range-onderkant; verlies = 3981 en dan D1-territorium

## Orders & posities

| Item | Status |
|---|---|
| Flip-short 4052 (B, nieuw) | `active` t/m 12:00 UTC (Rule 12); executor dry-run: SHORT LIMIT 4052 / SL 4066 / TP 4019 |
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC; op de screenshots geen orderlijnen meer zichtbaar — als je de sell limit op de broker hebt weggehaald: het pipeline-signaal staat er nog, laat weten als hij ook daar weg moet |
| User-long 4028,4 | gesloten op SL 4024,6 = **-$77** (na +$577 piek); de SL-lock deed zijn werk — verlies beperkt tot ~0,2R van de oorspronkelijke winst |
| Breakout-playbook 4072 (vannacht) | vervallen — de trigger (M30-close > 4072) is er nooit gekomen; vierde rejection bevestigde de deksel |

**Executie**: dry-run (geen CTRADER-credentials). Run gelogd in `signals/execution_log.jsonl`.
