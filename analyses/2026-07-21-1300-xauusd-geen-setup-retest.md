# XAUUSD — kill zone-run NY, 2026-07-21 13:00 UTC (15:00 NL)

**Data**: Swissquote spot 4057,3/4058,0 (mid 4057,3) · GC=F future 4063,1 → spread ~6. Candles 15m vers. Dagrange future 4048–4088.

## Marktanalyse

**De break-retest is in uitvoering — nog geen bevestiging.** Na de overnight-breakout naar 4081 (spot) consolideerde de prijs 4055–4081 en zakt nu terug richting de gebroken range-top **4052**. Spot 4057, precies bovenop de flip. De 15m maakt sinds de top een reeks **lower highs** (4088 → 4079 → 4074 → 4067 → 4063) — een gecontroleerde pullback, maar **nog geen bullish CHoCH**: er is nog geen higher low + break omhoog die de long bevestigt.

- **H1**: bullish structuur intact zolang 4046–4052 houdt; verlies daarvan = mislukte breakout.
- **H4/D1**: nog bearish hoofdstructuur — de long blijft counter-D1, dus bevestiging verplicht (Rule 13).

**Fib (rally-leg 4006 → 4081, incl. 0.65)**: 0.382 = 4052,3 · 0.5 = 4043,5 · 0.618 = 4034,6. De retest-zone **4043–4052** is dus fib + gebroken range-top ineen. Prijs test nu de bovenkant ervan.

**Momentum (Rule 8)**: 15m licht DOWN (de pullback), H1 nog UP. De trade is de *reactie* van de zone, niet de pullback zelf — vandaar wachten.

## Setup — advies met trigger (nog niet actief; Rule 13)

```
SETUP — XAUUSD 15m long (break-retest range-top) — WACHT op trigger

Zone:         4043 – 4056 — gebroken range-top 4052 + 0.382/0.5 fib
TRIGGER:      hold van de zone + 15m bullish CHoCH (15m-close terug boven ~4067
              ná een higher low in de zone). Nu NIET vervuld — prijs drift nog omlaag
Entry:        4054 (op/na de trigger)
Stop Loss:    4038 — onder 0.618 (4034,6) én terug in de oude range = breakout gefaald
Take Profit 1:4081 — overnight-high | TP2 4107 — CPI-high | TP3 4125 (runner)
Risk:Reward:  1,7 (TP1) / 3,1 (TP2)
Invalidatie:  15m-close onder 4044 = retest gefaald → short-scenario
Conviction:   B (na trigger) — clean break-retest, counter-D1 dus bevestiging verplicht
```

**Omkeer-scenario (short, wordt actief bij falen)**: 15m-close onder **4044** → mislukte breakout, terug de range in → short richting **4020 / 4006** (SL boven 4056). Dat is dan trend-mee (D1) en de betere trade — ik werk 'm uit zodra de zone breekt.

## Waarom (nog) geen order

Prijs staat ín de beslissingszone maar heeft geen kant gekozen: geen bullish CHoCH (long-trigger) én nog geen close onder 4044 (short-trigger). Een order plaatsen is nu gokken welke kant de zone kiest — precies wat Rule 13 (geen blinde counter-limit) en Rule 4 (niet forceren) verbieden. De volgende paar 15m-closes beslissen.

## Alertniveaus

- **4067** — 15m-close erboven ná higher low = long-trigger
- **4052** — de flip zelf (bovenkant zone)
- **4044** — 15m-close eronder = breakout gefaald → short-scenario
- **4081** — overnight-high / long-TP1; **4107** — CPI-high daarboven

## Orders & posities

| Item | Status |
|---|---|
| Supply-short 4030 | `closed_be` — 0R (gisteren) |
| Actieve pending orders | geen — beide scenario's trigger-conditioneel |
| Open posities gebruiker | geen bekend |
| Dry-run scorebord | +0,8R over 7 trades; discipline intact |

**Executie**: dry-run (credentials/netwerk niet ingesteld; cTrader-app wacht op KYC). Run gelogd. **Geen WhatsApp** (geen actieve A/B-order — wachten op de trigger).
