# TradingView-MCP — hoe het werkt en wat we ervan toepassen

Naar aanleiding van de "techskills"-post (Claude + TradingView MCP: charts scannen,
Pine Script schrijven, backtesten, setups vinden via prompts). Hieronder eerlijk wat
het is, of het in ónze omgeving werkt, en wat we er concreet van hebben toegepast.

## Wat is die "TradingView MCP" eigenlijk

Het zijn **community-MCP-servers** (geen officieel TradingView-product). De bekendste
voor forex/goud is `atilaahmettaner/tradingview-mcp`. Belangrijk om te weten:

- **Databron = Yahoo Finance + scraping van publieke endpoints.** *Niet* de officiële
  TradingView-API. De indicatoren komen uit de `tradingview-ta`-library (leest de
  publieke "Technicals"-widget). Zelfde bron als onze `scripts/fetch_xauusd.py`.
- Twee smaken: **self-host** (lokale Python `stdio`-server, gratis, MIT) of **hosted**
  (pro.cryptosieve.com, ~$9–29/mnd, 2.500–10.000 calls/mnd).
- ~37 tools: prijzen (`yahoo_price`, `market_snapshot`), technische analyse, screeners,
  candlestick-patronen, **backtesting** (`backtest_strategy`, `walk_forward_...`) en
  Pine-Script-helpers.

Bronnen: <https://github.com/atilaahmettaner/tradingview-mcp> ·
<https://github.com/vtlk/tv-pinescript-backtest-engine-mcp> ·
<https://www.humbledtrader.com/blog/connect-claude-to-tradingview-mcp/>

## Werkt dit in deze Claude-Code-webomgeving? — Nee, om dezelfde reden als Zapier

De self-host-MCP haalt data van **Yahoo Finance**, en de sandbox-proxy hier blokkeert
juist directe HTTP naar die datafeeds (dáárom draaien we nu via Zapier, mét task-quota).
Een lokale TradingView-MCP *ín* de sandbox loopt tegen exact dezelfde muur. De hosted
variant zou als remote-MCP eventueel door de proxy kunnen, maar kost geld en moet jij
zelf als connector koppelen — ik kan geen betaalde MCP namens jou toevoegen.

Kortom: de post beschrijft grotendeels wat wij al bouwen (analyse + setups + executie),
op dezelfde Yahoo-data. De post is er zelf eerlijk over: *"AI can produce errors,
overfit strategies, and generate signals that fail in live conditions."*

## Wat we er WÉL van hebben toegepast (nu, gratis, zonder externe MCP)

De twee stukken uit de workflow die wij nog niet hadden — **Pine Script + backtesten** —
zijn nu in de repo, toegepast op ónze eigen aangescherpte regels:

### 1. `strategies/xauusd_range_ote.pine` — onze regels als TradingView-strategie
Encodeert 1-op-1 de `risk_guard.py`-regels: range-detectie, alleen rand-entries (geen
midden), min-stop 12pt, RR ≥ 2, en de circuit breaker (halt na 2 verliezen op rij,
reset op de weekrol).

**Gebruik (echte TradingView-data, geen Zapier, geen sandbox-limiet):**
1. TradingView → grafiek op **XAUUSD** (of `GC1!`).
2. **Pine Editor** (onderin) → plak de inhoud van het `.pine`-bestand → **Add to chart**.
3. Tab **Strategy Tester** → zie trades, win%, net profit, max drawdown op echte historie.
4. Stel de inputs bij (range-lookback, edge-band, RR) en zie direct het effect.

### 2. `scripts/backtest_rules.py` — dezelfde regels over historische candles
Speelt de **identieke** structurele guard (`risk_guard.structural_reject_reason`) terug
over een candle-reeks, plus de circuit breaker. Zo verifiëren we of de regels écht
presteren i.p.v. het te beweren. Draait lokaal of op de VPS (waar data wél stroomt):

```bash
# Yahoo v8 chart-JSON (zoals fetch_xauusd ophaalt):
python3 scripts/fetch_xauusd.py                      # schrijft data/…
python3 scripts/backtest_rules.py --yahoo data/candles_1h.json --range-len 96
# of een simpele candle-lijst [{t,o,h,l,c}]:
python3 scripts/backtest_rules.py --candles data/candles.json
```
Uitvoer: trades, win%, som R, gem. R, max drawdown (R) en hoeveel entries de breaker
tegenhield. (`scripts/backtest.py` blijft de analyse van de handmatige trade-ledger;
`backtest_rules.py` is de candle-replay van de regels.)

## Als je de TradingView-MCP tóch wilt draaien

Doe het op de **altijd-aan machine** uit `docs/LIVE_247.md` (laptop/VPS met vrij
internet), niet in de webomgeving:

```bash
pipx install uv           # of pip install uv
# Claude Desktop → Settings → Developer → Edit Config → in mcpServers:
#   "tradingview": { "command": "uvx",
#                    "args": ["--from", "tradingview-mcp-server", "tradingview-mcp"] }
```
Dan kun je in Claude Desktop prompts als "scan XAUUSD multi-timeframe" of
"backtest deze Pine-strategie" draaien op dezelfde machine die ook onze
`run_local_loop.sh` + cTrader-executie draait. Data blijft Yahoo-kwaliteit — prima voor
research/backtest, maar kalibreer live-niveaus altijd op de Swissquote-spot (zoals nu).
