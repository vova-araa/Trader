using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

// XauEdge — de FLAGSHIP XAUUSD-bot: zo simpel mogelijk, expres. (cTrader Automate)
//
// WAAROM SIMPEL = "ZIEKST":
//   Onderzoek is eenduidig: minder parameters = robuuster; complexe/overfit bots scoren
//   mooi in de backtest en sterven live. Deze bot heeft één heldere edge en het minimum
//   aantal knoppen, zodat wat je in de backtest ziet ook out-of-sample standhoudt.
//
// DE EDGE (één ding, goed):
//   Trend-momentum. Handel ALLEEN mee met de hogere-tijdframe-trend (H1 EMA), en stap in op
//   een MOMENTUM-BREAKOUT: sluit de bar boven de hoogste high van de laatste N bars (long) /
//   onder de laagste low (short), in de trendrichting. Geen counter-trend, geen ruis-signalen.
//
// RISICO (niet-onderhandelbaar, zelfde scaffolding als de andere bots + risk_guard.py):
//   %-risk sizing, ATR-stop, vaste RR-TP, break-even + ATR-trailing, spread- & sessie-filter,
//   dag-circuit-breaker (verliesreeks + dagverlies) EN totaal-DD-halt (prop-bescherming).
//   Geen martingale, geen grid, altijd een harde stop.
//
// GEBRUIK: cTrader Automate -> plak -> Build -> XAUUSD M15 (of M5). Backtest volgens
//   docs/XAUEDGE.md (tick-data, walk-forward, Monte Carlo) — dat proces laat 'm slagen,
//   niet het sleutelen aan de code.

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC, AddIndicators = true)]
    public class XauEdge : Robot
    {
        // ---- De strategie: 5 knoppen, meer niet ----
        [Parameter("HTF trend EMA", Group = "Edge", DefaultValue = 50, MinValue = 5)]
        public int TrendEma { get; set; }
        [Parameter("HTF timeframe", Group = "Edge", DefaultValue = "Hour")]
        public TimeFrame HtfTf { get; set; }
        [Parameter("Breakout bars", Group = "Edge", DefaultValue = 20, MinValue = 3)]
        public int BreakoutBars { get; set; }
        [Parameter("SL = ATR x", Group = "Edge", DefaultValue = 1.5, MinValue = 0.3)]
        public double AtrMult { get; set; }
        [Parameter("Reward:Risk", Group = "Edge", DefaultValue = 1.8, MinValue = 0.5)]
        public double RR { get; set; }

        // ---- Risico ----
        [Parameter("Risk % per trade", Group = "Risk", DefaultValue = 0.5, MinValue = 0.05, MaxValue = 2)]
        public double RiskPct { get; set; }
        [Parameter("Trail at ATR x (0=off)", Group = "Risk", DefaultValue = 1.5, MinValue = 0)]
        public double TrailAtr { get; set; }

        // ---- Veiligheid ----
        [Parameter("Max spread (pips)", Group = "Safety", DefaultValue = 30, MinValue = 1)]
        public double MaxSpread { get; set; }
        [Parameter("Session start UTC", Group = "Safety", DefaultValue = 7, MinValue = 0, MaxValue = 23)]
        public int SessStart { get; set; }
        [Parameter("Session end UTC", Group = "Safety", DefaultValue = 20, MinValue = 0, MaxValue = 24)]
        public int SessEnd { get; set; }
        [Parameter("Daily loss % (0=off)", Group = "Safety", DefaultValue = 2.0, MinValue = 0)]
        public double DailyLossPct { get; set; }
        [Parameter("Max consec losses (0=off)", Group = "Safety", DefaultValue = 3, MinValue = 0)]
        public int MaxConsecLosses { get; set; }
        [Parameter("Max TOTAL DD % (0=off)", Group = "Safety", DefaultValue = 0, MinValue = 0)]
        public double MaxTotalDdPct { get; set; }

        private const string Label = "XauEdge";
        private Bars _htf;
        private MovingAverage _trend;
        private AverageTrueRange _atr;
        private DateTime _day;
        private int _consec;
        private double _dayStart, _initBal;
        private bool _haltDay, _haltRun;

        protected override void OnStart()
        {
            _htf = MarketData.GetBars(HtfTf);
            _trend = Indicators.MovingAverage(_htf.ClosePrices, TrendEma, MovingAverageType.Exponential);
            _atr = Indicators.AverageTrueRange(14, MovingAverageType.Exponential);
            Positions.Closed += OnClosed;
            _initBal = Account.Balance;
            NewDay();
            Print("XauEdge: trend H1-EMA{0} | breakout {1} bars | SL {2}xATR | RR {3} | risk {4}%",
                  TrendEma, BreakoutBars, AtrMult, RR, RiskPct);
        }

        protected override void OnBar()
        {
            if (Server.Time.Date != _day) NewDay();
            Trail();
            if (_haltRun || _haltDay) return;
            if (Server.Time.Hour < SessStart || Server.Time.Hour >= SessEnd) return;
            if ((Symbol.Ask - Symbol.Bid) / Symbol.PipSize > MaxSpread) return;
            if (Positions.Any(p => p.Label == Label && p.SymbolName == SymbolName)) return;

            int trend = _htf.ClosePrices.LastValue > _trend.Result.LastValue ? 1
                      : _htf.ClosePrices.LastValue < _trend.Result.LastValue ? -1 : 0;
            if (trend == 0 || Bars.Count < BreakoutBars + 2) return;

            double atr = _atr.Result.Last(1);
            if (atr <= 0) return;

            // hoogste high / laagste low over de vorige BreakoutBars (excl. de zojuist gesloten bar)
            double hi = double.MinValue, lo = double.MaxValue;
            for (int i = 2; i <= BreakoutBars + 1; i++)
            {
                hi = Math.Max(hi, Bars.HighPrices.Last(i));
                lo = Math.Min(lo, Bars.LowPrices.Last(i));
            }
            double close = Bars.ClosePrices.Last(1);

            if (trend > 0 && close > hi) Enter(TradeType.Buy, atr);
            else if (trend < 0 && close < lo) Enter(TradeType.Sell, atr);
        }

        private void Enter(TradeType side, double atr)
        {
            double slPips = (atr * AtrMult) / Symbol.PipSize;
            double tpPips = slPips * RR;
            double risk = Account.Balance * (RiskPct / 100.0);
            if (Symbol.PipValue <= 0 || slPips <= 0) return;
            double vol = Symbol.NormalizeVolumeInUnits(risk / (slPips * Symbol.PipValue), RoundingMode.Down);
            if (vol < Symbol.VolumeInUnitsMin) return;
            // Robuuste entry: synchroon, IsSuccessful-check + 1 retry, alles in try/catch.
            // (cTrader's fault-tolerance negeert veel fouten en laat de bot dóórlopen -> zelf afvangen.)
            for (int attempt = 1; attempt <= 2; attempt++)
            {
                try
                {
                    var r = ExecuteMarketOrder(side, SymbolName, vol, Label, slPips, tpPips);
                    if (r.IsSuccessful)
                    {
                        Print("{0} @ {1} | SL {2:0.0}p TP {3:0.0}p", side, r.Position.EntryPrice, slPips, tpPips);
                        return;
                    }
                    Print("Entry mislukt (poging {0}): {1}", attempt, r.Error);
                }
                catch (Exception ex) { Print("Entry-exceptie (poging {0}): {1}", attempt, ex.Message); }
            }
        }

        private void Trail()
        {
            if (TrailAtr <= 0) return;
            double atr = _atr.Result.LastValue;
            foreach (var p in Positions)
            {
                if (p.Label != Label || p.SymbolName != SymbolName) continue;
                bool lng = p.TradeType == TradeType.Buy;
                double price = lng ? Symbol.Bid : Symbol.Ask;
                if ((lng ? price - p.EntryPrice : p.EntryPrice - price) < atr * TrailAtr) continue;
                double sl = lng ? price - atr * TrailAtr : price + atr * TrailAtr;
                if (!p.StopLoss.HasValue || (lng ? sl > p.StopLoss.Value : sl < p.StopLoss.Value))
                    try { ModifyPosition(p, sl, p.TakeProfit); } catch { }
            }
        }

        private void OnClosed(PositionClosedEventArgs a)
        {
            if (a.Position.Label != Label) return;
            if (a.Position.NetProfit < 0) _consec++; else if (a.Position.NetProfit > 0) _consec = 0;
            double dayPnl = Account.Balance - _dayStart;
            if (MaxConsecLosses > 0 && _consec >= MaxConsecLosses) { _haltDay = true; Print("HALT dag: {0} losses op rij.", _consec); }
            if (DailyLossPct > 0 && dayPnl <= -_dayStart * (DailyLossPct / 100.0)) { _haltDay = true; Print("HALT dag: verlies {0:0.00}.", dayPnl); }
            if (MaxTotalDdPct > 0 && Account.Balance <= _initBal * (1 - MaxTotalDdPct / 100.0)) { _haltRun = true; Print("HALT totaal-DD -{0}% (prop).", MaxTotalDdPct); }
        }

        private void NewDay()
        {
            _day = Server.Time.Date; _consec = 0; _dayStart = Account.Balance; _haltDay = false;
        }

        // Last-resort vangnet: cTrader negeert veel fouten en laat de bot dóórlopen. Bij een
        // exceptie die hier landt: stop nieuwe entries (bestaande posities houden hun server-side
        // SL/TP). Staat NIET in de default template -> bewust toegevoegd.
        protected override void OnException(Exception exception)
        {
            _haltRun = true;
            Print("OnException -> nieuwe entries gestopt (SL/TP blijven server-side): {0}", exception.Message);
        }
    }
}
