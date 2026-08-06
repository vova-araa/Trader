using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

// XauFlow — tick-gedreven order-flow / volume-structuur scalper voor XAUUSD (cTrader Automate).
//
// EERLIJK OVER "HFT":
//   Letterlijke HFT (microseconden, colocatie, volledige L2-depth) kan een particulier niet.
//   Dit is het dichtstbijzijnde haalbare: een bot die op ELKE TICK (OnTick) reageert en de
//   VOLUME-STRUCTUUR leest — order-book-imbalance (DOM, als je broker die levert) én
//   tick-volume-bursts + micro-momentum. Snel in/uit, minieme stops, strak gefilterd.
//
// SIGNAAL (long; short = spiegelbeeld):
//   1. Volume-burst: tick-volume van de lopende bar > gemiddelde * VolumeBurstMult.
//   2. Order-flow-imbalance: DOM bid-volume / ask-volume >= ImbalanceRatio
//      (valt automatisch terug op tick-volume-richting als DOM niet beschikbaar is).
//   3. Micro-momentum: mid-prijs is over de laatste LookbackTicks met >= MomentumPips gestegen.
//   4. Trend-mee met een snelle EMA (geen tegendraadse flow-trades).
//   Alles moet kloppen -> markt-order met TP≈RR*SL. Cooldown tegen overtrading.
//
// RISICO: %-risk sizing, harde ATR/tick-stop, spread-guard, sessie-filter, en de in-bot
//   CIRCUIT BREAKER (consec-loss + dagverlies + max trades) — zelfde idee als risk_guard.py.
//   Geen martingale, altijd een stop.
//
// GEBRUIK: plak in cTrader Automate -> Build -> op een XAUUSD M1/tick-chart. Backtest met
//   TICK-data + echte spread/commissie; optimaliseer op Profit Factor/Drawdown, NIET win rate.

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC, AddIndicators = true)]
    public class XauFlow : Robot
    {
        [Parameter("Fast EMA (bias)", Group = "Flow", DefaultValue = 34, MinValue = 3)]
        public int FastEma { get; set; }
        [Parameter("Lookback ticks", Group = "Flow", DefaultValue = 20, MinValue = 3, MaxValue = 500)]
        public int LookbackTicks { get; set; }
        [Parameter("Momentum (pips)", Group = "Flow", DefaultValue = 3.0, MinValue = 0.1)]
        public double MomentumPips { get; set; }
        [Parameter("Volume-burst x avg", Group = "Flow", DefaultValue = 1.8, MinValue = 1.0)]
        public double VolumeBurstMult { get; set; }
        [Parameter("Vol-avg bars", Group = "Flow", DefaultValue = 20, MinValue = 3)]
        public int VolAvgBars { get; set; }
        [Parameter("DOM imbalance ratio", Group = "Flow", DefaultValue = 1.6, MinValue = 1.0)]
        public double ImbalanceRatio { get; set; }
        [Parameter("Cooldown (sec)", Group = "Flow", DefaultValue = 20, MinValue = 0)]
        public int CooldownSec { get; set; }

        [Parameter("Risk % per trade", Group = "Risk", DefaultValue = 0.5, MinValue = 0.05, MaxValue = 3)]
        public double RiskPercent { get; set; }
        [Parameter("ATR period", Group = "Risk", DefaultValue = 14, MinValue = 2)]
        public int AtrPeriod { get; set; }
        [Parameter("SL = ATR x", Group = "Risk", DefaultValue = 0.8, MinValue = 0.2)]
        public double SlAtrMult { get; set; }
        [Parameter("Reward:Risk (TP)", Group = "Risk", DefaultValue = 1.2, MinValue = 0.5)]
        public double RewardRatio { get; set; }
        [Parameter("Break-even at ATR x", Group = "Risk", DefaultValue = 0.7, MinValue = 0.1)]
        public double BreakEvenAtr { get; set; }

        [Parameter("Max spread (pips)", Group = "Filters", DefaultValue = 25, MinValue = 1)]
        public double MaxSpreadPips { get; set; }
        [Parameter("Session start (UTC hr)", Group = "Filters", DefaultValue = 7, MinValue = 0, MaxValue = 23)]
        public int SessionStart { get; set; }
        [Parameter("Session end (UTC hr)", Group = "Filters", DefaultValue = 20, MinValue = 0, MaxValue = 24)]
        public int SessionEnd { get; set; }

        [Parameter("Max consec losses/day", Group = "Breaker", DefaultValue = 3, MinValue = 1)]
        public int MaxConsecLosses { get; set; }
        [Parameter("Daily loss limit %", Group = "Breaker", DefaultValue = 3.0, MinValue = 0.5)]
        public double DailyLossLimitPct { get; set; }
        [Parameter("Max trades/day", Group = "Breaker", DefaultValue = 60, MinValue = 1)]
        public int MaxTradesPerDay { get; set; }
        [Parameter("Max TOTAL DD % (0=off, prop!)", Group = "Breaker", DefaultValue = 0, MinValue = 0)]
        public double MaxTotalDdPct { get; set; }

        private const string Label = "XauFlow";
        private MovingAverage _ema;
        private AverageTrueRange _atr;
        private MarketDepth _dom;

        private double[] _mids;   // ringbuffer met recente mid-prijzen
        private int _midIdx, _midCount;
        private DateTime _day, _lastTradeTime;
        private int _consecLosses, _tradesToday;
        private double _dayStartBalance, _initialBalance;
        private bool _halted, _deadForRun;

        protected override void OnStart()
        {
            _ema = Indicators.MovingAverage(Bars.ClosePrices, FastEma, MovingAverageType.Exponential);
            _atr = Indicators.AverageTrueRange(AtrPeriod, MovingAverageType.Exponential);
            _mids = new double[Math.Max(LookbackTicks + 1, 8)];
            try { _dom = MarketData.GetMarketDepth(Symbol); } catch { _dom = null; }

            Positions.Closed += OnClosed;
            _lastTradeTime = DateTime.MinValue;
            _initialBalance = Account.Balance;
            ResetDay();
            Print("XauFlow gestart. DOM {0} | risk {1}% | SL {2}xATR | RR {3}",
                  _dom != null ? "actief" : "n/b (tick-vol fallback)", RiskPercent, SlAtrMult, RewardRatio);
        }

        protected override void OnTick()
        {
            PushMid((Symbol.Ask + Symbol.Bid) / 2.0);
            ManageOpen();

            RollDayIfNeeded();
            if (_deadForRun) return;   // totaal-DD-halt (prop): geldt over alle dagen
            if (_halted) return;
            if (!InSession()) return;
            if (SpreadPips() > MaxSpreadPips) return;
            if (_tradesToday >= MaxTradesPerDay) return;
            if ((Server.Time - _lastTradeTime).TotalSeconds < CooldownSec) return;
            if (Positions.Any(p => p.Label == Label && p.SymbolName == SymbolName)) return;
            if (_midCount <= LookbackTicks) return;

            double atr = _atr.Result.LastValue;
            if (atr <= 0) return;
            if (!VolumeBurst()) return;

            double mom = MomentumPipsNow();            // + = omhoog, - = omlaag (in pips)
            int flow = FlowImbalance();                // +1 bid-heavy, -1 ask-heavy, 0 neutraal
            double price = Bars.ClosePrices.LastValue;
            bool bias = price > _ema.Result.LastValue; // snelle EMA-bias

            bool longSig = bias && mom >= MomentumPips && flow >= 0;
            bool shortSig = !bias && mom <= -MomentumPips && flow <= 0;

            if (longSig) Enter(TradeType.Buy, atr);
            else if (shortSig) Enter(TradeType.Sell, atr);
        }

        // ---------- Order-flow / volume ----------
        private bool VolumeBurst()
        {
            // gemiddelde tick-volume van de laatste VolAvgBars afgeronde bars
            int n = Math.Min(VolAvgBars, Bars.Count - 1);
            if (n < 2) return true;
            double sum = 0;
            for (int i = 1; i <= n; i++) sum += Bars.TickVolumes.Last(i);
            double avg = sum / n;
            return avg <= 0 || Bars.TickVolumes.LastValue >= avg * VolumeBurstMult;
        }

        private int FlowImbalance()
        {
            // 1) DOM (order-book) indien beschikbaar
            if (_dom != null && _dom.BidEntries != null && _dom.AskEntries != null
                && _dom.BidEntries.Count > 0 && _dom.AskEntries.Count > 0)
            {
                double bid = _dom.BidEntries.Sum(e => e.VolumeInUnits);
                double ask = _dom.AskEntries.Sum(e => e.VolumeInUnits);
                if (ask > 0 && bid / ask >= ImbalanceRatio) return 1;
                if (bid > 0 && ask / bid >= ImbalanceRatio) return -1;
                return 0;
            }
            // 2) Fallback: richting van de laatste tick-volume-toename via micro-momentum-teken
            double mom = MomentumPipsNow();
            return mom > 0 ? 1 : mom < 0 ? -1 : 0;
        }

        private double MomentumPipsNow()
        {
            double now = _mids[Prev(0)];
            double then = _mids[Prev(LookbackTicks)];
            return (now - then) / Symbol.PipSize;
        }

        private void PushMid(double mid)
        {
            _mids[_midIdx] = mid;
            _midIdx = (_midIdx + 1) % _mids.Length;
            if (_midCount < _mids.Length) _midCount++;
        }
        private int Prev(int back) => ((_midIdx - 1 - back) % _mids.Length + _mids.Length) % _mids.Length;

        // ---------- Entries / management ----------
        private void Enter(TradeType side, double atr)
        {
            double slPips = (atr * SlAtrMult) / Symbol.PipSize;
            double tpPips = slPips * RewardRatio;
            double volume = SizeByRisk(slPips);
            if (volume < Symbol.VolumeInUnitsMin) return;

            var r = ExecuteMarketOrder(side, SymbolName, volume, Label, slPips, tpPips);
            if (r.IsSuccessful)
            {
                _tradesToday++;
                _lastTradeTime = Server.Time;
                Print("{0} flow @ {1} | SL {2:0.0}p TP {3:0.0}p | #{4}", side, r.Position.EntryPrice, slPips, tpPips, _tradesToday);
            }
        }

        private double SizeByRisk(double slPips)
        {
            double risk = Account.Balance * (RiskPercent / 100.0);
            if (Symbol.PipValue <= 0 || slPips <= 0) return 0;
            return Symbol.NormalizeVolumeInUnits(risk / (slPips * Symbol.PipValue), RoundingMode.Down);
        }

        private void ManageOpen()
        {
            double atr = _atr.Result.LastValue;
            foreach (var p in Positions)
            {
                if (p.Label != Label || p.SymbolName != SymbolName) continue;
                bool isLong = p.TradeType == TradeType.Buy;
                double price = isLong ? Symbol.Bid : Symbol.Ask;
                double moved = isLong ? price - p.EntryPrice : p.EntryPrice - price;
                if (BreakEvenAtr > 0 && moved >= atr * BreakEvenAtr)
                {
                    double be = isLong ? p.EntryPrice + Symbol.PipSize : p.EntryPrice - Symbol.PipSize;
                    if (!p.StopLoss.HasValue || (isLong ? p.StopLoss.Value < be : p.StopLoss.Value > be))
                        try { ModifyPosition(p, be, p.TakeProfit); } catch { }
                }
            }
        }

        // ---------- Breaker / helpers ----------
        private void OnClosed(PositionClosedEventArgs a)
        {
            if (a.Position.Label != Label) return;
            if (a.Position.NetProfit < 0) _consecLosses++;
            else if (a.Position.NetProfit > 0) _consecLosses = 0;

            double dayPnl = Account.Balance - _dayStartBalance;
            if (_consecLosses >= MaxConsecLosses) { _halted = true; Print("RISICO-HALT: {0} losses op rij.", _consecLosses); }
            if (dayPnl <= -_dayStartBalance * (DailyLossLimitPct / 100.0)) { _halted = true; Print("RISICO-HALT: dagverlies {0:0.00}.", dayPnl); }
            if (MaxTotalDdPct > 0 && Account.Balance <= _initialBalance * (1 - MaxTotalDdPct / 100.0))
            { _deadForRun = true; _halted = true; Print("TOTAAL-DD-HALT: -{0}% vanaf start — bot stopt (prop).", MaxTotalDdPct); }
        }

        private bool InSession()
        {
            int h = Server.Time.Hour;
            return SessionStart <= SessionEnd ? (h >= SessionStart && h < SessionEnd) : (h >= SessionStart || h < SessionEnd);
        }
        private double SpreadPips() => (Symbol.Ask - Symbol.Bid) / Symbol.PipSize;
        private void RollDayIfNeeded() { if (Server.Time.Date != _day) ResetDay(); }
        private void ResetDay()
        {
            _day = Server.Time.Date;
            _consecLosses = 0; _tradesToday = 0; _dayStartBalance = Account.Balance; _halted = false;
        }
    }
}
