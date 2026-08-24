# Trader

Deze repo bevat mijn discretionaire trading-workflow (SMC/ICT + Fib OTE) en de tooling om chart-analyses (semi-)automatisch te draaien.

## Verplicht voor elke analyse

Lees **CLAUDE_TRADE.md** volledig voordat je een chart of dataset analyseert — inclusief de Learned Rules onderaan. Elke setup volgt exact het template uit sectie 3 van dat bestand. Geen SL of invalidatie = geen setup. Minimum RR 1:2 tot TP1.

## Workflow

1. Haal data op (of ontvang een screenshot van de gebruiker). In Claude Code-omgevingen blokkeert de netwerkpolicy directe HTTP — gebruik dan de **Zapier MCP**: app "Webhooks by Zapier", action `custom` (method GET, `return_raw_response: yes`) op:
   - Spot: `https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD`
   - Candles: `https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=15m&range=5d` (ook `1h&range=1mo` en `4h&range=3mo` voor HTF-bias)
   - Let op: GC=F is de goud-future en noteert enkele dollars boven spot — kalibreer alle niveaus op de spotprijs.
   Lokaal met vrij netwerk kan ook: `python3 scripts/fetch_xauusd.py` (schrijft `data/snapshot.json` + samenvatting).
2. Analyseer volgens de workflow in CLAUDE_TRADE.md sectie 6 (instrument → HTF-bias → structuur → fib/OTE → template).
3. Sla de analyse op in `analyses/YYYY-MM-DD-<instrument>-<richting>.md`.
4. Alleen bij een A- of B-setup de gebruiker actief notificeren; bij "geen setup" volstaat de log.

**Backtesten / regels verifiëren** (de "run backtests"-stap): `scripts/backtest_rules.py`
speelt de mechanische `risk_guard`-regels terug over historische candles; de identieke
regels staan ook als TradingView-strategie in `strategies/xauusd_range_ote.pine` (gratis
backtesten op echte data in de browser). Zie `docs/TRADINGVIEW_MCP.md` voor de context
rond de "TradingView MCP" (Yahoo-data, werkt niet in de web-sandbox — draai lokaal).

**Geautomatiseerde XAUUSD-cBots (cTrader)**: flagship = `strategies/XauEdge.cs` (bewust simpel:
H1-trend + momentum-breakout, 5 edge-knoppen; gebruik deze op **The5ers**, bar-based). Smart-money-
bot = `strategies/XauSmart.cs` (**liquidity sweep + order-flow/DOM-bevestiging**, alleen op **FP
Markets raw ECN** — order-book vereist; NIET op The5ers ivm HFT-verbod; doc: `docs/XAUSMART.md`).
Varianten/experimenten: `XauScalper.cs` (trend-pullback), `XauFlow.cs` (tick-order-flow, "HFT-achtig",
NIET op The5ers), `XauBreakout.cs` (Donchian-breakout). Allemaal met risk-scaffolding + in-bot
circuit breaker + totaal-DD-halt (idee van `risk_guard`). Compileren + backtesten in cTrader Automate;
optimaliseer op profit factor/drawdown, NIET op win rate. Proces (walk-forward etc.): `docs/XAUEDGE.md`;
bot-details: `docs/XAUSCALPER.md`.

## cTrader MCP + skill `xauusd-ctrader`

Spotware heeft **officiële cTrader MCP-servers** (lokaal `http://127.0.0.1:9876/mcp/` bij een
draaiende desktop; remote voor cTrader Web via bearer-token uit Web → Settings → MCP; docs:
help.ctrader.com/ctrader-ai-agent-connect). Het project-skill
`.claude/skills/xauusd-ctrader/SKILL.md` bevat de volledige goud-workflow daarvoor (MTF-trendbars,
SMC/ICT top-down, killzones, confluence-score ≥3, news-blackout, volume-conversie in lots + raw
units) — gebruik dat skill bij elke goud-analyse ZODRA een cTrader-MCP verbonden is; zonder MCP:
bestaande workflow (screenshots/Zapier). Orders via MCP alléén na expliciete bevestiging van de
gebruiker in de chat, en altijd binnen de risk_guard-pipeline hieronder.

## WhatsApp-notificatie — UITGESCHAKELD (per gebruiker, 2026-08-09)

**Stuur GEEN WhatsApp meer.** De gebruiker wil de setups rechtstreeks in de chat, niet via
WhatsApp. Bij élke A/B-setup (én bij fill/TP/stop-updates): rapporteer de setup **in de chat**
— entry, stop, doelen, RR, conviction, modus — en sla de WhatsApp-stap over. De rest van de
pipeline (active_setups.json bijwerken, trade_cycle draaien, analyse loggen, committen/pushen)
blijft ongewijzigd. Onderstaande WhatsApp-instructies zijn historisch/inactief.

<details><summary>Historisch (inactief): oud WhatsApp-format</summary>

### WhatsApp-notificatie — DIRECT versturen, simpel format (geen link)

**Timing: stuur de WhatsApp METEEN zodra een A/B-setup bekend is** — als éérste actie
ná het bepalen van de setup, nog vóór het loggen/committen/pushen. Dit geldt voor élke
A/B-setup: geplande kill zone-runs én on-demand analyses (screenshot/vraag van de
gebruiker). Bij C of "geen setup": geen WhatsApp. Bij een fill/TP/stop-update: ook direct.

Gebruik de app "WhatsApp Notifications", action `send_message`, **template
`calendar_reminder`** (de enige zónder verplichte reply-link). Geen regeleinden (`\n`)
in de velden — de template weigert die. Twee velden, kort en simpel:

De vaste kop van de WhatsApp-template ("New Calendar Event") ligt vast bij Meta en is
niet via de integratie te hernoemen; laat daarom `event_name` **beginnen met een
onderwerp-woord** zodat dát de eerste vetgedrukte regel is:
- nieuwe setup → `NEW TRADE SETUP`
- fill/TP/stop-update → `TRADE UPDATE`

- `event_name` = onderwerp + de kernregel:
  `NEW TRADE SETUP  •  <RICHTING> goud  •  Entry <x>  •  Stop <x>  •  Doel <TP1>  •  RR <x>`
  (gebruik gewone woorden: "Stop" i.p.v. SL, "Doel" i.p.v. TP1; alleen het éérste doel
  in deze regel.)
- `date_and_time` = de details, gescheiden met ` · `:
  `<A/B>-setup · <dry-run|LIVE|gevuld +xR> · extra doelen <TP2> / <TP3> · dood boven/onder <invalidatie>`

Voorbeeld: event_name `NEW TRADE SETUP • SHORT goud • Entry 4105 • Stop 4118 • Doel 4074 • RR 2,4`,
date_and_time `B-setup · dry-run · extra doelen 4052 / 4045 · dood boven 4118`.
Bij een update: event_name `TRADE UPDATE • SHORT goud • TP1 4074 geraakt • +2,4R`.
Houd het strak: regel 1 = onderwerp + wat te doen + de kerngetallen, regel 2 = de rest. Geen link.

</details>

## Taal

Nederlands, concreet, met prijzen en RR. Trading-termen mogen in het Engels.

## Executie-pipeline (geautomatiseerd; live pas na credentials van de gebruiker)

Bij elke A/B-setup:

1. `signals/active_setups.json` bijwerken (zelfde niveaus als het template;
   C-setups NIET — die blijven advies). **VERPLICHTE velden per A/B-setup**
   (mechanisch afgedwongen door `scripts/risk_guard.py`, anders `rejected`):
   - `regime`: `"range"` of `"trend"` — je moet de markt éérst classificeren.
   - bij `regime:"range"`: `range_low` + `range_high`. De entry moet aan een
     RAND liggen (short in de top-band, long in de low-band) met ruimte naar de
     overkant — geen midden-trades. Dit is de fix voor de −551-week (29-30/07).
   - bij `regime:"trend"`: `htf_bias` (`"bearish"`/`"bullish"`); alleen trend-mee.
   - stop entry→SL ≥ 12 punten (geen ruis-stops).
2. `python3 scripts/trade_cycle.py` draaien. Die valideert de signalen
   (verlopen → expired; RR < 1:2, verkeerde regime/rand, te krappe stop →
   rejected), checkt de **circuit breaker** (`risk_guard`: ≥2 verliezen op rij
   of ≤ −3R deze week ⇒ RISICO-HALT, géén nieuwe orders), kiest zelf de modus
   (LIVE met credentials + bereikbare host, anders dry-run) en logt elke run in
   `signals/execution_log.jsonl`. Commit het log en het signaalbestand mee.
3. **Na élke gesloten trade** het resultaat vastleggen zodat de breaker klopt:
   `python3 scripts/risk_guard.py record --r <R> --pnl <bedrag> --note "..."`.
   Status bekijken: `risk_guard.py status`. Bewust hervatten na een halt (jouw
   knop): `risk_guard.py resume` (geldt die week, vervalt bij een winst/reset).

Credentials als env vars (NOOIT in code/repo): CTRADER_CLIENT_ID/SECRET/
ACCESS_TOKEN/ACCOUNT_ID, CTRADER_ENV=demo|live. Voor live executie moet de
netwerkpolicy van de omgeving `demo.ctraderapi.com`/`live.ctraderapi.com`
poort 5035 toestaan (raw TLS, niet via de HTTPS-proxy).

Kill switch: `python3 scripts/trade_cycle.py --kill on` zodra de gebruiker
"stop trading" zegt — de eerstvolgende run annuleert alle executor-orders.
