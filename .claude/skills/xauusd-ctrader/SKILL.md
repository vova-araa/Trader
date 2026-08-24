---
name: xauusd-ctrader
description: Analyze XAU/USD (gold) and generate ICT/Smart-Money trade setups on cTrader. Use whenever the user mentions gold, XAUUSD, XAU, a gold setup, gold bias, killzone, liquidity sweep, FVG/order block on gold, or asks to check/scan/analyze/trade gold via cTrader. Pulls multi-timeframe trendbars via the cTrader MCP server, runs top-down SMC analysis, sizes positions in cTrader volume units, and ALWAYS requires explicit human confirmation before any order is placed.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# XAU/USD (Gold) Analysis & Setup Generation — cTrader

Turn a natural-language gold request into a **sourced, multi-timeframe SMC setup** with exact **cTrader volume**, then optionally place it **only after explicit human confirmation**.

> Huisregels: dit skill werkt BINNEN de bestaande workflow van deze repo. Lees ALTIJD eerst
> `CLAUDE_TRADE.md` (alle Learned Rules, m.n. 12/14/16-19/22/23/24) en volg de executie-pipeline
> uit `CLAUDE.md` (active_setups.json → trade_cycle.py → risk_guard-breaker). Bij conflict wint
> de strengste regel.

## 0. Session bootstrap (every session, in order)
1. **Route to cTrader**: start with "Using the cTrader MCP server…" so the agent calls MCP, not web search. ([FAQ](https://help.ctrader.com/ctrader-ai-agent-connect/faq/))
2. **Verify connection & list tools**: enumerate the connected `ctrader` MCP server's tools; print the **exact tool names you actually have**. Do NOT assume names — Spotware publishes *operation categories* + REST paths, not fixed snake_case tool IDs, so names vary by client/server.
3. **Detect server type**:
   - **Local** (Windows/Mac): `{ "mcpServers": { "ctrader": { "type": "http", "url": "http://127.0.0.1:9876/mcp/" } } }` ([setup](https://help.ctrader.com/ctrader-ai-agent-connect/local-mcp/setup/)). Widest coverage: trading, account, market data, charts, indicators, UI. Vereist een DRAAIENDE cTrader-desktop op dezelfde machine als Claude (werkt dus NIET vanuit een cloud-sessie).
   - **Remote** (cTrader Web): per-account bearer token via cTrader Web → Settings → MCP ([docs](https://help.ctrader.com/ctrader-ai-agent-connect/remote-mcp/)). Coverage: trading, account, analysis (candles + live prices) only.
   - Neither responds → tell user to enable MCP in cTrader and re-run. In deze repo-omgeving zonder cTrader-MCP: val terug op de bestaande workflow (screenshots van de gebruiker / Zapier-feed) en zeg dat expliciet.
4. **Map capability → intent** (self-adapt to what exists):
   - Historical candles → `GET /v1/trendbars` (returns `Trendbar[]`; [API-referentie](https://help.ctrader.com/ctrader-ai-agent-connect/api/reference/)).
   - Live price snapshot (no streaming) → prices/`SpotPrice` tool.
   - Symbols → `GET /v1/symbols`; assets → `GET /v1/assets`; account → `GET /v1/balance`; positions → positions tool; place order → `POST /v1/orders`; amend/cancel → order tools.
   - Missing capability → degrade gracefully and state what's unavailable.
5. **Resolve the gold symbol**: list symbols and find gold — may be `XAUUSD`, `GOLD`, `XAUUSD.`, `XAUUSD.pro`, or a suffixed variant. Read its **contract size, digits, min volume, volume step** from symbol details. **Never hardcode.**

## 1. cTrader facts to obey
- **Trendbar periods** (underscore form): `M_1 M_2 M_3 M_4 M_5 M_10 M_15 M_30 H_1 H_2 H_3 H_4 H_6 H_8 H_12 D_1 W_1 MN_1`.
- **Trendbar payload**: `{ timestamp(ms), open, high, low, close, volume }` (MCP `/v1/trendbars` returns absolute OHLC; raw Open API returns relative deltas over `low/100000`).
- **Bars need ticks**: Open API FAQ — *"trend bars are only created if there are incoming ticks."* For the freshest quote use the **live-price/spot** tool (raw API: `ProtoOASubscribeSpotsReq` → first `ProtoOASpotEvent` carries latest bid/ask).
- **Volume conventions (critical)**:
  - Natural-language layer: **volume = units of the base asset**; forex 1 lot = 100,000 units; **metals vary — read from symbol details.**
  - Raw `/v1/orders` layer: volume is in **"cents" = units of 0.0000001 lots** (e.g. EURUSD 1 lot = `10000000`).
  - **XAUUSD**: 1 standard lot = **100 troy ounces**; **1 pip = 0.01 = $1.00 per 1.00 lot** (0.10 lot = $0.10/pip; 0.01 lot = $0.01/pip). A **$1.00 gold move = 100 pips.**
  - Always show the intended size in **lots** AND the raw volume you will send; let contract size do the conversion. Verify against **min volume / volume step**.
- **Auth**: MCP handles it — local via the running desktop session, remote via the cTrader-ID-scoped bearer token. (Underlying Open API is OAuth 2.0: auth code 1 min → access token ~30 dagen → refresh token verloopt nooit. You normally never touch this.)
- **Official skills** you may layer in: `spotware/ctrader-skills` → `ctrader-mcp-servers` (units/encoding + pip/position-sizing/margin helpers) en `ctrader-cli`. Install: `npx skills add spotware/ctrader-skills --skill '*' --yes`.

## 2. Multi-timeframe pull (default)
Fetch gold trendbars: **D_1** (~60), **H_4** (~120), **H_1** (~120), **M_15** (~200), **M_5** (~200). Pull a **live price snapshot**. Pull **DXY** too if the symbol list exposes it.

## 3. SMC / ICT workflow (top-down)
- **A — HTF bias (D1→H4)**: trend via structure (HH/HL vs LH/LL); last **BOS** (continuation) vs **CHoCH** (reversal). Mark **PDH/PDL, PWH/PWL, daily open**, equal highs/lows (liquidity), unmitigated **FVGs/OBs**.
- **B — Premium/Discount**: draw the dealing range from the **most-recently-broken swing**. **Longs only in discount (<50%)**, **shorts only in premium (>50%)**. **OTE = 62–79%** retrace (key 70.5%).
- **C — Draw on liquidity**: name the pool price is likely targeting next.
- **D — LTF entry (M15→M5)**: **liquidity sweep → displacement (fast candles leaving an FVG) → CHoCH/MSS → enter on retrace into the FVG or OB inside OTE.**
- **E — Stops/targets**: **SL** beyond the sweep extreme (structure, not fixed pips; huisregel: stop ≥ 12 punten). **TP1** = nearest opposing liquidity; **TP2** = range extreme / PDH-PDL. Enforce **min 1:2 R:R** (huisregel Rule 2, mechanisch afgedwongen).

## 4. Killzones — trade only inside these (New York ET / Amsterdam CET)
Amsterdam CET/CEST = **ET + 6h** (both observe DST; expect a temporary +5h offset during the ~2-week March & Oct/Nov DST-transition mismatch — verify).
- **Asian range** (builds liquidity): 20:00–00:00 ET / **02:00–06:00 CET**.
- **London KZ** (often sets daily low/high; deepest gold book): 02:00–05:00 ET / **08:00–11:00 CET**.
- **London Silver Bullet**: 03:00–04:00 ET / **09:00–10:00 CET**.
- **New York KZ** (largest gold moves; London overlap): 07:00–10:00 ET / **13:00–16:00 CET**.
- **NY AM Silver Bullet**: 10:00–11:00 ET / **16:00–17:00 CET**.
- **London Close** (late reversals): 10:00–12:00 ET / **16:00–18:00 CET**.
Gold is uniquely active in **both** London open (currency) and NY open (COMEX). Outside killzones → **NO TRADE** unless HTF setup is exceptional. (Sluit aan op Rule 23: geen thin-liquidity knife-catches.)

## 5. Intermarket confluence — DXY & US 10Y real yields
- **Historical**: gold ↔ DXY inverse (≈ −0.5 to −0.82); gold ↔ 10Y real yield inverse — Erb & Harvey, *The Golden Dilemma* (NBER WP 18706): TIPS-real-yield vs real goudprijs ≈ −0.82 (1997–2012; auteurs noemen het "likely spurious"). PIMCO: +100 bp real yield ≈ −18% real gold.
- **2026 regime break (flag explicitly)**: door 2024–2026 werd de relatie **asymmetrisch/decoupled** — goud steeg ook bij stijgende reële rentes ([J.P. Morgan](https://privatebank.jpmorgan.com/apac/en/insights/markets-and-investing/is-it-a-golden-era-for-gold)), gedreven door **record centrale-bank-koop + de-dollarization** (WGC: 1.136t 2022, 1.037t 2023, ~1.045t 2024, 863t 2025; goud passeerde in 2025 US Treasuries als grootste reserve-asset).
- **Rules**: check correlation on the **daily**, not intraday. DXY weak / real yields falling → **+1 confluence** for longs. **Do NOT blind-short gold just because DXY is up** — confirm the driver. A lone correlation signal = noise.

## 6. High-impact USD news filter
- Key events (ET): **NFP** 08:30 (1e vrijdag), **CPI** 08:30, **Core PCE**, **FOMC** 14:00 (+ presser), plus PPI/GDP/retail sales/JOLTS & Fed-chair speeches (bijv. Jackson Hole).
- **Blackout**: no new gold entries **60 min vóór t/m 60 min ná** any high-impact USD release (verscherping van Rule 12). Holding into it → move to break-even or step aside.
- After release **wait 15–30 min**, then trade the post-spike **sweep → FVG/OB** retrace. Reduce size ~50% on news days.

## 7. Confluence scoring — require ≥3 to trade
1 pt each: (1) HTF D1/H4 bias aligned; (2) correct **premium/discount + OTE**; (3) **liquidity sweep** done; (4) **displacement + CHoCH/MSS** on LTF; (5) entry at **FVG/OB**; (6) inside a **killzone**; (7) **DXY/real-yield** confluence; (8) clear **draw on liquidity** for TP.
**< 3 pts OR R:R < 1:2 OR inside news blackout OR risk_guard-HALT zonder bewuste resume → NO TRADE.**

## 8. Structured output (always use this block)
<!-- Aangevuld door Claude (origineel afgekapt): gebaseerd op CLAUDE_TRADE.md sectie 3 / Rule 10-template. -->
```
SETUP — XAUUSD [TF] [LONG/SHORT]   (of: GEEN SETUP — reden)
Bias:        [D1/H4-richting + laatste BOS/CHoCH]
Zone:        [entry-zone + waarom (FVG/OB/OTE/premium-discount)]
Confluences: [score x/8: opsomming van de punten uit §7]
Killzone:    [welke / of "buiten killzone"]
Entry:       [prijs + ordertype (limit/stop/market-op-bevestiging)]
Stop Loss:   [prijs] ([pt] — voorbij de sweep-extreme, ≥12pt)
Take Profit: TP1 [prijs] (RR [x]) · TP2 [prijs] · TP3 [prijs]
Risk:Reward: [naar TP1; min 1:2]
Invalidatie: [H1-close-conditie]
Conviction:  [A/B/C + waarom]
Size:        [lots] = [raw volume units] (@ [risk%] van balans, ≤$[bedrag])
Nieuws:      [events binnen 24u + blackout-plan]
Management:  BE bij +1R (VERPLICHT, Rule 22) · partial 1/3 op TP1 · trail runner
```

## 9. Executie — pipeline + bevestigingspoort (NOOIT overslaan)
1. A/B-setup → schrijf naar `signals/active_setups.json` (met `regime`/`htf_bias`) en draai `python3 scripts/trade_cycle.py --no-fetch`; rejected = niet fixen door regels op te rekken.
2. Check `risk_guard.py status`: bij HALT géén order zonder expliciete, bewuste `resume` door de gebruiker.
3. **Order plaatsen via de cTrader MCP mag ALLEEN na expliciete menselijke bevestiging in de chat** ("plaats hem" o.i.d.) — toon eerst het volledige §8-blok + de exacte lots én raw volume die verstuurd worden. Geen bevestiging = analyse only.
4. Na fill/TP/SL: resultaat boeken met `risk_guard.py record`, setup-status bijwerken, committen en pushen.
5. C-setups blijven advies. Kill switch (`trade_cycle.py --kill on`) bij "stop trading".
