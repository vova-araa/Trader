# XAUUSD — on-demand analyse (screenshot M5), 2026-07-14 18:40 UTC (20:38 NL)

**Bron**: screenshot broker-app M5 + eerdere datafeeds van vandaag. Prijs 4052,50 (broker/spot). Open positie gebruiker: **BUY 0.2 vanaf 4004,33 (+$969)**, TP 4125,83. Pending: **SELL LIMIT 0.2 @ 4133,03** (= pipeline swing-short).

## Marktanalyse

De CPI-move is volledig teruggezakt naar de origin: spike 4030 → 4107, daarna trapsgewijs lager (lower highs 4100 → 4085 → 4070) en nu **4052,5 — precies de S/R-flip van de 13-jul breakdown én de 0.705 OTE van de CPI-leg**. M5-momentum(14) = 99,76 (DOWN), RSI(7) = 23,6 (oversold op support). H1 blijft bullish van structuur (CHoCH van vanmiddag intact zolang 4030+ houdt), H4 blijft bearish onder 4143. Buiten de kill zones — geen setup forceren, limits laten werken.

**Fib-cluster (multi-leg, incl. 0.65) op de CPI-legs**:
- Kleine leg 4030 → 4107: 0.618 = 4059,4 · 0.65 = 4057,0 · **0.705 = 4052,7 (huidige prijs!)** · **0.786 = 4046,5** · 0.886 = 4038,8
- Grote leg 4004,3 → 4107: **0.618 = 4043,5** · 0.65 = 4040,2 · 0.705 = 4034,6
- **Cluster: 4043,5–4046,5** (0.618 groot + 0.786 klein) — de sweet spot nét onder de markt

## Beste setup

```
SETUP — XAUUSD 15m long (OTE-retest van de CPI-breakout)

Bias:         Long op H1 — CHoCH omhoog intact, geslaagde breakout boven de 4052-zone
              wordt van bovenaf geretest; H4 blijft bearish onder 4143 (dus geen A)
Zone:         4043 – 4053 — S/R-flip 4052 + OTE-cluster (0.705 klein op 4052,7;
              0.618 groot 4043,5 + 0.786 klein 4046,5)
Confluences:  fib-cluster multi-leg + breakout-retest van de 13-jul supply (nu demand) +
              RSI(7) oversold 23,6 op de zone + H1-structuur bullish; M5-momentum DOWN
              levert de entry aan maar is tegen de richting (Rule 8 → conviction lager)

Entry:        4046 (limit in het cluster; agressief: 4052 direct)
Stop Loss:    4036 — achter 0.886 (4038,8) én onder de 4040-shelf
Take Profit 1:4080 — post-CPI consolidatie / eerste supply
Take Profit 2:4100 — CPI-high zone
Take Profit 3:4125 — runner (= TP van je open long)

Risk:Reward:  3,4 (TP1) / 5,4 (TP2)
Invalidatie:  15m-close onder 4036 — dan is de retest gefaald en flipt het speelboek
Conviction:   B — sterke confluence op de zone, maar tegen H4-bias én M5-momentum in
```

**Flip-scenario (trigger, geen order)**: 15m-close onder 4040 → CPI-move afgewezen, short-continuation richting 4030 (shelf) en 4004; onder 4004 ligt 3981. Dan is ook de open long zijn edge kwijt.

## Positie-management (open BUY 0.2 vanaf 4004,33)

- **Trek je SL op naar minimaal 4038–4040** (onder de flip + 0.886). Dat locked ~+$680–700 van de huidige +$969 en je zit gratis in het long-scenario.
- Alternatief: 50% winst nemen op 4052 en de rest op de opgetrokken SL laten lopen naar 4125.
- Je SELL LIMIT 4133 kan blijven: invalidatie (H1-close > 4143) is niet geraakt en hij dekt het scenario waarin de long-runner tegen de H4 lower-high aanloopt.

## Alertniveaus

- **4040** — verlies = long-invalidatie nabij + flip-trigger
- **4046** — cluster-entry actief
- **4080** — TP1 / supply; break = weg naar 4100 open
- **4107** — CPI-high; erboven komt de fade-short 4098 onder druk (die expireert 20:00 UTC vanzelf)

## Orders & posities (pipeline)

| Item | Status |
|---|---|
| OTE-long 4046 (B, nieuw) | `active` t/m 15-07 07:00 UTC; executor dry-run: LONG LIMIT 4046 / SL 4036 / TP 4080 |
| CPI-fade-short 4098 (B) | `active`, nooit gevuld (high na plaatsing ~4086); expireert 20:00 UTC |
| Swing-short 4133 (B) | `active` t/m 17-07 — door gebruiker handmatig als SELL LIMIT 0.2 op de broker gezet |
| Open positie | BUY 0.2 @ 4004,33 (+$969) — handmatig door gebruiker; advies SL → 4038–4040 |

**Executie**: dry-run (geen CTRADER-credentials). Run gelogd in `signals/execution_log.jsonl`.
