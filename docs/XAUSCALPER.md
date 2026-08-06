# XAUUSD cBot-suite (cTrader Automate)

Drie cBots voor goud, allemaal met dezelfde risk-scaffolding (%-risk sizing, ATR-stops,
spread-guard, sessie-filter, break-even/trailing) én een **in-bot circuit breaker**
(consec-loss + dagverlies + max trades, idee van `scripts/risk_guard.py`). Geen martingale,
altijd een harde stop.

| Bot | Bestand | Stijl | TF | Aard |
|---|---|---|---|---|
| **XauScalper** | `strategies/XauScalper.cs` | trend-pullback momentum | M1/M5 | hogere win rate, RR ~1,4 |
| **XauFlow** | `strategies/XauFlow.cs` | tick-order-flow / volume-structuur | tick/M1 | "HFT-achtig", snel in/uit, RR ~1,2 |
| **XauBreakout** | `strategies/XauBreakout.cs` | Donchian/range-breakout + volume | M5/M15 | lagere win rate, RR ~2, grote winnaars |

Kies er één per chart/instance (niet stapelen op hetzelfde symbool). Hieronder de details van
XauScalper; XauFlow en XauBreakout hebben dezelfde risk-logica, andere entry.

## XauScalper — trend-pullback momentum

## Eerst: de "90% win"-valkuil (waarom die target verkeerd is)

Win rate alleen zegt **niets** over winst. Je haalt makkelijk 90% wins met een brede stop +
mini-TP — maar één loser (die 10%) wist dan tientallen winnaars uit. Wat telt:

- **Expectancy** = (winrate × gem. winst) − (verliesrate × gem. verlies). Dit moet **positief**.
- **Profit factor** = brutowinst / brutoverlies. **1,2–1,5** is werkbaar voor scalping.
- **Max drawdown** — hoe diep zakt de equity? Bepaalt of je 't overleeft.

Normale win rates: **55–70%** voor scalping/mean-reversion, 30–45% voor trend-volgen — beide
kunnen top zijn. Bij goud vreet de **spread** je edge, dus scalp niet blind. Optimaliseer
daarom op **Net Profit / Profit Factor / Drawdown**, nooit op win rate alleen.

Bronnen: <https://tradingstats.net/win-rate-profit-factor-expectancy/> ·
<https://www.tradezella.com/blog/win-rate> ·
<https://help.ctrader.com/ctrader-algo/documentation/cbots/cbot-code-samples/>

## Wat de bot doet

1. **HTF-trendfilter** (H1 EMA 21/55): alleen long in bullish, short in bearish HTF — geen
   counter-trend (zelfde geest als Rule 14 / risk_guard).
2. **Entry**: pullback naar de entry-EMA op de chart-TF die weer in de trendrichting sluit,
   met RSI-momentumbevestiging. Geen midden-trades.
3. **ATR-stops**: SL = ATR×1,5 (instelbaar), TP = SL×RR (default RR 1,4). Volatiliteit
   bepaalt de stop.
4. **Spread-guard**: skip als de goud-spread > MaxSpreadPips (default 30) — anti-scalp-killer.
5. **Sessie-filter**: alleen 07–20 UTC (Londen+NY), instelbaar.
6. **Break-even + ATR-trailing**: stop naar BE zodra +1×ATR, daarna trailen op 1,5×ATR.
7. **Circuit breaker (de kern)**: stopt de héle dag na **3 verliezen op rij** of een
   **dagverlies ≥ 3%**, en max **20 trades/dag**. Mechanisch — net als `scripts/risk_guard.py`.
8. **Risk-sizing**: elke trade riskeert een vast **% van je balans** (default 0,5%), lotgrootte
   volgt automatisch uit de ATR-stopafstand. Geen martingale, geen averaging-down, altijd een SL.

## Installeren & draaien

1. cTrader → **Automate** → **New cBot** → plak `strategies/XauScalper.cs` → **Build**.
2. Open een **XAUUSD**-chart (M1 of M5 aanrader), sleep de cBot erop.
3. Zet parameters (of laat default), kies **instance** → **Backtest**-tab.

## Backtesten & optimaliseren — de juiste manier

1. **Data**: kies **Tick data** (of m1) voor XAUUSD, minimaal 6–12 maanden, inclusief nieuws-
   periodes. Zet realistische **commissie + spread** aan (belangrijk bij goud!).
2. **Optimaliseer** op **Net Profit** of **Profit Factor** met **Max Drawdown** als grens —
   niet op win rate. Vary: `SL = ATR x`, `Reward:Risk`, `Entry EMA`, `RSI`-drempels, sessie.
3. **Walk-forward**: optimaliseer op periode A, test out-of-sample op periode B. Als 't daar
   instort → overfit, niet gebruiken.
4. **Reality-check**: profit factor > 1,3 én drawdown die je aankunt, over meerdere jaren en
   markttypes. Anders bijstellen of niet live.

## Naar live — voorzichtig, gefaseerd

1. **Demo eerst** (weken), vergelijk of live fills/spreads matchen met de backtest.
2. Dan **klein live**: `Risk % per trade` op 0,25–0,5%, laat de **breaker** aanstaan.
3. Schaal pas op ná bewezen positieve expectancy op je échte account.

## Eerlijke verwachting

Geen enkele retail-bot is "gegarandeerd 90% win" — wie dat verkoopt, liegt of blaast op.
Deze bot is gebouwd om een **positieve verwachting met beheerst risico** te hebben en te
**stoppen als het misgaat**. De rest is jouw werk: backtesten, valideren, klein beginnen.
Echte HFT (microseconden, colocatie) kan een particulier sowieso niet — dit is een snelle
intraday-scalper, wat wél haalbaar is.

## XauFlow — tick-order-flow / volume-structuur ("HFT-achtig")

Reageert op **elke tick** en leest **volume-structuur**: order-book-imbalance (DOM, mits je
broker die levert — anders automatische fallback op tick-volume + micro-momentum), een
**volume-burst**-filter en snel micro-momentum, trend-mee met een snelle EMA. Minieme ATR-stop
(0,8×ATR), RR ~1,2, cooldown tegen overtrading. **Eerlijk:** dit is géén echte HFT (dat kan
retail niet — microseconden/colocatie/L2 zijn bank-terrein); het is de snelste haalbare
order-flow-scalper. Backtest **met tick-data** en realistische spread, anders is het resultaat
fictie. Werkt het best op een lage-spread ECN-goud-feed.

## XauBreakout — Donchian/range-breakout + volume

Koopt de **uitbraak** van een N-bar-kanaal (hoogste high / laagste low) mits bevestigd door een
**volume-burst** en (optioneel) mee met de HTF-trend. Default plaatst hij **stop-orders** net
boven/onder het kanaal zodat je op de break zelf in zit (intrabar), met order-expiry. Breakouts
hebben een **lagere win rate maar grotere winnaars** — mik op RR ≥ 2 en expectancy, niet op win%.

---

## Broker-presets (The5ers & FP Markets)

### The5ers (funded — cTrader of MT5)
- **ALLEEN `XauScalper` en `XauBreakout`.** `XauFlow` NIET — The5ers verbiedt **HFT/tick-scalping**;
  die bot kan je account breachen/bannen.
- Zet de **breaker onder** hún limiet (met marge), en zet de **totaal-DD-halt** aan:

  | Programma | firma dag-DD | firma totaal-DD | `Daily loss limit %` | `Max TOTAL DD %` | `Risk %` |
  |---|---|---|---|---|---|
  | Hyper Growth | 3% | 6% static | **2.0** | **4.5** | 0.25–0.5 |
  | High Stakes | 4% | 6% max | **2.5** | **4.5** | 0.25–0.5 |
  | Bootcamp (trailing DD) | — | trailing | **2.0** | **3.5** | **0.25** |

  De bot-halts staan bewust **strakker** dan de firma-limiet zodat je nooit tegen hún grens
  aanloopt. `Max consec losses/day` = 2–3. **Let op:** de totaal-DD-halt rekent vanaf de
  startbalans van de run (static). Bootcamp gebruikt *trailing* DD — houd 'm daar extra klein
  en monitor zelf mee; de bot kent jouw high-water-trailing niet.

### FP Markets demo (cTrader, raw ECN)
- **Alle drie** mogen hier — dit is je **testomgeving**, inclusief `XauFlow` (raw ECN heeft een
  order-book/DOM en lage spread → order-flow werkt hier het best).
- `Max TOTAL DD %` = **0** (uit) op de demo; `Daily loss limit %` 3, `Risk %` 0.5 om vrij te testen.
- Check de **live spread** op XAUUSD (raw-account, in pips = `(Ask-Bid)/PipSize`) en zet
  `Max spread` ~2× de gemiddelde rustige spread. Bij nieuws spuit gold-spread omhoog — de guard
  slaat die trades dan over.

**Werkvolgorde:** eerst álles op de **FP Markets demo** backtesten + forward-testen (weken),
pas wat bewezen werkt op **The5ers** zetten (zonder XauFlow), met de presets hierboven.

---

> Let op: `.cs`-cBots draaien in cTrader zelf (C#), niet in deze repo-omgeving. De repo bewaart
> de broncode + deze uitleg; compileren en backtesten doe je in cTrader Automate.
