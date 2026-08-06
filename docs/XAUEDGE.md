# XauEdge — de flagship-bot + het proces dat 'm laat werken

`strategies/XauEdge.cs`. Dit is de bot om te gebruiken; de andere drie (`XauScalper`,
`XauFlow`, `XauBreakout`) blijven experimenten. Hieronder eerst waarom simpel wint, dan de
**5 stappen** die het verschil maken tussen "mooie backtest" en "werkt live".

## Waarom de simpelste bot de beste is (geen mening — onderzoek)

- **Minder parameters = robuuster.** Elke extra knop is een kans om te *overfitten*: de bot
  leert de ruis van het verleden i.p.v. een echte edge. XauEdge heeft **5 strategie-knoppen**.
- **Complexe bots scoren mooi in de backtest en sterven live.** Wat telt is dat de winst
  **out-of-sample** (op ongeziene data) standhoudt.
- **Win rate is een afleiding.** Optimaliseer op **profit factor** (1,2–1,5+) en **max
  drawdown**, met een gezonde **expectancy** — niet op win%.

Bronnen: <https://www.luxalgo.com/blog/what-is-overfitting-in-trading-strategies/> ·
<https://blog.quantinsti.com/walk-forward-optimization-introduction/> ·
<https://en.wikipedia.org/wiki/Walk_forward_optimization>

## De edge (één ding, goed gedaan)

Trend-momentum: **alleen mee met de H1-trend** (koers t.o.v. H1-EMA), instap op een
**momentum-breakout** (bar sluit boven de hoogste high van de laatste N bars = long; onder de
laagste low = short). ATR-stop, vaste RR, %-risk, break-even/trailing, en de veiligheidslagen
(spread/sessie/dag-breaker/totaal-DD). That's it.

## Het proces — 5 stappen (dit is 80% van het werk)

### 1. Goede data
XAUUSD **tick-data** (of m1) in cTrader, **≥ 2 jaar**, inclusief nieuws/crashes. Zet
**echte commissie + spread** aan. Slechte data = fictieve resultaten.

### 2. In-sample optimaliseren — op de JUISTE maatstaf
Optimaliseer op **Net Profit / Profit Factor**, met **Max Drawdown** als harde grens. Vary
alleen de 5 edge-knoppen (`TrendEma`, `BreakoutBars`, `SL=ATR x`, `RR`, sessie). Pak **niet**
de absolute topscore — pak een waarde die in een **breed, vlak gebied** van goede resultaten
ligt (robuust), niet een geïsoleerde piek (overfit).

### 3. Walk-forward (de belangrijkste stap)
Optimaliseer op periode A → test **out-of-sample** op de daaropvolgende periode B → schuif het
venster op en herhaal. cTrader's optimizer + handmatig vensters, of split je data in 4–6 blokken.
**Slaagt de bot alleen in-sample maar faalt out-of-sample → overfit, niet gebruiken.**
Consistente winst over álle out-of-sample-blokken = een echte edge.

### 4. Monte Carlo / stress
Neem de trade-reeks en schud 'm 1.000× door elkaar (of varieer entry met ±1 tick / random
skip 10% trades). Zo zie je de **verdeling** van uitkomsten, niet één gelukkig pad. Kijk of de
**worst-case drawdown** je account (en je The5ers-limiet!) overleeft.

### 5. Demo → klein live
Draai **weken op de FP Markets demo**; vergelijk live fills/spreads met de backtest (ze moeten
matchen). Pas dán klein live, met de breaker + (op The5ers) de totaal-DD-halt aan.

## Pass/fail-poorten (haal je er één niet → niet live)

| Poort | Eis |
|---|---|
| Profit factor (out-of-sample) | **≥ 1,3** |
| Consistentie | winst in **elk** walk-forward-blok, niet één uitschieter |
| Max drawdown (Monte Carlo p95) | **binnen** je risicolimiet / The5ers-DD |
| Live-vs-backtest (demo) | fills/spreads **matchen**, geen grote afwijking |
| Aantal trades | genoeg (**>100+**) voor statistische betekenis |

## Presets

- **FP Markets demo (testen):** `Max TOTAL DD %` = 0, `Risk %` 0,5, `Max spread` ~2× je rustige
  XAUUSD-spread. Hier alles valideren.
- **The5ers (funded):** zet de veiligheid **strakker dan hun limiet** — Hyper Growth:
  `Daily loss %` 2, `Max TOTAL DD %` 4,5, `Risk %` 0,25–0,5. XauEdge is bar-based (geen HFT),
  dus toegestaan.

## Kort

De "ziekste" bot is de **simpelste met een echte, gevalideerde edge**. XauEdge levert de simpele
edge; stap 1–5 hierboven leveren het "dit moet echt goed gaan". Sla geen stap over — vooral niet
walk-forward. Geen bot is gegarandeerd winstgevend; deze aanpak geeft je de beste eerlijke kans.

> `.cs`-bots draaien in cTrader (C#), niet in deze repo. Compileren + backtesten doe je daar.
