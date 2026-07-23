# XAUUSD — kill zone-run London open, 2026-07-23 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4107,7/4108,4 (mid 4107,7) · GC=F future ~4120 → spread verbreed naar ~12 (genoteerd; kalibratie op spot). 1h-candles vers. NB: één 1h-candle toont een low 4074,6 met volume 0 — **data-artefact/dunne wick, niet als echte low meegenomen**.

## Marktanalyse

**De rally kreeg zijn eerste serieuze pullback — recht in de OTE + flip.** Na de top op ~4158 (spot; future 4171) trok de prijs terug naar **4107,7** — precies:
- de **0.65-OTE** van de leg 4081 → 4158 (0.618 = 4110,4 · 0.65 = 4107,9 · 0.705 = 4103,7), én
- de **4107-flip** (CPI-high 14-07, break-retest-support van de hele week).

Twee onafhankelijke redenen op exact hetzelfde niveau = **fib-cluster + structuur** (Rule 6/7). De 3-daagse uptrend (3963 → 4158, +195 pt) is intact zolang deze zone houdt.

- **H1/H4: bullish** — dit is een pullback in een uptrend, geen omkering (tenzij 4090 valt).
- **D1: bijna neutraal** — lower-high-reeks vrijwel gebroken.
- **Weekly: nog bearish** — 4278 blijft de grote weerstand; long = counter-weekly → **bevestiging verplicht (Rule 13)**.

**Momentum (Rule 8)**: 1h drift nog licht DOWN de zone in — **nog geen 15m bullish CHoCH**. De prijs zit ín de zone maar heeft niet gedraaid.

## Setup — geprimede long met trigger (geen blinde limit; Rule 13)

```
SETUP — XAUUSD 15m long (OTE + flip-retest van de uptrend) — WACHT op trigger

Bias:         Long met de 3-daagse trend; counter-weekly dus bevestiging verplicht
Zone:         4103 – 4110 — 0.65-OTE (4107,9) + 4107-flip (CPI-high/weekflip)
TRIGGER:      15m bullish CHoCH in de zone (higher low + reclaim). NU niet vervuld
              — prijs drift nog omlaag, geen draai. Zonder trigger geen entry
Entry:        4107 (op/na de trigger)
Stop Loss:    4090 — onder 0.886 (4092) én onder de zone = pullback werd omkering
Take Profit 1:4140 — recente consolidatie-high (eerste liquidity)
Take Profit 2:4158 — de high | Take Profit 3: 4180 (runner)
Risk:Reward:  1,9 (TP1) / 3,0 (TP2)
Invalidatie:  15m-close onder 4090 = OTE/flip verloren, uptrend-dag draait
Conviction:   B (na trigger) — A-locatie (cluster), maar counter-weekly en de
              trigger moet nog printen
```

**Omkeer-scenario (short, trend-mee weekly)**: 15m-close onder **4090** → de 4107-flip is verloren, het hele break-retest-verhaal draait → short richting 4052/4030 (SL boven 4107). Dat wordt dan de trend-mee (weekly) trade en zet ik direct in de pipeline.

## Waarom (nog) geen order

Prijs zit exact in een A-locatie, maar de long is counter-weekly en de zone heeft nog niet gedraaid (geen 15m-CHoCH) — een blinde limit hier is precies de OTE-long-4046-fout (Rule 13). En de short is pas geldig ná verlies van 4090. Beide wachten op een 15m-close. Dit is de belangrijkste besliszone van de week: **4090 is de scheidslijn** tussen "uptrend leeft, long naar 4158" en "pullback werd omkering, short naar 4052".

## Alertniveaus

- **4107 / 4103** — OTE + flip; hold + 15m-CHoCH = long-trigger
- **4090** — 15m-close eronder = long dood, short-scenario actief
- **4140 / 4158** — long-targets / recente highs
- **4052** — eerste short-target onder 4090

## Orders & posities

| Item | Status |
|---|---|
| Actieve pending orders | geen — geprimed, wacht op 15m-trigger boven of onder |
| Open posities gebruiker | geen bekend |
| Dry-run scorebord | +0,8R over 7 trades; discipline intact |

**Executie**: dry-run (credentials/netwerk niet ingesteld; cTrader-app wacht op KYC). Run gelogd. **Geen WhatsApp** (geen actieve A/B-order — geprimed, trigger nog niet vervuld). Zodra 4090 breekt of een 15m-CHoCH print, kan de dan-geldige setup als A/B in de pipeline en volgt WhatsApp.
