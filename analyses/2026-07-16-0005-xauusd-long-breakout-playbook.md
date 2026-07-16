# XAUUSD — on-demand analyse (screenshots M30 + H4), 2026-07-16 00:05 UTC (02:05 NL)

**Bron**: screenshots broker-app. Prijs 4057,4. Posities gebruiker: BUY 0.2 @ ~4028,4 (+$577,80, SL ~4024,6 = vrijwel breakeven-lock), SELL LIMIT 0.2 @ 4133,08 (SL 4157, TP 4039,95). Indicatoren: M30 Momentum(14) 100,57 / RSI(7) 50,9; H4 Momentum(14) 101,59 / RSI(7) 52,6.

## Marktanalyse

**H4 (macro)**: de meidaling (4680 → 3980) is nog het dominante frame — beide MA's dalen boven de prijs. Maar juli bouwt onmiskenbaar een base: **higher lows 3981 → 4016 → 4028**, drie krachtige rejections van de onderkant, en H4-momentum kruipt boven 100. Dit is een decision zone: base-breakout of zoveelste lower high.

**M30 (intraday)**: na de 12:45-spike naar 4072 kwam de pullback exact in de OTE-zone van gisteren (4028–4048) en daar is jouw long gevuld — netjes. Sindsdien: hogere bodems ónder de dubbele weerstand **4070–4072**. Ascending-triangle-gedrag: kopers dringen op tegen een vaste deksel. Boven: 4070–4072 (trigger), 4084–4093 (0.786/0.886-cluster + supply), 4107 (CPI-high), 4133–4143 (swing-zone). Onder: 4040 (flip), 4028–4030 (base + jouw entry), 4016, 4004, 3981.

**Timing**: Asia — liquidity-mapping, geen kill zone. Orders forceren is hier tegen de regels; het speelboek is voor London.

## Setup (trigger-voorwaardelijk — Rule 13, dus GEEN blinde limit in de pipeline)

```
SETUP — XAUUSD M30 long (breakout-retest 4072) — pas ná trigger

Bias:         Long intraday — higher lows 3981→4016→4028 onder een vaste deksel
              4070/4072; H4 formeel nog bearish (dalende MA's) → bevestiging
              verplicht vóór entry (Learned Rule 13)
Zone:         4060 – 4068 — retest van de gebroken 4066-4072 weerstand (na de trigger)
Confluences:  triple-top-liquidity boven 4072 + higher-low-reeks + H4-momentum >100
              + retest-zone = oude supply-onderkant; M30-momentum rond 100 neutraal

TRIGGER:      M30-close boven 4072. Zonder die close bestaat deze setup niet.
Entry:        4064 (limit op de retest, pas plaatsen ná de trigger)
Stop Loss:    4051 — onder de retest-structuur én de laatste M30 higher low
Take Profit 1:4093 — top van het 0.786/0.886-cluster
Take Profit 2:4107 — CPI-high
Take Profit 3:4125 — net onder je sell limit-zone (runner eruit vóór de supply)

Risk:Reward:  2,2 (TP1) / 3,3 (TP2)
Invalidatie:  M30-close terug onder 4052 na de breakout = failed break, setup dood
Conviction:   B (ná trigger) — mooie base + duidelijke trigger, maar tegen het
              H4-macroframe in, dus zonder bevestiging geen trade
```

**Short-scenario (spiegel)**: geen M30-close boven 4072 maar een rejection in **4084–4093** na een sweep van 4072 → 15m bearish CHoCH → short richting 4052/4040. En zakt de base door **4028** heen, dan is 4016 → 4004 direct in beeld en is de triangle gefaald.

## Positie-management

- **BUY 0.2 @ 4028,4**: SL op 4024,6 is al bijna een free trade — perfect. Plan: bij M30-close > 4072 SL naar **4052** en laten lopen naar 4107/4125; bij een derde afwijzing op 4070–4072 zónder break → partial nemen, want dan groeit de kans dat de deksel houdt.
- **SELL LIMIT 4133**: laten staan (cancel-discipline: H1-close > 4143). Rotatie-scenario blijft: long runt eruit op 4125, short neemt over in de supply.

## Alertniveaus

- **4072** — de triggerlijn (M30-close erboven = speelboek long actief)
- **4084–4093** — supply; rejection = short-scenario
- **4040** — flip; verlies zet de base onder druk
- **4028** — jouw entry/base; M30-close eronder = triangle gefaald

## Orders & posities (pipeline)

| Item | Status |
|---|---|
| Breakout-long 4064 | ADVIES met trigger — NIET in signals (Rule 13: geen blinde counter-HTF limit; executor kan geen conditionele orders aan) |
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC |
| Gebruiker | BUY 0.2 @ 4028,4 (SL 4024,6) + SELL LIMIT 0.2 @ 4133 |

**Executie**: geen wijziging aan het signaalbestand (trigger-setup blijft advies tot de M30-close boven 4072 er is; daarna kan hij als A/B-signaal worden toegevoegd).
