# 2026-07-13 13:00 UTC — Kill zone-run (NY)

Data: Swissquote spot 4.062,4 (13:04 UTC), Yahoo GC=F 15m (vandaag).
Let op: future-spot basis schommelde vandaag tussen ~8 en ~13 punten —
futures alleen voor structuur gebruikt, niveaus op spot/broker geijkt.
Eén Zapier-call faalde tijdelijk (JWT-fout serverzijde), retry slaagde.

## Structuur sinds London

- London-low ~4.048 spot, daarna pullback-rally naar ~4.080 (OTE getikt,
  entry gebruiker gevuld op 4.075), rejection, nieuwe daling naar de
  low-zone ~4.048–4.050 → nu bounce naar 4.062 richting NY open.
- Equal lows rond 4.048–4.050 = liquidity pool onder de markt. TP1 (4.049)
  ligt daar precies op: goede kans op een sweep die TP1 raakt.
- Geen 15m-close boven 4.083 → short blijft geldig.

## Status posities/orders

1. **Open short 4.075** (SL 4.084, TP 4.049): +13 pt. Advies ongewijzigd:
   SL op 4.084 houden (achter structuur), BE pas na 15m-break onder 4.048.
   De bounce naar 4.062 kan de NY judas-swing zijn — 4.070–4.078 hertesten
   is normaal gedrag, geen reden tot actie.
2. **Swing short 4.133** (SL 4.157, TP 4.026): geldig, onaangetast.
3. **Long-trigger 1 waarschuwing**: worden de equal lows geveegd én volgt
   een 15m CHoCH omhoog, dan activeert het counter-long-scenario — maar de
   gebruiker zit short; TP1 nemen gaat dan vóór.

## Besluit

Geen nieuwe setup, geen WhatsApp (positiemanagement, geen nieuw A/B-signaal).

## Update 16:36 UTC — 4.000 GEBROKEN (flush live)

Spot 3.992 (M1-RSI 2,9). Long-trigger 2 in uitvoering: flush ✓, wachten op
reclaim. Entry alleen bij 15m-close terug boven ~4.003 (agressief) of
H1-close boven 4.000 (conservatief); SL onder de definitieve flush-low,
TP1 4.026, TP2 4.048, RR ≥ 1:2 verplicht op de echte low. Geen reclaim =
breakdown = flat blijven; onder 4.000 geen betrouwbare niveaus zonder
daily-data. Swing sell 4.133 ongewijzigd.
