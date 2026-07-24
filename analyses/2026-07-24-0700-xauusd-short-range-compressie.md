# XAUUSD — kill zone-run London open, 2026-07-24 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4046,0/4046,7 (mid 4046,0) · GC=F future ~4040 → **spread geconvergeerd (roll bijna voltooid, future ≈ spot); spot blijft de anker**. 1h-candles vers. Overnight-range 4024–4054.

## Marktanalyse

**De breakdown stalde in een tight range onder de flip.** Na de reversal van donderdag consolideerde de prijs de hele nacht in **4024–4054** — geen doorbraak naar 4006, maar ook geen herovering van 4052. De bounce-highs bleven op **~4054 (spot)**, exact onder de short-entry 4058 (net als gisteren: de zone verkoopt, maar 4058 werd niet geraakt). Overnight-low ~4024.

- **Intraday/H1: bearish/neutraal** — lower highs onder 4052, maar de down-follow-through stokt; compressie.
- **D1/weekly: bearish** — trend-mee intact; weekrange 3963–4052, prijs onderin de bovenste helft.

**Fib (drop-leg 4107 → 4024, incl. 0.65)**: 0.382 = 4055,7 · 0.5 = 4065,5 · 0.65 = 4078. De bounce naar 4054 bleef **onder de 0.382** = zwakke correctie, bearish. De short-zone 4054–4058 = range-top + 0.382.

**Momentum (Rule 8)**: 15m/H1 vlak in de range. **Event (Rule 12): vrijdag 12:30 UTC US-data** — de pending short expireert om **12:00 UTC** vóór het venster; **geen weekend-carry**.

## Setup — ACTIEF, pending (range-top short; expireert vóór data)

```
SETUP — XAUUSD 1H short (breakdown-retest / range-top) — PENDING

Entry:        4058 (sell limit — nu effectief range-top; bounces stokken ~4054)
Stop Loss:    4074 — boven 0.5-retr
Take Profit 1:4006 | TP2 3980 | TP3 3963
Risk:Reward:  3,3 (TP1) / 4,7 (TP2) | Conviction B
Geldig t/m:   vandaag 12:00 UTC (Rule 12, vóór US-data) — GEEN weekend-carry
Invalidatie:  H1-close boven 4074 → terug naar 4090
```

**Twee wegen naar het target**: (a) bounce naar 4054–4058 → order vult, short op de range-top; (b) **H1-close onder 4024** → range-breakdown, 4006 direct open — dan mist de order de fill maar speelt het bearish scenario zich af (geen chase, Rule 4). Compressie onder een flip lost meestal naar beneden op, dus (b) is goed mogelijk.

## Alertniveaus

- **4054 / 4058** — range-top / short-entry
- **4024** — range-low; H1-close eronder = 4006 open
- **4074** — H1-close erboven = setup dood, terug naar 4090
- **4006 / 3980 / 3963** — targets / weekrange-bodem

## Orders & posities

| Item | Status |
|---|---|
| Breakdown-retest-short 4058 (B) | `active` PENDING; expireert vandaag 12:00 UTC (Rule 12); dry-run: SHORT LIMIT 4058 / SL 4074 / TP 4006 |
| Open posities gebruiker | geen bekend |
| Dry-run scorebord | +0,8R over 7 trades; discipline intact |

**Executie**: dry-run (credentials/netwerk niet ingesteld; cTrader-app wacht op KYC). Run gelogd. **Geen WhatsApp** (geen nieuwe A/B en geen fill — dezelfde pending order). Na 12:00 UTC/de data herbeoordeelt de NY-run; vrijdagavond gaat alles flat het weekend in (geen pending carry).
