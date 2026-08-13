# cBot Hardening — "live-proof" maken (research-gebaseerd)

Bron: deep-research (107 agents, 24/25 claims bevestigd, grotendeels **officiële cTrader-docs**).
Doel: XauEdge/XauSmart zó bouwen dat ze **niet glitchen** en **veilig naar live** kunnen.

> ⛔ **De #1 regel uit al het onderzoek:** *direct live met echt geld zonder wekenlange demo-
> validatie is de grootste faaloorzaak.* Overfitting faalt niet netjes — het klapt binnen dagen/
> weken zoals de backtest nooit liet zien. **Eerst demo. Altijd.**

## A. Betrouwbare order-executie (cTrader/cAlgo — geverifieerd)

1. **OnBar vs OnTick — bewuste keuze.** `OnTick()` vuurt bij elke bid/ask-verandering; `OnBar()`
   bij een nieuwe candle. **Let op:** `OnBar()` vuurt bij de **open** van de nieuwe bar → lees je
   signaal van de **zojuist gesloten** bar (`Last(1)`), niet de vormende bar, anders "repaint" je.
   XauEdge/XauSmart doen dit al goed (ze lezen `Last(1)`).
2. **SL/TP atomair meesturen.** `ExecuteMarketOrder(side, symbol, vol, Label, slPips, tpPips)` zet
   de bescherming in **één call** server-side. **Valkuil:** de parameters zijn in **PIPS, niet
   absolute prijs** — voor prijs-niveaus een aparte `ModifyPosition`-call. (Onze bots rekenen al
   in pips → goed.)
3. **Label = dubbele-order-preventie.** Check vóór entry `Positions.Any(p => p.Label == Label ...)`.
   Overleeft ook een herstart: na reconnect herken je je eigen positie aan het Label i.p.v. een
   tweede te openen. (Al aanwezig.)
4. **Synchroon executeren als je de uitkomst nodig hebt.** Sync `ExecuteMarketOrder` geeft een
   `TradeResult` — **check `IsSuccessful`**, log anders `r.Error`. Gebruik async alleen als je niet
   op de fill hoeft te wachten.
5. **Vertrouw NIET op de fault-tolerance om te stoppen.** cTrader **negeert** veel fouten en laat
   de bot **dóórlopen**. Dus: **expliciete `try/catch` rond elke trade-call**, en `OnException(...)`
   als **last-resort** vangnet (staat NIET in de default template — zelf toevoegen).
6. **Fault-tolerance vangt NIET alles.** `OutOfMemoryException`, `StackOverflowException` en elke
   exceptie in een **eigen thread** stoppen de instance alsnog (geen auto-herstart). → **Doe
   DOM/order-flow in de main event-thread** (XauSmart leest de DOM synchroon in OnBar → veilig).
   Gebruik je ooit het `.Updated`-event of een thread: wrap de hele body in try/catch.

## B. Concrete code-patronen (toe te passen / toegepast)

**Robuuste entry (retry + IsSuccessful + try/catch):**
```csharp
for (int attempt = 1; attempt <= 2; attempt++)
{
    try
    {
        var r = ExecuteMarketOrder(side, SymbolName, vol, Label, slPips, tpPips);
        if (r.IsSuccessful) { Print("OK {0} @ {1}", side, r.Position.EntryPrice); return; }
        Print("Entry mislukt (poging {0}): {1}", attempt, r.Error);
    }
    catch (Exception ex) { Print("Entry-exceptie (poging {0}): {1}", attempt, ex.Message); }
}
```

**Last-resort vangnet:**
```csharp
protected override void OnException(Exception exception)
{
    _haltRun = true; // stop nieuwe entries; bestaande SL/TP blijven server-side actief
    Print("OnException -> entries gestopt: {0}", exception.Message);
}
```

**State-persistence over herstart (AANRADER, nog te doen — verifieer de LocalStorage-API tegen
je cTrader-versie):** bewaar de circuit-breaker-tellers (`_consec`, `_haltDay/_haltRun`) én de
**totaal-DD-baseline** (`_initBal`). Zonder dit reset na een herstart je breaker én je DD-nulpunt →
de bot "vergeet" dat 'ie in een verliesreeks/halt zat. Patroon: bij OnStart uit `LocalStorage`
laden, bij elke wijziging wegschrijven. Reconcilieer open posities via `Positions` + Label.

## C. Wat banken/whales doen — en wat jij WEL/NIET kopieert

- **Zij:** VWAP/TWAP/Implementation-Shortfall slicen **grote** orders om market-impact te
  minimaliseren; dat leunt op **colocatie + infra** (colo ~$6-12k/mnd, feeds tot $50k/mnd, software
  tot $1M). Onmogelijk voor retail.
- **Belangrijke nuance (geverifieerd — één claim VERWORPEN):** het is een mythe dat je een
  latency-race móét winnen. Retail wint die niet, maar **niet-latency-gevoelige strategieën
  (trend/swing/liquidity-sweep op hogere TF — precies XauEdge/XauSmart) blijven wél viabel.**
- **Wat je WEL kopieert:** order-slicing/laddering, tijd-gespreide entries, en vooral **discipline +
  risicobeheer**. Daar win je, niet op snelheid.

## D. Risk-discipline (niet-onderhandelbaar, geverifieerd)

- **Risk per trade 1-2%** van equity; **totaal open risk 4-8%**. (Elder: 2%/6%.)
- **Drawdown is asymmetrisch:** -50% vereist +100% om terug te komen → harde loss-limits.
- **Step-down:** verlaag risk% als de drawdown oploopt (bijv. 1% → 0,5% bij -5%). Dit is exact wat
  `risk_guard` al doet (breaker bij ≥2 losses op rij of ≤ −3R/week).

## E. Validatie vóór live — de poorten (geen enkele overslaan)

1. **Tick-data, ≥ 1-2 jaar**, echte spread + commissie (FP Markets raw ECN).
2. **Walk-forward** (gouden standaard): optimaliseer in-sample → test out-of-sample → rol vooruit.
   Winst in **elk** OOS-blok = robuust. Alleen in-sample goed = **overfit → niet gebruiken**.
3. **Overfit-alarm:** onnatuurlijk **gladde equity-curve** + **veel parameters** t.o.v. trades.
   Vuistregel: **30-100 trades per vrije parameter**.
4. **Monte Carlo** op de trade-volgorde → overleeft de worst-case DD je account/limiet?
5. **Demo forward-test, WEKEN** → vergelijk live fills/spreads/slippage met de backtest. Dáár
   sneuvelen bots, niet op bugs.
6. Pas dán **klein live**, met de breaker + (op prop) de totaal-DD-halt aan.

## Openstaand (research kon dit niet volledig beantwoorden — doelgericht uitzoeken)
- Exacte reject/partial-fill-afhandeling op FP Markets raw ECN (`TradeResult.Error`-codes +
  backoff-retry).
- State-persistence over restart + positie-reconciliatie (LocalStorage-API per versie).
- Welke backtest-vs-live-verschillen op XAUUSD (spread/slippage/weekend-gaps) het meest degraderen.

## Kort
De "niet-glitchende" bot = **geverifieerde executie-patronen** (A/B) + **discipline** (D) +
**validatie** (E). De code-hardening is klein; de winst zit in het **proces**. En nogmaals:
**eerst weken demo, nooit blind live.**
