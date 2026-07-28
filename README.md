# Trader — automatische XAUUSD trade-analyse

Discretionaire SMC/ICT + Fib OTE workflow (zie `CLAUDE_TRADE.md`), met tooling om de analyse automatisch te laten draaien via Claude Code Routines.

## Onderdelen

| Bestand | Doel |
|---|---|
| `CLAUDE_TRADE.md` | De strategie en harde regels — het "brein" van elke analyse |
| `CLAUDE.md` | Instructies zodat elke Claude-sessie in deze repo de strategie volgt |
| `scripts/fetch_xauusd.py` | Haalt live spot + 15m/1h/4h candles op, detecteert swings en berekent auto-fib (OTE) |
| `analyses/` | Gelogde setups per datum |
| `data/snapshot.json` | Laatste data-snapshot (gegenereerd, niet gecommit) |

## Volledig automatisch (Routines)

Het idee: een geplande Routine start rond de kill zones (London open ~09:00 NL, NY open ~14:30 NL) een verse Claude-sessie die:

1. `python3 scripts/fetch_xauusd.py` draait voor verse data;
2. `CLAUDE_TRADE.md` leest en de data analyseert volgens de vaste workflow;
3. de setup logt in `analyses/` en commit;
4. **alleen bij een A- of B-setup** een push-/e-mailnotificatie stuurt — "geen setup" blijft stil.

### Datapad: Zapier MCP (actief)

De netwerkpolicy van de omgeving blokkeert directe HTTP naar de datafeeds, maar via de gekoppelde **Zapier MCP** ("Webhooks by Zapier" → action `custom`, GET) zijn Swissquote-spot en Yahoo GC=F-candles live op te halen — getest en werkend. Zie CLAUDE.md voor de exacte URLs. Alternatief blijft: de network policy van de omgeving verruimen zodat `scripts/fetch_xauusd.py` direct werkt.

De Routine draait **elk uur** ma–vr (`7 * * * 1-5`, UTC): continue monitoring i.p.v. alleen de kill zones. Beslisboom per uur:
- **A/B-setup of wijziging aan een actieve order/positie** (fill/TP/stop/invalidatie) → direct WhatsApp-alert (linkloos `calendar_reminder`-format), signaalbestand bij, `trade_cycle.py`, volledige analyse in `analyses/`, commit + push.
- **Rustig uur (geen setup)** → geen WhatsApp, geen analysebestand; alleen validatie/expiry via `trade_cycle.py` en één regel in `signals/monitor_log.jsonl`.

De WhatsApp-alert gaat als éérste actie de deur uit zodra een setup bekend is (ook bij on-demand analyses), niet pas aan het eind van de run.

Live-executie aanzetten: zie `docs/LIVE_SETUP.md`; verifieer met `python3 scripts/check_live_ready.py`.

Optionele upgrade: TradingView-alerts per e-mail laten sturen — de Routine leest Gmail (Zapier) en neemt geraakte alertniveaus mee in de analyse.

## Semi-automatisch (huidige flow)

Zonder netwerkverruiming werkt de screenshot-flow altijd: stuur 1H + 15m charts in een sessie, Claude leest `CLAUDE_TRADE.md` en levert de setup in het vaste template.

## Disclaimer

Trade-ideeën en analyse, geen financieel advies. De beslissing en het risico zijn aan jou.

## TradingView-integratie

`tradingview/trader_setups.pine` — indicator die de actieve setups tekent
(zone-box, entry, SL, TP1–3) en bewaakt: alert bij zone-touch, entry-fill en
invalidatie-close. Installatie: Pine Editor → plakken → Add to chart → per
setup de template-getallen invullen → één alert aanmaken op "Any alert()
function call" met app-notificatie.

## Automatische executie (pipeline klaar; live is een bewuste gebruikersstap)

De pipeline draait automatisch mee in elke analyse-run, maar plaatst pas echte
orders nadat de gebruiker zélf de credentials heeft ingesteld (zie checklist
hieronder) — dat is de "knop" uit CLAUDE_TRADE.md sectie 0, en die blijft bij
de gebruiker. Zonder credentials draait alles in dry-run. De keten:

```
Routine (kill zones) → analyse → signals/active_setups.json (alleen A/B)
    → scripts/trade_cycle.py → scripts/executor_ctrader.py
    → limit orders + SL/TP op FP Markets cTrader
```

`trade_cycle.py` is het enige entrypoint dat de Routine draait. Vangrails
(machinaal afgedwongen, dubbel: in de cycle-validator én in de executor):

- alleen conviction **A/B** met status `active`; C blijft advies
- **RR ≥ 1:2 tot TP1**, anders `rejected`; verlopen setups → `expired` + cancel
- niveaus moeten logisch liggen (short: SL > entry > TP1; long: omgekeerd)
- max 30 punten entry→SL risico, max 3 gelijktijdige orders, altijd SL + TP mee
- idempotent via order-labels (`claude-trader:<setup-id>`) — nooit dubbel plaatsen
- `kill_switch: true` (of `trade_cycle.py --kill on`) annuleert alles
- elke run gelogd in `signals/execution_log.jsonl`

**Modus is automatisch**: zonder `CTRADER_*` env vars of zonder netwerk naar
`*.ctraderapi.com:5035` draait de cycle in dry-run en rapporteert waarom.

### Live zetten (checklist)

1. App aanmaken op [openapi.ctrader.com](https://openapi.ctrader.com), OAuth
   access token met trading-scope voor het FP Markets-account genereren.
2. In de Claude Code-omgevingsinstellingen als env vars zetten:
   `CTRADER_CLIENT_ID`, `CTRADER_CLIENT_SECRET`, `CTRADER_ACCESS_TOKEN`,
   `CTRADER_ACCOUNT_ID`, `CTRADER_ENV=demo` (eerst demo!), optioneel
   `EXECUTOR_VOLUME_LOTS` (default 0.01).
3. Netwerkpolicy van de omgeving verruimen zodat `demo.ctraderapi.com` en
   `live.ctraderapi.com` op poort **5035** bereikbaar zijn (raw TLS — dit
   loopt níét via de HTTPS-proxy).
4. `pip install ctrader-open-api` in de setup van de omgeving.
5. Eerst een paar dagen `CTRADER_ENV=demo` meedraaien, dan pas `live`.
