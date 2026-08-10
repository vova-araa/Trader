# XauSmart — de "smart money" XAUUSD-bot (FP Markets raw ECN)

`strategies/XauSmart.cs`. Dit is de bot die de hele order-flow/liquidity-discussie automatiseert:
hij handelt waar het grote geld instapt — op een **liquidity sweep (stop-hunt)** die door
**order flow (DOM)** wordt bevestigd. Bewust **FP-Markets-gespecialiseerd**, want de order-book-laag
bestaat alleen op een echte ECN.

> ⚠️ **NIET op The5ers.** Order-flow/sweep-scalping raakt hun HFT-verbod, en hun feed levert de
> diepe DOM niet. XauSmart is voor je **FP Markets raw ECN**-account. Voor The5ers gebruik je de
> bar-based `XauEdge`.

## De edge — één samenhangend idee (geen los-zand van indicatoren)

1. **HTF-trendfilter** (H1-EMA): alleen mee met de hogere-tijdframe-richting (Rule 14 / risk_guard).
2. **Liquidity mapping**: hoogste high / laagste low over de laatste N bars = de **stop-pools**
   (buy-side boven de high, sell-side onder de low).
3. **Sweep-detectie**: de bar wickt **voorbij** dat niveau (neemt de stops) en sluit weer **terug
   binnen**, met een sterke rejection (≥ x·ATR). Long = sweep van de sell-side low + close erboven;
   short = mirror. Dit is de voetafdruk van een stop-hunt.
4. **Order-flow-bevestiging (DOM)**: op de sweep moet de order-book de reversal steunen —
   bid-volume ≥ ask-volume × ratio voor een long (kopers absorberen). Geen DOM beschikbaar? Dan
   **fallback op een volume-burst** (tick-volume >> gemiddelde).
5. **Entry op de reversal**, **stop net voorbij de sweep-extreme** (tight → hoge RR), TP = RR-multiple,
   daarna trailen richting de tegenoverliggende liquidity.

Waarom dit werkt: whales kunnen hun grote size niet in één keer kwijt, dus ze **jagen eerst de stops**
om liquiditeit te vinden en draaien dán. De tight stop achter de sweep-extreme geeft je een
asymmetrische R:R die een gewone breakout-bot niet heeft.

## De knoppen (bewust beperkt)

| Groep | Knop | Default | Wat |
|---|---|---|---|
| Edge | HTF timeframe / trend EMA | Hour / 50 | trendrichting-filter |
| Edge | Liquidity lookback | 20 bars | hoe ver terug de stop-pools |
| Edge | Min rejection (xATR) | 0,5 | hoe sterk de terug-close moet zijn (ruisfilter) |
| Edge | Allow counter-trend | uit | standaard alleen trend-mee |
| Order flow | Use order flow (DOM) | aan | DOM-bevestiging vereisen |
| Order flow | DOM levels / imbalance | 5 / 1,5 | diepte + benodigde bid/ask-scheefheid |
| Order flow | Volume-burst x avg | 1,5 | fallback als DOM leeg is |
| Risk | Risk % / Stop buffer / RR / Trail | 0,5 / 0,5xATR / 2,5 / 1,5xATR | sizing + exits |
| Safety | spread / sessie / dag-breaker / totaal-DD | 30 / 7-20 / 2%+3 / 0 | de vangnetten |

## Installeren

1. cTrader **Desktop/Web** → **Automate** → **New cBot** → plak `strategies/XauSmart.cs` → **Build**.
2. Log in op je **FP Markets raw ECN**-account (levert de DOM). Open een **XAUUSD M5/M15**-chart.
3. Sleep XauSmart erop, kies instance, check de parameters, **Backtest**-tab.

## Het proces — dít laat 'm slagen (niet het sleutelen aan de code)

Zelfde discipline als `docs/XAUEDGE.md`, met één extra: **order flow backtest je alleen eerlijk met
tick-data**.

1. **Tick-data, ≥ 1-2 jaar**, met **echte commissie + spread** aan. Zonder tick-data is de
   order-flow-laag fictie.
2. **Optimaliseer op profit factor / net profit**, met **max drawdown** als harde grens — NOOIT op
   win rate. Vary de edge-knoppen (lookback, rejection, DOM-imbalance, RR), niet alles tegelijk.
3. **Walk-forward** (de belangrijkste stap): optimaliseer op periode A → test out-of-sample op B →
   schuif op. Slaagt 'ie alleen in-sample → overfit, niet gebruiken.
4. **Monte Carlo**: schud de trade-reeks 1.000× → kijk of de worst-case drawdown je account (en
   je limiet) overleeft.
5. **Demo → klein live**: weken op de **FP Markets demo**, vergelijk of live DOM/fills matchen met
   de backtest. Order flow is gevoeliger voor slippage — check dat expliciet.

### Pass/fail-poorten
| Poort | Eis |
|---|---|
| Profit factor (out-of-sample) | ≥ 1,3 |
| Consistentie | winst in **elk** walk-forward-blok |
| Max drawdown (Monte Carlo p95) | binnen je risicolimiet |
| Live-vs-backtest (demo) | DOM-gedrag + fills matchen, geen grote slippage-afwijking |
| Aantal trades | > 100 voor statistische betekenis |

## Presets (FP Markets)

- **FP Markets demo (testen):** `Use order flow` aan, `Max TOTAL DD %` 0, `Risk %` 0,5,
  `Max spread` ~2× je rustige XAUUSD-spread, `DOM imbalance` 1,5. Hier alles valideren.
- **FP Markets klein live (na validatie):** `Risk %` 0,25-0,5, breaker aan, `Max spread` strak.
  Rond **hoog-impact nieuws (bijv. CPI 12:30 UTC)**: pauzeer de bot of laat de sessie/spread-guard
  'm eruit houden — order-flow-signalen zijn dan onbetrouwbaar (Rule 12).

## Eerlijke grenzen

- **Geen echte HFT, geen garantie.** Dit leest de sporen (sweep + absorptie) en executeert
  gedisciplineerd — dat is de haalbare edge, niet magie.
- **cTrader-DOM = je broker's aggregatie**, geen volle COMEX-L2. Op raw ECN bruikbaar; verwacht geen
  bank-niveau order flow.
- **Meer knoppen dan XauEdge** → hoger overfit-risico. Houd 'm strak, valideer walk-forward, en als
  een simpelere variant (DOM uit, puur sweep + volume-burst) out-of-sample even goed is: kies die.

> `.cs`-bots draaien in cTrader (C#), niet in deze repo. Compileren + backtesten doe je daar.
