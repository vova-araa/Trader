# XAUUSD — avondrun, 2026-07-20 19:00 UTC (21:00 NL)

**Data**: Swissquote spot 4006,3/4006,9 (mid 4006,3) · GC=F future 4011,5 → spread ~5. Candles 15m vers. Dagrange 3986,5 – 4046,0.

## Marktanalyse

**De supply-short 4030 loopt nog, +24 open.** Na de rejection van 4046 zakte de prijs in de NY-sessie naar **4002** (15m-low 4001,6) — dicht bij, maar **TP1 3986 niet geraakt** — en bouncede terug naar 4006/4011. De hele middag/avond is een chop tussen **4002 en 4046**; de bounce van 4002 maakt de korte termijn minder eenrichtings.

**Structuur**: nog steeds range **3986–4046** binnen de grotere 3963–4052. Prijs 4006 = onderste helft, maar de verkoopdruk stokt boven de dag-low. **Onder**: 4000 (psych/scharnier), 3986 (dag-low = TP1), 3968, 3963. **Boven**: 4020 (intraday LH), 4046 (dag-high/SL-zone), 4052 (range-top).

**Momentum (Rule 8)**: 15m vlak/licht op na de 4002-bounce — het momentum dat de trade droeg is afgezwakt. D1/H4 blijven bearish, dus de bias klopt nog, maar het intraday-tempo is weg. Buiten kill zones nu (Asia-aanloop) — geen nieuwe order forceren.

## Positie-management (geen nieuwe order)

```
SETUP — XAUUSD 1H short @ 4030 (GEVULD) — B

Huidig:       4006 (+24 open)
Stop Loss:    → BREAKEVEN 4030 (risicoloze trade vanaf hier)
Take Profit 1:3986 — dag-low (partial bij touch)
Take Profit 2:3968 | Take Profit 3: 3950 (runner)
Beheer:       runner overnight met BE-stop; bij 3986 partial + rest trailen naar 3998
Invalidatie:  terug boven 4030 = BE-stop (0R), geen schade
```

Waarom geen partial forceren op +24: met de stop op BE is het risico nul, dus de runner mag ademen richting 3986. Het enige "verlies" scenario is 0R (terug naar BE) — precies wat je wilt op een lopende winnaar in dunne uren.

**Scenario's overnight**: (a) door 4000 → TP1 3986, partial; (b) chop 4002–4020 → BE-stop beschermt, geduld; (c) terug boven 4046 → range breekt omhoog, dan is 4070 in beeld en is de short-swing voorbij (BE, 0R).

## Alertniveaus

- **4000** — scharnier; break = TP1 3986 in zicht
- **3986** — TP1 / dag-low
- **4030** — BE-stop (terug hierboven = flat, 0R)
- **4046 / 4052** — range-top; H1-close erboven = bias-flip omhoog

## Orders & posities

| Item | Status |
|---|---|
| Supply-short 4030 (B) | **GEVULD**, +24 open; **SL op BE 4030**; runner naar 3986/3968 overnight |
| Open posities gebruiker | geen bekend |
| Dry-run scorebord | week 29 +0,8R gesloten; deze short +2,4R open (op BE-stop min. 0R gelockt) |

**Executie**: dry-run. Geen nieuwe A/B-setup deze run (positie loopt, niet stapelen) — WhatsApp als management-update op de lopende B. Live-setup wacht nog op: cTrader KYC ("Active"), netwerkpolicy poort 5035, env vars — en op jouw saldo + minimaal lot voor de veilige sizing.
