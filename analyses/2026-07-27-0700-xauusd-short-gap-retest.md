# XAUUSD — kill zone-run London open, 2026-07-27 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4098,0/4098,7 (mid 4098,0) · GC=F future ~4102 → spread ~4 (genormaliseerd). 1h-candles vers. Sunday-open + Monday-structuur.

## Marktanalyse — weekend-gap omhoog

**De markt gapte het weekend +53 omhoog** (vrijdag-close spot ~4045 → Sunday-open ~4091 → nu **4098**). Dit **bevestigt de weekend-flat-discipline**: een short die vrijdag was blijven staan, had 53 punten tegen zich gehad, dwars door elke stop. Precies waarvoor "geen weekend-carry" bestaat.

De gap reclaimde alles boven **4074/4090** en tikte Sunday-night **~4115 (spot; future 4119)** — recht in de **4098–4107 CPI-high resistance**, de zone waar de grote daling van vorige donderdag begon. Daar volgde een rejection terug naar 4098.

- **Intraday: gap-up negeert de bearish breakdown van vorige week** — terug boven 4074, korte termijn neutraal-bullish.
- **D1/weekly: bearish** — 4098–4107 is de resistance die de hele maand capt; 4278 blijft de grote weekly-weerstand. Een short hier is **trend-mee weekly**.

**Fib/structuur**: de gap-up in een bearish weekly context heeft een **gap-fill-neiging** richting de vrijdag-close (4045). De resistance 4098–4115 (CPI-high + Sunday-high) is de logische short-zone.

**Momentum (Rule 8)**: gap-momentum kort UP, maar Sunday-high (4115) al gerejecteerd. De short verkoopt de retest van de resistance, mét de weekly-trend.

## Setup — ACTIEF in de pipeline (trend-mee, gap-retest short)

```
SETUP — XAUUSD 1H short (gap-retest van de CPI-high resistance)

Bias:         Short — weekly bearish; gap-up loopt in de 4098-4107 resistance
              (maand-deksel) + Sunday-rejection op 4115; gap-fill-neiging naar 4045
Zone:         4100 – 4110 — CPI-high 4107 + Sunday-consolidatie
Confluences:  CPI-high resistance (capt de hele maand) + Sunday-high-rejection 4115 +
              weekly-downtrend + gap-fill-tendens richting vrijdag-close 4045

Entry:        4105 (sell limit — retest van de resistance)
Stop Loss:    4118 — boven de Sunday-high (4115) en CPI-high
Take Profit 1:4074 — gap-origin / gebroken flip (eerste liquidity)
Take Profit 2:4052 — weekpivot
Take Profit 3:4045 — vrijdag-close / volledige gap-fill (runner)

Risk:Reward:  2,4 (TP1) / 4,1 (TP2)
Invalidatie:  H1-close boven 4118 — dan loopt de gap door richting 4140/4171;
              expiry 20:00 UTC (geen carry)
Conviction:   B — trend-mee weekly + clean resistance + gap-fill-logica. Geen A
              omdat gap-up-momentum vers is en Monday-gaps soms doorlopen
```

**Continuation-long (counter-weekly, alleen mét bevestiging)**: H1-close boven 4118 → gap loopt door, 15m bullish CHoCH → long richting 4140. Advies, geen order (Rule 13).

## Alertniveaus

- **4105 / 4107** — resistance / short-entry-zone
- **4118** — H1-close erboven = short dood, gap loopt door naar 4140
- **4074** — TP1 / gap-origin; break = 4052/4045 open
- **4045** — volledige gap-fill / vrijdag-close (TP3)

## Orders & posities

| Item | Status |
|---|---|
| Gap-retest-short 4105 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: SHORT LIMIT 4105 / SL 4118 / TP 4074 |
| Breakdown-retest-short 4058 | `expired` (vrijdag, Rule 12) |
| Open posities gebruiker | geen bekend |
| Dry-run scorebord | +0,8R over 8 trades (2 weken); discipline intact |

**Executie**: dry-run (credentials/netwerk niet ingesteld; cTrader-app wacht op KYC). Run gelogd. WhatsApp verstuurd (actieve B-setup + weekend-gap-context).
