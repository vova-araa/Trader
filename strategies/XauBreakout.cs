using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

// XauBreakout — Donchian/range-breakout bot voor XAUUSD (cTrader Automate), met volume-
// bevestiging en optionele stop-order-entry op het break-niveau.
//
// IDEE:
//   Goud maakt scherpe expansie-moves uit consolidatie. Deze bot koopt de UITBRAAK van een
//   N-bar-kanaal (hoogste high / laagste low) mits die break wordt bevestigd door VOLUME
//   (tick-volume-burst) en — optioneel — mee is met de HTF-trend. Breakouts hebben een LAGERE
//   win rate maar GROTERE winnaars; verwacht dus geen 90% wins, mik op RR >= 2 en expectancy.
//
// TWEE ENTRY-MODI:
//   - Stop-order (default): plaatst een BUY-STOP net boven het kanaal (en SELL-STOP eronder),
//     zodat je exact op de break in zit — intrabar, niet pas op bar-close.
//   - Market-on-close: als de afgeronde bar buiten het kanaal sluit -> markt-order.
//
// RISICO: %-risk sizing, ATR-stop, TP = RR*SL, spread-guard, sessie-filter, break-even +
//   ATR-trailing, en de in-bot CIRCUIT BREAKER (consec-loss + dagverlies + max trades) —
//   zelfde idee als risk_guard.py. Geen martingale, altijd een stop.
//
// GEBRUIK: plak in cTrader Automate -> Build -> XAUUSD M5/M15. Backtest op tick/m1-data met
//   echte spread/commissie; optimaliseer op Net Profit / Profit Factor / Drawdown.

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC, AddIndicators = true)]
    public class XauBreakout : Robot
    {
        [Parameter("Channel bars (Donchian)", Group = "Breakout", DefaultValue = 40, MinValue = 5)]
        public int ChannelBars { get; set; }
        [Parameter("Buffer (pips)", Group = "Breakout", DefaultValue = 5, MinValue = 0)]
        public double BufferPips { get; set; }
        [Parameter("Use stop-orders", Group = "Breakout", DefaultValue = true)]
        public bool UseStopOrders { get; set; }
        [Parameter("Volume-confirm x avg", Group = "Breakout", DefaultValue = 1.5, MinValue = 1.0)]
        public double VolConfirmMult { get; set; }
        [Parameter("Vol-avg bars", Group = "Breakout", DefaultValue = 20, MinValue = 3)]
        public int VolAvgBars { get; set; }
        [Parameter("Use HTF trend filter", Group = "Breakout", DefaultValue = true)]
        public bool UseHtfFilter { get; set; }
        [Parameter("HTF timeframe", Group = "Breakout", DefaultValue = "Hour")]
        public TimeFrame HtfTimeFrame { get; set; }
        [Parameter("HTF EMA", Group = "Breakout", DefaultValue = 50, MinValue = 5)]
        public int HtfEma { get; set; }
        [Parameter("Order expiry (bars)", Group = "Breakout", DefaultValue = 3, MinValue = 1)]
        public int OrderExpiryBars { get; set; }

        [Parameter("Risk % per trade", Group = "Risk", DefaultValue = 0.5, MinValue = 0.05, MaxValue = 3)]
        public double RiskPercent { get; set; }
        [Parameter("ATR period", Group = "Risk", DefaultValue = 14, MinValue = 2)]
        public int AtrPeriod { get; set; }
        [Parameter("SL = ATR x", Group = "Risk", DefaultValue = 1.5, MinValue = 0.3)]
        public double SlAtrMult { get; set; }
        [Parameter("Reward:Risk (TP)", Group = "Risk", DefaultValue = 2.0, MinValue = 0.5)]
        public double RewardRatio { get; set; }
        [Parameter("Break-even at ATR x", Group = "Risk", DefaultValue = 1.0, MinValue = 0.1)]
        public double BreakEvenAtr { get; set; }
        [Parameter("Trail at ATR x (0=off)", Group = "Risk", DefaultValue = 2.0, MinValue = 0)]
        public double TrailAtr { get; set; }

        [Parameter("Max spread (pips)", Group = "Filters", DefaultValue = 30, MinValue = 1)]
        public double MaxSpreadPips { get; set; }
        [Parameter("Session start (UTC hr)", Group = "Filters", DefaultValue = 7, MinValue = 0, MaxValue = 23)]
        public int SessionStart { get; set; }
        [Parameter("Session end (UTC hr)", Group = "Filters", DefaultValue = 20, MinValue = 0, MaxValue = 24)]
        public int SessionEnd { get; set; }

        [Parameter("Max consec losses/day", Group = "Breaker", DefaultValue = 3, MinValue = 1)]
        public int MaxConsecLosses { get; set; }
        [Parameter("Daily loss limit %", Group = "Breaker", DefaultValue = 3.0, MinValue = 0.5)]
        public double DailyLossLimitPct { get; set; }
        [Parameter("Max trades/day", Group = "Breaker", DefaultValue = 10, MinValue = 1)]
        public int MaxTradesPerDay { get; set; }

        private const string Label = "XauBreakout";
        private AverageTrueRange _atr;
        private Bars _htf;
        private MovingAverage _htfEma;

        private DateTime _day;
        private int _consecLosses, _tradesToday;
        private double _dayStartBalance;
        private bool _halted;

        protected override void OnStart()
        {
            _atr = Indicators.AverageTrueRange(AtrPeriod, MovingAverageType.Exponential);
            if (UseHtfFilter)
            {
                _htf = MarketData.GetBars(HtfTimeFrame);
                _htfEma = Indicators.MovingAverage(_htf.ClosePrices, HtfEma, MovingAverageType.Exponential);
            }
            Positions.Closed += OnClosed;
            ResetDay();
            Print("XauBreakout gestart. Kanaal {0} bars | {1} | RR {2} | vol x{3}",
                  ChannelBars, UseStopOrders ? "stop-orders" : "market-close", RewardRatio, VolConfirmMult);
        }

        protected override void OnBar()
        {
            RollDayIfNeeded();
            ManageOpen();
            if (_halted) return;
            if (!InSession()) return;
            if (SpreadPips() > MaxSpreadPips) return;
            if (_tradesToday >= MaxTradesPerDay) return;
            if (Positions.Any(p => p.Label == Label && p.SymbolName == SymbolName)) return;
            if (PendingOrders.Any(o => o.Label == Label)) return;   // niet stapelen

            double atr = _atr.Result.Last(1);
            if (atr <= 0 || Bars.Count < ChannelBars + 2) return;
            if (!VolumeConfirm()) return;

            // Kanaal over de vorige ChannelBars (exclusief de zojuist afgeronde bar).
            double hi = double.MinValue, lo = double.MaxValue;
            for (int i = 2; i <= ChannelBars + 1; i++)
            {
                hi = Math.Max(hi, Bars.HighPrices.Last(i));
                lo = Math.Min(lo, Bars.LowPrices.Last(i));
            }
            double buf = BufferPips * Symbol.PipSize;
            double upLevel = hi + buf, dnLevel = lo - buf;
            int trend = HtfTrend();                    // +1/-1/0 (0 = filter uit of vlak)

            double slPips = (atr * SlAtrMult) / Symbol.PipSize;
            double tpPips = slPips * RewardRatio;
            DateTime expiry = Server.Time.AddSeconds(OrderExpiryBars * BarSeconds());

            if (UseStopOrders)
            {
                if (trend >= 0) PlaceStop(TradeType.Buy, upLevel, slPips, tpPips, expiry);
                if (trend <= 0) PlaceStop(TradeType.Sell, dnLevel, slPips, tpPips, expiry);
            }
            else
            {
                double close = Bars.ClosePrices.Last(1);
                if (trend >= 0 && close > upLevel) Market(TradeType.Buy, slPips, tpPips);
                else if (trend <= 0 && close < dnLevel) Market(TradeType.Sell, slPips, tpPips);
            }
        }

        // ---------- Volume / trend ----------
        private bool VolumeConfirm()
        {
            int n = Math.Min(VolAvgBars, Bars.Count - 2);
            if (n < 2) return true;
            double sum = 0;
            for (int i = 2; i <= n + 1; i++) sum += Bars.TickVolumes.Last(i);
            double avg = sum / n;
            return avg <= 0 || Bars.TickVolumes.Last(1) >= avg * VolConfirmMult;
        }

        private int HtfTrend()
        {
            if (!UseHtfFilter) return 0;
            double price = _htf.ClosePrices.LastValue, ema = _htfEma.Result.LastValue;
            if (price > ema) return 1;
            if (price < ema) return -1;
            return 0;
        }

        // ---------- Orders ----------
        private void PlaceStop(TradeType side, double price, double slPips, double tpPips, DateTime expiry)
        {
            double volume = SizeByRisk(slPips);
            if (volume < Symbol.VolumeInUnitsMin) return;
            PlaceStopOrder(side, SymbolName, volume, price, Label, slPips, tpPips, expiry);
            _tradesToday++;
            Print("STOP {0} @ {1:0.00} | SL {2:0.0}p TP {3:0.0}p | #{4}", side, price, slPips, tpPips, _tradesToday);
        }

        private void Market(TradeType side, double slPips, double tpPips)
        {
            double volume = SizeByRisk(slPips);
            if (volume < Symbol.VolumeInUnitsMin) return;
            var r = ExecuteMarketOrder(side, SymbolName, volume, Label, slPips, tpPips);
            if (r.IsSuccessful) { _tradesToday++; Print("BREAKOUT {0} @ {1} | #{2}", side, r.Position.EntryPrice, _tradesToday); }
        }

        private double SizeByRisk(double slPips)
        {
            double risk = Account.Balance * (RiskPercent / 100.0);
            if (Symbol.PipValue <= 0 || slPips <= 0) return 0;
            return Symbol.NormalizeVolumeInUnits(risk / (slPips * Symbol.PipValue), RoundingMode.Down);
        }

        // ---------- Management ----------
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
                if (TrailAtr > 0 && moved >= atr * TrailAtr)
                {
                    double trail = isLong ? price - atr * TrailAtr : price + atr * TrailAtr;
                    if (!p.StopLoss.HasValue || (isLong ? trail > p.StopLoss.Value : trail < p.StopLoss.Value))
                        try { ModifyPosition(p, trail, p.TakeProfit); } catch { }
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
        }

        private double BarSeconds()
        {
            // grove bar-duur voor order-expiry; werkt voor minuten/uur-tijdframes
            var span = Bars.OpenTimes.Count > 1
                ? Bars.OpenTimes.LastValue - Bars.OpenTimes.Last(1)
                : TimeSpan.FromMinutes(5);
            return Math.Max(60, span.TotalSeconds);
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
