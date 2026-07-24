# XAUUSD — NY-run / weekafsluiting, 2026-07-24 13:00 UTC (15:00 NL)

**Data**: Swissquote spot 4046,4/4047,0 (mid 4046,4) · GC=F future ~4056–4067 → future-premium terug (~10–15; roll voltooid). Spot blijft de anker. 15m-candles vers.

## Marktanalyse

**Het datavenster bracht geen richting; de range houdt.** De 12:30 UTC US-data leverde een milde bounce naar de range-top (spot ~4054–4056, future 4067) die direct werd verkocht — prijs terug naar **4046**. De hele dag blijft de compressie **~4024–4056 (spot)** onder de gebroken 4052-flip intact. Geen doorbraak naar 4006, geen herovering van 4052.

- **Intraday: neutraal-bearish** — range onder de flip, lagere toppen, maar geen momentum.
- **D1/weekly: bearish** — trend-mee intact; weekrange 3963–4052, 4278 blijft de grote weekly-weerstand.

**Fib (drop-leg 4107 → 4024)**: de bounces blijven onder de 0.382 (4055,7) — structureel zwak, past bij een bearish continuation-pauze.

**Momentum (Rule 8)**: 15m/H1 vlak. Vrijdagmiddag + range + net na data = geen edge, en **geen order het weekend over** (gap-risico).

## Rule 12 werkte — de short expireerde schoon

De breakdown-retest-short 4058 is om **12:00 UTC verlopen** (Rule 12), vóór de data, **zonder fill en zonder risico**. De post-data bounce naar ~4056 kwam ná de expiry — de order had daar toch niet op de goede kant gestaan. Precies de discipline die op 15-07 nog -1R kostte, nu correct toegepast.

## Setup — geen (weekend flat); scenario's voor maandag

```
CONTINUATION-SHORT (trend-mee) — trigger maandag
Zone/trigger: H1-close onder 4024 → range-breakdown → 4006 / 3980 / 3963
Of:           bounce naar 4052-4058 + 15m bearish rejection → zelfde targets

RECLAIM-LONG (counter, alleen mét bevestiging) — trigger maandag
Trigger:      H1-close boven 4074 → breakdown teruggekocht → 4090/4107 (Rule 13)
```

Geen enkele order gaat het weekend in — bij een weekend-gap doet een SL niet wat je denkt. Maandag 09:00 NL (London) pakt de eerste trigger op met verse data.

## Alertniveaus

- **4024** — range-low; H1-close eronder = 4006 open (maandag)
- **4052 / 4058** — range-top / flip; rejection = short, reclaim boven 4074 = long
- **4006 / 3980 / 3963** — bearish targets / weekrange-bodem
- **4278 / 3876** — weekly-referenties

## Orders & posities

| Item | Status |
|---|---|
| Breakdown-retest-short 4058 | `expired` 12:00 UTC (Rule 12) — schoon, geen fill, geen risico |
| Actieve pending orders | geen — alles flat het weekend in |
| Open posities gebruiker | geen bekend |

## Dry-run scorebord — twee weken compleet

**+0,8R totaal over 8 gevulde trades** (3W / 4L / 1 BE):
+2,5R (breakdown-short) · +2,3R (lowflip-short) · 0R (supply-short BE) · −1R ×4 (ote-long, retest-short, sweep-long, fridayflip) · plus talloze correcte "geen order"-beslissingen die verliezers voorkwamen.

**Kernles van 2 weken**: de winnaars waren trend-mee met kill-zone-timing; alle verliezers waren óf counter-trend óf procesfouten die nu harde regels zijn (12 = datavenster, 13 = CHoCH-bevestiging). Geen enkele trade > 1R verlies. Dat is een overleefbaar systeem — precies wat een dun account nodig heeft.

**Executie**: dry-run (credentials/netwerk niet ingesteld; cTrader-app wacht op KYC). Run gelogd. **Geen WhatsApp** (geen setup — weekend). Maandag draait dit live op demo zodra de credentials + poort 5035 er zijn.
