# Trader — automatische XAUUSD trade-analyse

Discretionaire SMC/ICT + Fib OTE workflow (zie `CLAUDE_TRADE.md`), met tooling om de analyse automatisch te laten draaien via Claude Code Routines.

## Onderdelen

| Bestand | Doel |
|---|---|
| `CLAUDE_TRADE.md` | De strategie en harde regels — het "brein" van elke analyse |
| `CLAUDE.md` | Instructies zodat elke Claude-sessie in deze repo de strategie volgt |
| `scripts/fetch_xauusd.py` | Haalt live spot + 15m/1h/4h candles op, detecteert swings en berekent auto-fib (OTE) |
| `scripts/superbot.py` | Persistente bot: plaatst SMC/ICT-setups uit `signals/active_setups.json` én draait een losse HFT/scalp-strategie, met gedeelde risicobewaking (marge-check, verlies-pauze, dag-cap) |
| `scripts/executor_ctrader.py` | Oudere, eenmalige executor (handmatige `--dry-run`-checks); niet meer de primaire route |
| `signals/active_setups.json` | Machine-leesbaar signaalbestand + `risk_state` (pauzes, dag-verlieslimiet) |
| `signals/execution_log.jsonl` | Audit-log van elke order/skip-beslissing van de bot |
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

De Routine draait ma–vr op `0 7,13 * * 1-5` (UTC): 09:00 NL (London open) en 15:00 NL (NY kill zone). Notificatie bij A/B-setup gaat via WhatsApp (Zapier) + push; "geen setup" wordt alleen gelogd in `analyses/`.

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
function call" met app-notificatie. Blijft nuttig naast de superbot voor
visuele controle op TradingView zelf.

## Superbot: SMC/ICT + HFT op cTrader (FP Markets / IC Markets)

`scripts/superbot.py` is één persistent proces (geen cron-Routine) dat op
een cTrader-account tegelijk (1) de SMC/ICT-setups uit `active_setups.json`
plaatst/annuleert en (2) een deterministische HFT/scalp-strategie
(Bollinger + RSI mean-reversion op M1, spread- en sessiefilter) draait op
dezelfde rekening, met gedeelde risicobewaking. Zie de docstring in het
script voor alle env vars en vangrails.

**Dit is een bewuste uitzondering op CLAUDE_TRADE.md sectie 0** ("ik druk
niet op de knop") — alleen voor deze automatische pijplijn, met expliciete
vangrails: marge-check, consecutive-loss circuit breaker per strategie,
automatische dag-verlieslimiet, en `EXECUTOR_ARMED=yes` als extra slot
bovenop credentials voor live geld.

**Moet 24/5 draaien op eigen infrastructuur** (VPS o.i.d.) — een Claude
Code-sessie of Routine stopt na inactiviteit en is niet geschikt om de bot
zelf te hosten. De Routine kan wel de SMC/ICT-analyse (kill zones) blijven
verzorgen door `active_setups.json` bij te werken; de superbot leest dat
bestand elke cyclus opnieuw.

**Credentials regelen (cTrader Open API):**
1. Registreer een app op [openapi.ctrader.com](https://openapi.ctrader.com)
   → levert `CTRADER_CLIENT_ID` + `CTRADER_CLIENT_SECRET`.
2. Doorloop de OAuth-authorize-flow voor je (demo-)account → levert
   `CTRADER_ACCESS_TOKEN`.
3. `CTRADER_ACCOUNT_ID` is je numerieke `ctidTraderAccountId` (zichtbaar in
   de cTrader-app of via de API).
4. Zet alle vier plus `CTRADER_ENV=demo` als env vars op de machine die de
   bot host — **nooit in code, chat of repo**.

Verifieer bij de eerste live/demo-run de geplaatste order-grootte handmatig
in de cTrader-UI — de volume-conversie is gebaseerd op de officiële
protobuf-specificatie maar nog niet tegen een echte server getest.
