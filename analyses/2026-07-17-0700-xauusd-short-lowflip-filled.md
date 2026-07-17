# XAUUSD — kill zone-run London open, 2026-07-17 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 3994,7/3995,3 (mid 3995,0) · GC=F future 4004,1 → spread ~9 (niveaus in spot). Candles 1h (3d) vers.

## Marktanalyse

**De lowflip-short 4000 is gevuld en loopt.** Om ~03:20 UTC tagde de Asia-spike exact het cluster (high ~4003–4005 spot = 0.705 van de leg 4018→3967) en de limit vulde op 4000. Daarna rejection naar 3984, en nu een **tweede test van het cluster met een lagere high** (4001,7 vs 4003) — de zone houdt tot nu toe, prijs 3995, positie +5.

**Structuur**: onder de gebroken juli-low blijft het frame bearish (D1-close gisteren 3976, alle MA's dalend), maar de Asia-sessie bouwde hogere lows (3967 → 3974 → 3979) tegen het cluster aan — er zit dus wél koopdruk onder de markt. Dat maakt vandaag binair rond het cluster: houdt **4008–4013**, dan is de weg naar 3970/3950 open; H1-close boven **4013** en de short-these is dood met 4030 als volgende magneet.

**Boven**: 4003–4008 (cluster-top + 0.786 = 4007,7), **4013** (0.886 + SL), 4030, 4052. **Onder**: 3984 (nacht-flip), **3970/3967** (TP1 + low), 3950, 3910.

**Momentum (Rule 8)**: H1-momentum vlak-op (de grind omhoog), tegen de positie in — normaal voor een retracement-fill, maar het mag niet door 4013. **Event (Rule 12)**: vrijdag **12:30 UTC US-data** — de pending-order-administratie expireert om 12:00 UTC vanzelf; voor de (hypothetisch) lopende positie geldt het advies **SL naar breakeven vóór 12:30 UTC**.

## Lopend setup (gevuld — geen nieuwe orders vandaag vóór de data)

```
SETUP — XAUUSD 1H short (retest gebroken juli-low) — GEVULD @ 4000

Entry:        4000 (gevuld ~03:20 UTC op de 0.705-tag)   | huidig 3995 (+5)
Stop Loss:    4013 — achter 0.886 (4012,5); NAAR BREAKEVEN vóór 12:30 UTC US-data
Take Profit 1:3970 — nacht-low-zone
Take Profit 2:3950 | Take Profit 3: 3910 (runner)
Risk:Reward:  2,3 / 3,8 | Conviction B
Invalidatie:  H1-close boven 4013 → direct eruit, frame draait naar 4030
```

Geen tweede setup deze run: de positie loopt, het is data-dag (Rule 12) en stapelen vóór een release is precies wat de vangrails verbieden. Na de data (of bij de NY-run 13:00) herbeoordelen we.

**Scenario's**: (a) cluster houdt → TP1 3970, partial, rest naar 3950; (b) H1-close > 4013 → stop, wachten op 4030-supply of CHoCH; (c) data-spike omlaag door 3967 → TP's laten werken, niet bijplaatsen in het venster.

## Alertniveaus

- **4008** — derde test cluster-top; let op judas-swing bij London open
- **4013** — H1-close erboven = eruit
- **3984** — nacht-flip; verlies = momentum naar TP1
- **3970** — TP1; **3967** — low; break = continuation naar 3950

## Orders & posities

| Item | Status |
|---|---|
| Lowflip-short 4000 (B) | **GEVULD** (dry-run) @ 4000, nu +5; order-administratie expireert 12:00 UTC (Rule 12), positie-advies SL→BE vóór 12:30 |
| Swing-short 4133 (B) | `active` t/m 20:00 UTC vandaag — fill-kans nihil (138 pt boven markt), verloopt vanavond vanzelf |
| Dry-run scorebord | +2,5R · -1R · -1R · -1R → -0,5R; lopende short +0,4R open |

**Executie**: dry-run (credentials/netwerk nog niet ingesteld door gebruiker; cTrader-app wacht op KYC). Run gelogd. WhatsApp verstuurd (fill-update B-setup).
