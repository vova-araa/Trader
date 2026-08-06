using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

// XauScalper — disciplinaire XAUUSD-momentum-scalper voor cTrader Automate (cBot).
//
// FILOSOFIE (lees dit vóór je 'm aanzet):
//   Dit is GEEN "90% win"-martingale. Zo'n bot haalt een hoge win rate met een brede stop
//   + kleine TP en blaast op de eerste losers je hele account op — precies de -551-week.
//   Wat telt is EXPECTANCY en PROFIT FACTOR, niet win rate. Deze bot is gebouwd om een
//   POSITIEVE verwachting te hebben met beheerst risico, en om te STOPPEN als het misgaat.
//
// EDGE-COMPONENTEN:
//   1. HTF-trendfilter (H1 EMA fast/slow): alleen trades MÉT de hogere-tijdframe-trend.
//   2. Entry-trigger: pullback naar de fast-EMA op de chart-TF + momentum-resume (RSI),
//      in de trendrichting. Geen counter-trend, geen midden-van-nergens.
//   3. ATR-stops: SL = ATR*mult, TP = SL*RR. Volatiliteit bepaalt de stop, geen vaste pips.
//   4. Spread-guard: sla trades over als de goud-spread te wijd staat (killt scalp-edge).
//   5. Sessie-filter: alleen in de liquide uren (default 07-20 UTC = Londen+NY).
//   6. Break-even + ATR-trailing: winst beschermen, laten lopen.
//   7. CIRCUIT BREAKER (kern): stop de hele dag na N verliezen op rij of een dag-verlies%.
//      Zelfde idee als scripts/risk_guard.py — mechanisch, niet afhankelijk van discipline.
//
// GEBRUIK: cTrader -> Automate -> nieuwe cBot -> plak deze code -> Build.
//   Backtest+optimaliseer op ECHTE XAUUSD-data (Ticks/M1), demo eerst, dan pas klein live.
//   Optimaliseer op NET PROFIT / PROFIT FACTOR / MAX DRAWDOWN — NIET op win rate alleen.

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC, AddIndicators = true)]
    public class XauScalper : Robot
    {
        // ---------- Trend / entry ----------
        [Parameter("HTF trend timeframe", Group = "Trend", DefaultValue = "Hour")]
        public TimeFrame HtfTimeFrame { get; set; }
        [Parameter("HTF EMA fast", Group = "Trend", DefaultValue = 21, MinValue = 3)]
        public int HtfFast { get; set; }
        [Parameter("HTF EMA slow", Group = "Trend", DefaultValue = 55, MinValue = 5)]
        public int HtfSlow { get; set; }
        [Parameter("Entry EMA (pullback)", Group = "Trend", DefaultValue = 20, MinValue = 3)]
        public int EntryEma { get; set; }
        [Parameter("RSI period", Group = "Trend", DefaultValue = 14, MinValue = 2)]
        public int RsiPeriod { get; set; }
        [Parameter("RSI long-min", Group = "Trend", DefaultValue = 50, MinValue = 1, MaxValue = 99)]
        public int RsiLongMin { get; set; }
        [Parameter("RSI short-max", Group = "Trend", DefaultValue = 50, MinValue = 1, MaxValue = 99)]
        public int RsiShortMax { get; set; }

        // ---------- Risk / exits ----------
        [Parameter("Risk % per trade", Group = "Risk", DefaultValue = 0.5, MinValue = 0.05, MaxValue = 3)]
        public double RiskPercent { get; set; }
        [Parameter("ATR period", Group = "Risk", DefaultValue = 14, MinValue = 2)]
        public int AtrPeriod { get; set; }
        [Parameter("SL = ATR x", Group = "Risk", DefaultValue = 1.5, MinValue = 0.3)]
        public double SlAtrMult { get; set; }
        [Parameter("Reward:Risk (TP)", Group = "Risk", DefaultValue = 1.4, MinValue = 0.5)]
        public double RewardRatio { get; set; }
        [Parameter("Break-even at ATR x", Group = "Risk", DefaultValue = 1.0, MinValue = 0.1)]
        public double BreakEvenAtr { get; set; }
        [Parameter("Trail at ATR x (0=off)", Group = "Risk", DefaultValue = 1.5, MinValue = 0)]
        public double TrailAtr { get; set; }

        // ---------- Filters ----------
        [Parameter("Max spread (pips)", Group = "Filters", DefaultValue = 30, MinValue = 1)]
        public double MaxSpreadPips { get; set; }
        [Parameter("Session start (UTC hr)", Group = "Filters", DefaultValue = 7, MinValue = 0, MaxValue = 23)]
        public int SessionStart { get; set; }
        [Parameter("Session end (UTC hr)", Group = "Filters", DefaultValue = 20, MinValue = 0, MaxValue = 24)]
        public int SessionEnd { get; set; }

        // ---------- Circuit breaker (risk_guard-parallel) ----------
        [Parameter("Max consec losses/day", Group = "Breaker", DefaultValue = 3, MinValue = 1)]
        public int MaxConsecLosses { get; set; }
        [Parameter("Daily loss limit %", Group = "Breaker", DefaultValue = 3.0, MinValue = 0.5)]
        public double DailyLossLimitPct { get; set; }
        [Parameter("Max trades/day", Group = "Breaker", DefaultValue = 20, MinValue = 1)]
        public int MaxTradesPerDay { get; set; }
        [Parameter("Max TOTAL DD % (0=off, prop!)", Group = "Breaker", DefaultValue = 0, MinValue = 0)]
        public double MaxTotalDdPct { get; set; }

        private const string Label = "XauScalper";
        private Bars _htf;
        private MovingAverage _htfFast, _htfSlow, _entryEma;
        private RelativeStrengthIndex _rsi;
        private AverageTrueRange _atr;

        private DateTime _day;
        private int _consecLosses, _tradesToday;
        private double _dayStartBalance, _initialBalance;
        private bool _halted, _deadForRun;

        protected override void OnStart()
        {
            _htf = MarketData.GetBars(HtfTimeFrame);
            _htfFast = Indicators.MovingAverage(_htf.ClosePrices, HtfFast, MovingAverageType.Exponential);
            _htfSlow = Indicators.MovingAverage(_htf.ClosePrices, HtfSlow, MovingAverageType.Exponential);
            _entryEma = Indicators.MovingAverage(Bars.ClosePrices, EntryEma, MovingAverageType.Exponential);
            _rsi = Indicators.RelativeStrengthIndex(Bars.ClosePrices, RsiPeriod);
            _atr = Indicators.AverageTrueRange(AtrPeriod, MovingAverageType.Exponential);

            Positions.Closed += OnClosed;
            _initialBalance = Account.Balance;
            ResetDay();
            Print("XauScalper gestart. Risk {0}% | SL {1}xATR | RR {2} | breaker {3} losses / {4}% dag / totaal-DD {5}%",
                  RiskPercent, SlAtrMult, RewardRatio, MaxConsecLosses, DailyLossLimitPct, MaxTotalDdPct);
        }

        // Signalen op bar-close; management (BE/trailing) op elke tick.
        protected override void OnBar()
        {
            RollDayIfNeeded();
            if (_deadForRun) return;   // totaal-DD-halt (prop): geldt over alle dagen
            if (_halted) return;
            if (!InSession()) return;
            if (SpreadPips() > MaxSpreadPips) return;
            if (_tradesToday >= MaxTradesPerDay) return;
            if (Positions.Any(p => p.Label == Label && p.SymbolName == SymbolName)) return; // 1 tegelijk

            int dir = HtfTrend();            // +1 bullish, -1 bearish, 0 geen trend
            if (dir == 0) return;

            double close = Bars.ClosePrices.Last(1);
            double ema = _entryEma.Result.Last(1);
            double rsi = _rsi.Result.Last(1);
            double atr = _atr.Result.Last(1);
            if (atr <= 0) return;

            // Long: bullish HTF + pullback naar/onder de EMA die weer boven sluit + momentum.
            bool longSig = dir > 0
                           && Bars.LowPrices.Last(1) <= ema
                           && close > ema
                           && rsi >= RsiLongMin;
            // Short: spiegelbeeld.
            bool shortSig = dir < 0
                            && Bars.HighPrices.Last(1) >= ema
                            && close < ema
                            && rsi <= RsiShortMax;

            if (longSig) Enter(TradeType.Buy, atr);
            else if (shortSig) Enter(TradeType.Sell, atr);
        }

        protected override void OnTick()
        {
            ManageOpen();
        }

        // ---------- Entries ----------
        private void Enter(TradeType side, double atr)
        {
            double slPrice = atr * SlAtrMult;                 // stopafstand in prijs
            double slPips = slPrice / Symbol.PipSize;
            double tpPips = slPips * RewardRatio;
            double volume = SizeByRisk(slPips);
            if (volume < Symbol.VolumeInUnitsMin) return;

            var r = ExecuteMarketOrder(side, SymbolName, volume, Label, slPips, tpPips);
            if (r.IsSuccessful)
            {
                _tradesToday++;
                Print("{0} @ {1} | SL {2:0.0}p TP {3:0.0}p | vol {4} | trade #{5} vandaag",
                      side, r.Position.EntryPrice, slPips, tpPips, volume, _tradesToday);
            }
            else
                Print("Order faalde: {0}", r.Error);
        }

        private double SizeByRisk(double slPips)
        {
            double riskAmount = Account.Balance * (RiskPercent / 100.0);
            double perPipPerUnit = Symbol.PipValue;           // waarde 1 pip / 1 unit, account-valuta
            if (perPipPerUnit <= 0 || slPips <= 0) return 0;
            double volume = riskAmount / (slPips * perPipPerUnit);
            return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);
        }

        // ---------- Management: break-even + ATR-trailing ----------
        private void ManageOpen()
        {
            double atr = _atr.Result.LastValue;
            foreach (var p in Positions)
            {
                if (p.Label != Label || p.SymbolName != SymbolName) continue;
                bool isLong = p.TradeType == TradeType.Buy;
                double price = isLong ? Symbol.Bid : Symbol.Ask;
                double moved = isLong ? price - p.EntryPrice : p.EntryPrice - price;

                // Break-even zodra prijs BreakEvenAtr*ATR meeloopt.
                if (BreakEvenAtr > 0 && moved >= atr * BreakEvenAtr)
                {
                    double be = isLong ? p.EntryPrice + Symbol.PipSize : p.EntryPrice - Symbol.PipSize;
                    if (!p.StopLoss.HasValue || (isLong ? p.StopLoss.Value < be : p.StopLoss.Value > be))
                        ModifyPositionSafe(p, be);
                }
                // ATR-trailing daarna.
                if (TrailAtr > 0 && moved >= atr * TrailAtr)
                {
                    double trail = isLong ? price - atr * TrailAtr : price + atr * TrailAtr;
                    if (!p.StopLoss.HasValue || (isLong ? trail > p.StopLoss.Value : trail < p.StopLoss.Value))
                        ModifyPositionSafe(p, trail);
                }
            }
        }

        private void ModifyPositionSafe(Position p, double sl)
        {
            try { ModifyPosition(p, sl, p.TakeProfit); }
            catch (Exception e) { Print("ModifyPosition faalde: {0}", e.Message); }
        }

        // ---------- Circuit breaker ----------
        private void OnClosed(PositionClosedEventArgs args)
        {
            var p = args.Position;
            if (p.Label != Label) return;
            if (p.NetProfit < 0) _consecLosses++;
            else if (p.NetProfit > 0) _consecLosses = 0;

            double dayPnl = Account.Balance - _dayStartBalance;
            double lossLimit = -_dayStartBalance * (DailyLossLimitPct / 100.0);

            if (_consecLosses >= MaxConsecLosses)
            {
                _halted = true;
                Print("RISICO-HALT: {0} verliezen op rij — geen nieuwe trades vandaag.", _consecLosses);
            }
            if (dayPnl <= lossLimit)
            {
                _halted = true;
                Print("RISICO-HALT: dagverlies {0:0.00} <= limiet {1:0.00} — stop voor vandaag.", dayPnl, lossLimit);
            }
            if (MaxTotalDdPct > 0 && Account.Balance <= _initialBalance * (1 - MaxTotalDdPct / 100.0))
            {
                _deadForRun = true; _halted = true;
                Print("TOTAAL-DD-HALT: balans {0:0.00} <= start {1:0.00} -{2}% — bot stopt (prop-bescherming).",
                      Account.Balance, _initialBalance, MaxTotalDdPct);
            }
        }

        // ---------- Helpers ----------
        private int HtfTrend()
        {
            double f = _htfFast.Result.LastValue, s = _htfSlow.Result.LastValue;
            if (f > s) return 1;
            if (f < s) return -1;
            return 0;
        }

        private bool InSession()
        {
            int h = Server.Time.Hour;
            return SessionStart <= SessionEnd
                ? (h >= SessionStart && h < SessionEnd)
                : (h >= SessionStart || h < SessionEnd);  // sessie over middernacht
        }

        private double SpreadPips() => (Symbol.Ask - Symbol.Bid) / Symbol.PipSize;

        private void RollDayIfNeeded()
        {
            if (Server.Time.Date != _day) ResetDay();
        }

        private void ResetDay()
        {
            _day = Server.Time.Date;
            _consecLosses = 0;
            _tradesToday = 0;
            _dayStartBalance = Account.Balance;
            _halted = false;
        }
    }
}
