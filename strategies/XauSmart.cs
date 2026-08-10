using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

// XauSmart — de "smart money" XAUUSD-bot voor cTrader / FP Markets raw ECN.
//
// WAAROM DEZE BOT (en waarom FP Markets):
//   Dit is de automatisering van precies wat je niet met een simpele MA-bot vangt: waar het
//   grote geld instapt. De edge is een LIQUIDITY SWEEP (stop-hunt) die door ORDER FLOW wordt
//   bevestigd. Die order-flow-laag (DOM/market depth) bestaat ALLEEN op een echte ECN — op
//   FP Markets raw ECN krijg je de order-book; op The5ers niet/verboden. Deze bot is dus
//   bewust FP-Markets-gespecialiseerd. NIET op The5ers draaien (order-flow/sweep-scalping
//   raakt hun HFT-verbod).
//
// DE EDGE (één samenhangend idee, geen 20 losse knoppen):
//   1. HTF-trendfilter (H1-EMA): alleen mee met de hogere-tijdframe-richting (Rule 14).
//   2. Liquidity mapping: de hoogste high / laagste low over de laatste N bars = de stop-pools
//      (buy-side boven de high, sell-side onder de low).
//   3. Sweep-detectie: de bar wickt VOORBIJ dat niveau (neemt de stops) en sluit weer TERUG
//      binnen -> stop-hunt. Long = sweep van de sell-side low + close erboven; short = mirror.
//   4. Order-flow-bevestiging (DOM): op de sweep moet de order-book de reversal steunen
//      (bid-volume >> ask-volume voor long = kopers absorberen). Fallback: volume-burst.
//   5. Entry op de reversal, stop NET voorbij de sweep-extreme (tight!), TP = RR-multiple,
//      trailen naar de tegenoverliggende liquidity.
//
// RISICO (niet-onderhandelbaar, zelfde scaffolding als de andere bots + risk_guard.py):
//   %-risk sizing, structurele stop achter de sweep, vaste RR-TP, break-even/ATR-trailing,
//   spread- & sessie-filter, dag-breaker (verliesreeks + dagverlies) EN totaal-DD-halt.
//   Geen martingale, geen grid, altijd een harde stop.
//
// EERLIJK: dit is GEEN garantie en GEEN echte HFT. Het leest de footprint die whales
//   achterlaten (sweep + absorptie) en executeert gedisciplineerd. De winst zit in het PROCES
//   (tick-data, walk-forward, Monte Carlo) — zie docs/XAUSMART.md. Sleutel niet aan de code
//   om een mooiere backtest te forceren; dat is overfitten.

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC, AddIndicators = true)]
    public class XauSmart : Robot
    {
        // ---- Edge: liquidity sweep ----
        [Parameter("HTF timeframe", Group = "Edge", DefaultValue = "Hour")]
        public TimeFrame HtfTf { get; set; }
        [Parameter("HTF trend EMA", Group = "Edge", DefaultValue = 50, MinValue = 5)]
        public int TrendEma { get; set; }
        [Parameter("Liquidity lookback (bars)", Group = "Edge", DefaultValue = 20, MinValue = 5)]
        public int SwingLookback { get; set; }
        [Parameter("Min rejection (xATR)", Group = "Edge", DefaultValue = 0.5, MinValue = 0.1)]
        public double MinRejectionAtr { get; set; }
        [Parameter("Allow counter-trend sweep", Group = "Edge", DefaultValue = false)]
        public bool AllowCounter { get; set; }

        // ---- Order flow (DOM) ----
        [Parameter("Use order flow (DOM)", Group = "Order flow", DefaultValue = true)]
        public bool UseOrderFlow { get; set; }
        [Parameter("DOM levels", Group = "Order flow", DefaultValue = 5, MinValue = 1)]
        public int DomLevels { get; set; }
        [Parameter("DOM imbalance ratio", Group = "Order flow", DefaultValue = 1.5, MinValue = 1.0)]
        public double DomImbalance { get; set; }
        [Parameter("Volume-burst x avg (fallback)", Group = "Order flow", DefaultValue = 1.5, MinValue = 1.0)]
        public double VolBurstMult { get; set; }

        // ---- Risk ----
        [Parameter("Risk % per trade", Group = "Risk", DefaultValue = 0.5, MinValue = 0.05, MaxValue = 2)]
        public double RiskPct { get; set; }
        [Parameter("Stop buffer (xATR)", Group = "Risk", DefaultValue = 0.5, MinValue = 0.1)]
        public double StopBufferAtr { get; set; }
        [Parameter("Reward:Risk", Group = "Risk", DefaultValue = 2.5, MinValue = 0.5)]
        public double RR { get; set; }
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

        private const string Label = "XauSmart";
        private Bars _htf;
        private MovingAverage _trend;
        private AverageTrueRange _atr;
        private MarketDepth _depth;
        private DateTime _day;
        private int _consec;
        private double _dayStart, _initBal;
        private bool _haltDay, _haltRun;

        protected override void OnStart()
        {
            _htf = MarketData.GetBars(HtfTf);
            _trend = Indicators.MovingAverage(_htf.ClosePrices, TrendEma, MovingAverageType.Exponential);
            _atr = Indicators.AverageTrueRange(14, MovingAverageType.Exponential);
            if (UseOrderFlow) _depth = MarketData.GetMarketDepth(SymbolName);
            Positions.Closed += OnClosed;
            _initBal = Account.Balance;
            NewDay();
            Print("XauSmart: HTF {0}-EMA{1} | liquidity {2} bars | sweep>= {3}xATR | RR {4} | risk {5}% | DOM {6}",
                  HtfTf, TrendEma, SwingLookback, MinRejectionAtr, RR, RiskPct, UseOrderFlow);
        }

        protected override void OnBar()
        {
            if (Server.Time.Date != _day) NewDay();
            Trail();
            if (_haltRun || _haltDay) return;
            if (Server.Time.Hour < SessStart || Server.Time.Hour >= SessEnd) return;
            if ((Symbol.Ask - Symbol.Bid) / Symbol.PipSize > MaxSpread) return;
            if (Positions.Any(p => p.Label == Label && p.SymbolName == SymbolName)) return;
            if (Bars.Count < SwingLookback + 3) return;

            double atr = _atr.Result.Last(1);
            if (atr <= 0) return;

            int trend = _htf.ClosePrices.LastValue > _trend.Result.LastValue ? 1
                      : _htf.ClosePrices.LastValue < _trend.Result.LastValue ? -1 : 0;

            // Liquidity pools = hoogste high / laagste low over de vorige N bars (excl. de zojuist gesloten bar)
            double priorHigh = double.MinValue, priorLow = double.MaxValue;
            for (int i = 2; i <= SwingLookback + 1; i++)
            {
                priorHigh = Math.Max(priorHigh, Bars.HighPrices.Last(i));
                priorLow = Math.Min(priorLow, Bars.LowPrices.Last(i));
            }

            double hi = Bars.HighPrices.Last(1), lo = Bars.LowPrices.Last(1), cl = Bars.ClosePrices.Last(1);

            // Bullish sweep: wick onder de sell-side liquidity, sluit terug erboven, met sterke rejection
            bool bullSweep = lo < priorLow && cl > priorLow && (cl - lo) >= MinRejectionAtr * atr;
            // Bearish sweep: wick boven de buy-side liquidity, sluit terug eronder, met sterke rejection
            bool bearSweep = hi > priorHigh && cl < priorHigh && (hi - cl) >= MinRejectionAtr * atr;

            if (bullSweep && (trend >= 0 || AllowCounter) && OrderFlowOk(true))
                Enter(TradeType.Buy, lo, atr);
            else if (bearSweep && (trend <= 0 || AllowCounter) && OrderFlowOk(false))
                Enter(TradeType.Sell, hi, atr);
        }

        // Order-flow-bevestiging: DOM-imbalance in de trendrichting, of (fallback) een volume-burst.
        private bool OrderFlowOk(bool bullish)
        {
            if (!UseOrderFlow) return true;

            // 1) DOM: som het volume van de top-N niveaus aan bid en ask.
            try
            {
                if (_depth != null)
                {
                    double bid = 0, ask = 0;
                    int nb = Math.Min(DomLevels, _depth.BidEntries.Count);
                    int na = Math.Min(DomLevels, _depth.AskEntries.Count);
                    for (int i = 0; i < nb; i++) bid += _depth.BidEntries[i].Volume;
                    for (int i = 0; i < na; i++) ask += _depth.AskEntries[i].Volume;
                    if (bid > 0 && ask > 0)
                        return bullish ? bid >= ask * DomImbalance : ask >= bid * DomImbalance;
                }
            }
            catch { /* DOM niet beschikbaar -> val terug op volume-burst */ }

            // 2) Fallback: volume-burst op de sweep-bar (tick-volume >> gemiddelde).
            int n = Math.Min(20, Bars.Count - 2);
            if (n < 5) return true;
            double sum = 0;
            for (int i = 2; i <= n + 1; i++) sum += Bars.TickVolumes.Last(i);
            double avg = sum / n;
            return avg <= 0 || Bars.TickVolumes.Last(1) >= avg * VolBurstMult;
        }

        private void Enter(TradeType side, double sweepExtreme, double atr)
        {
            double entry = side == TradeType.Buy ? Symbol.Ask : Symbol.Bid;
            double slPrice = side == TradeType.Buy
                ? sweepExtreme - StopBufferAtr * atr
                : sweepExtreme + StopBufferAtr * atr;
            double slPips = Math.Abs(entry - slPrice) / Symbol.PipSize;
            if (slPips <= 0 || Symbol.PipValue <= 0) return;
            double tpPips = slPips * RR;
            double risk = Account.Balance * (RiskPct / 100.0);
            double vol = Symbol.NormalizeVolumeInUnits(risk / (slPips * Symbol.PipValue), RoundingMode.Down);
            if (vol < Symbol.VolumeInUnitsMin) return;
            var r = ExecuteMarketOrder(side, SymbolName, vol, Label, slPips, tpPips);
            if (r.IsSuccessful)
                Print("{0} sweep @ {1} | SL {2:0.0}p ({3}) TP {4:0.0}p RR {5}", side, r.Position.EntryPrice, slPips,
                      side == TradeType.Buy ? "onder sweep-low" : "boven sweep-high", tpPips, RR);
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
    }
}
