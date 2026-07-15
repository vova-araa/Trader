//+------------------------------------------------------------------+
//| TraderHFT_XAUUSD.mq5                                             |
//|                                                                  |
//| MQL5-poort van de HFT/scalp-module uit scripts/superbot.py:      |
//| dezelfde Bollinger(20,2)+RSI(14) mean-reversion-scalp op M1, met |
//| spread-filter, sessiefilter en dezelfde soort vangrails          |
//| (marge-check, consecutive-loss circuit breaker, dag-verlieslimiet|
//| kill switch). Bedoeld voor wie liever op MetaTrader 5 draait     |
//| i.p.v. de cTrader-superbot — GEEN vervanging, een los alternatief|
//|                                                                  |
//| NIET hier gecompileerd/getest: MetaEditor/Strategy Tester zijn   |
//| Windows-only en draaien niet in deze sandbox. Compileer en       |
//| draai dit EERST in de Strategy Tester op historische data, en    |
//| daarna op een demo-account, voor je 'm ooit live zet.            |
//+------------------------------------------------------------------+
#property copyright "Trader"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>

CTrade trade;

//---------------------------------------------------------------- inputs --
input group "Aan/uit"
input bool   InpEnabled              = true;    // Scalper actief

input group "Risico"
input double InpRiskPctPerTrade      = 1.0;     // Risico % van equity per trade
input double InpFallbackLots         = 0.01;    // Fallback-lotgrootte als sizing niet lukt
input double InpMaxMarginUtilPct     = 50.0;    // Max % van equity als marge (cumulatief)
input int    InpConsecutiveLossLimit = 3;       // Pauze na N verliezen op rij
input int    InpPauseHours           = 4;       // Pauzeduur na circuit breaker (uur)
input double InpMaxDailyLossPct      = 5.0;     // Dagverlieslimiet (% van dag-start-equity)

input group "Strategie (Bollinger + RSI mean-reversion, M1)"
input int    InpBBPeriod             = 20;
input double InpBBDeviation          = 2.0;
input int    InpRSIPeriod            = 14;
input double InpRSIOverbought        = 70.0;
input double InpRSIOversold          = 30.0;
input double InpSLDollars            = 10.0;    // SL-afstand in $ (XAUUSD-prijs, geen MQL5-"points")
input double InpTPDollars            = 18.0;    // TP-afstand in $ (RR ~1.8)
input double InpMaxSpreadDollars     = 5.0;     // skip entry als spread hoger is
input int    InpSessionStartUTC      = 7;       // Londen-open
input int    InpSessionEndUTC        = 20;      // NY-sluit
input int    InpCooldownSeconds      = 300;

input group "Overig"
input ulong  InpMagic                = 20260715;
input string InpKillSwitchGlobalVar  = "TraderHFT_KillSwitch"; // zet deze terminal-global var op 1 om alles te stoppen

//---------------------------------------------------------------- state ---
int      bbHandle = INVALID_HANDLE;
int      rsiHandle = INVALID_HANDLE;
datetime lastTradeTime = 0;
datetime pausedUntil = 0;
datetime lastBarTime = 0;
datetime dailyHaltDay = 0;   // middernacht (UTC) van de dag waarop de daglimiet geraakt is
datetime dayStartRefDay = 0; // middernacht (UTC) van de dag waarvoor dayStartEquity geldt
double   dayStartEquity = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   bbHandle = iBands(_Symbol, PERIOD_M1, InpBBPeriod, 0, InpBBDeviation, PRICE_CLOSE);
   rsiHandle = iRSI(_Symbol, PERIOD_M1, InpRSIPeriod, PRICE_CLOSE);
   if(bbHandle == INVALID_HANDLE || rsiHandle == INVALID_HANDLE)
   {
      Print("Indicator-init mislukt (Bollinger/RSI)");
      return INIT_FAILED;
   }
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetTypeFillingBySymbol(_Symbol);
   dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   dayStartRefDay = DayStartUTC(TimeGMT());
   Print("TraderHFT_XAUUSD gestart. symbol=", _Symbol, " magic=", InpMagic);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(bbHandle != INVALID_HANDLE) IndicatorRelease(bbHandle);
   if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
}

//+------------------------------------------------------------------+
datetime DayStartUTC(datetime t)
{
   return t - (t % 86400);
}

bool KillSwitchActive()
{
   if(GlobalVariableCheck(InpKillSwitchGlobalVar))
      return GlobalVariableGet(InpKillSwitchGlobalVar) > 0.5;
   return false;
}

bool InSession(datetime tGMT)
{
   MqlDateTime dt;
   TimeToStruct(tGMT, dt);
   return dt.hour >= InpSessionStartUTC && dt.hour < InpSessionEndUTC;
}

//---------------------------------------------------------- positions/history --
int CountOpenMagicPositions()
{
   int n = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == (long)InpMagic)
         n++;
   }
   return n;
}

void CloseAllMagicPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == (long)InpMagic)
      {
         trade.PositionClose(ticket);
      }
   }
}

// Nettowinst (profit+swap+commissie) van gesloten deals van dit EA, nieuwste
// eerst. sinceTime beperkt de historieselectie (performance).
int GetClosedDealsDesc(datetime sinceTime, double &pnlOut[], datetime &timeOut[])
{
   if(!HistorySelect(sinceTime, TimeCurrent()))
      return 0;
   int total = HistoryDealsTotal();
   double pnls[]; datetime times[];
   ArrayResize(pnls, 0); ArrayResize(times, 0);
   for(int i = 0; i < total; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0) continue;
      if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol) continue;
      if(HistoryDealGetInteger(ticket, DEAL_MAGIC) != (long)InpMagic) continue;
      if(HistoryDealGetInteger(ticket, DEAL_ENTRY) != DEAL_ENTRY_OUT) continue;
      double net = HistoryDealGetDouble(ticket, DEAL_PROFIT)
                 + HistoryDealGetDouble(ticket, DEAL_SWAP)
                 + HistoryDealGetDouble(ticket, DEAL_COMMISSION);
      datetime tt = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
      int n = ArraySize(pnls);
      ArrayResize(pnls, n + 1); ArrayResize(times, n + 1);
      pnls[n] = net; times[n] = tt;
   }
   // sorteer aflopend op tijd (eenvoudige insertion sort, kleine array)
   int n = ArraySize(pnls);
   for(int i = 1; i < n; i++)
   {
      double pv = pnls[i]; datetime tv = times[i];
      int j = i - 1;
      while(j >= 0 && times[j] < tv)
      {
         pnls[j+1] = pnls[j]; times[j+1] = times[j];
         j--;
      }
      pnls[j+1] = pv; times[j+1] = tv;
   }
   ArrayResize(pnlOut, n); ArrayResize(timeOut, n);
   for(int i = 0; i < n; i++) { pnlOut[i] = pnls[i]; timeOut[i] = times[i]; }
   return n;
}

int CountConsecutiveLosses()
{
   double pnl[]; datetime tm[];
   int n = GetClosedDealsDesc(TimeCurrent() - 3*86400, pnl, tm);
   int losses = 0;
   for(int i = 0; i < n; i++)
   {
      if(pnl[i] < 0) losses++;
      else break;
   }
   return losses;
}

double GetTodayRealizedPnL()
{
   datetime today = DayStartUTC(TimeGMT());
   double pnl[]; datetime tm[];
   int n = GetClosedDealsDesc(today, pnl, tm);
   double total = 0;
   for(int i = 0; i < n; i++) total += pnl[i];
   return total;
}

//------------------------------------------------------------- risk gates --
// Bijgewerkt eenmaal per nieuwe M1-bar (niet elke tick) — zet pausedUntil /
// halt-status. Sluit ALLE eigen posities bij dagverlieslimiet, net als de
// kill_switch-logica in superbot.py.
void UpdateRiskGates()
{
   datetime today = DayStartUTC(TimeGMT());
   if(today != dayStartRefDay)
   {
      dayStartRefDay = today;
      dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      dailyHaltDay = 0; // nieuwe dag, halt-status reset
   }

   int losses = CountConsecutiveLosses();
   if(losses >= InpConsecutiveLossLimit && TimeCurrent() >= pausedUntil)
   {
      pausedUntil = TimeCurrent() + InpPauseHours * 3600;
      Print("Circuit breaker: ", losses, " verliezen op rij -> pauze tot ", TimeToString(pausedUntil));
   }

   if(dailyHaltDay != today && dayStartEquity > 0)
   {
      double dayPnl = GetTodayRealizedPnL();
      if(dayPnl < 0 && MathAbs(dayPnl) / dayStartEquity * 100.0 >= InpMaxDailyLossPct)
      {
         dailyHaltDay = today;
         Print("Dag-verlieslimiet geraakt (", DoubleToString(dayPnl, 2), ") -> stop voor de rest van de dag, sluit posities");
         CloseAllMagicPositions();
      }
   }
}

//------------------------------------------------------------- sizing/margin --
// Broker-agnostische risk-based sizing via tick value (correcter dan een
// aanname over contractgrootte): $ per 1.0-lot per prijseenheid = TickValue/TickSize.
double CalcVolumeLots(double slDollars)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(equity <= 0 || slDollars <= 0 || tickValue <= 0 || tickSize <= 0)
      return InpFallbackLots;

   double dollarsPerPriceUnitPerLot = tickValue / tickSize;
   double dollarRisk = equity * (InpRiskPctPerTrade / 100.0);
   double lots = dollarRisk / (slDollars * dollarsPerPriceUnitPerLot);

   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minV = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxV = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0) step = 0.01;
   lots = MathFloor(lots / step) * step;
   if(lots < minV) lots = minV;
   if(maxV > 0 && lots > maxV) lots = maxV;
   return lots;
}

bool MarginOk(double lots, ENUM_ORDER_TYPE orderType, double price)
{
   double margin = 0;
   if(!OrderCalcMargin(orderType, _Symbol, lots, price, margin))
      return false;
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double usedMargin = AccountInfoDouble(ACCOUNT_MARGIN);
   if(equity <= 0) return false;
   double projectedUtil = (usedMargin + margin) / equity * 100.0;
   if(projectedUtil > InpMaxMarginUtilPct)
   {
      Print("Order geweigerd: marge-utilisatie ", DoubleToString(projectedUtil,1), "% > ", InpMaxMarginUtilPct, "%");
      return false;
   }
   return true;
}

//------------------------------------------------------------- signaal --
// Retourneert 1 (long), -1 (short) of 0 (geen signaal). Zelfde regel als
// hft_signal() in scripts/superbot.py: Bollinger-extreem + RSI-bevestiging.
int GetSignal()
{
   double bbUpper[], bbLower[], rsiVal[];
   ArraySetAsSeries(bbUpper, true); ArraySetAsSeries(bbLower, true);
   ArraySetAsSeries(rsiVal, true);

   if(CopyBuffer(bbHandle, 1, 0, 1, bbUpper) <= 0) return 0;   // upper band
   if(CopyBuffer(bbHandle, 2, 0, 1, bbLower) <= 0) return 0;   // lower band
   if(CopyBuffer(rsiHandle, 0, 0, 1, rsiVal) <= 0) return 0;

   double lastClose = iClose(_Symbol, PERIOD_M1, 0);
   if(lastClose >= bbUpper[0] && rsiVal[0] >= InpRSIOverbought) return -1;
   if(lastClose <= bbLower[0] && rsiVal[0] <= InpRSIOversold) return 1;
   return 0;
}

//------------------------------------------------------------- entry --
void TryEnter(int signal)
{
   if(CountOpenMagicPositions() > 0) return; // max 1 gelijktijdige scalp-positie

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double spread = ask - bid;
   if(spread > InpMaxSpreadDollars)
   {
      Print("Skip: spread ", DoubleToString(spread,2), " > max ", InpMaxSpreadDollars);
      return;
   }

   double lots = CalcVolumeLots(InpSLDollars);
   ENUM_ORDER_TYPE orderType = (signal > 0) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   double entryPrice = (signal > 0) ? ask : bid;
   if(!MarginOk(lots, orderType, entryPrice)) return;

   double sl = (signal > 0) ? entryPrice - InpSLDollars : entryPrice + InpSLDollars;
   double tp = (signal > 0) ? entryPrice + InpTPDollars : entryPrice - InpTPDollars;

   bool ok;
   if(signal > 0)
      ok = trade.Buy(lots, _Symbol, 0, sl, tp, "bollinger+rsi mean-reversion scalp");
   else
      ok = trade.Sell(lots, _Symbol, 0, sl, tp, "bollinger+rsi mean-reversion scalp");

   if(ok)
   {
      lastTradeTime = TimeCurrent();
      Print("Order geplaatst: ", (signal>0?"BUY":"SELL"), " ", lots, " lots @ ~", entryPrice,
            " SL=", sl, " TP=", tp);
   }
   else
   {
      Print("Order MISLUKT: ", trade.ResultRetcodeDescription());
   }
}

//+------------------------------------------------------------------+
void OnTick()
{
   if(!InpEnabled) return;

   if(KillSwitchActive())
   {
      CloseAllMagicPositions();
      return;
   }

   // Signaal + risk-gates alleen bij een nieuwe M1-bar evalueren (geen
   // overbodige rekenkracht per tick, en voorkomt dubbele entries binnen
   // dezelfde bar).
   datetime barTime = iTime(_Symbol, PERIOD_M1, 0);
   if(barTime == lastBarTime) return;
   lastBarTime = barTime;

   UpdateRiskGates();

   datetime nowGMT = TimeGMT();
   if(dailyHaltDay == DayStartUTC(nowGMT)) return;
   if(TimeCurrent() < pausedUntil) return;
   if(!InSession(nowGMT)) return;
   if(TimeCurrent() - lastTradeTime < InpCooldownSeconds) return;

   int signal = GetSignal();
   if(signal == 0) return;

   TryEnter(signal);
}
//+------------------------------------------------------------------+
