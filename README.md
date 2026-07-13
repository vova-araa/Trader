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

De Routine draait ma–vr op `0 7,13 * * 1-5` (UTC): 09:00 NL (London open) en 15:00 NL (NY kill zone). Notificatie bij A/B-setup gaat via WhatsApp (Zapier) + push; "geen setup" wordt alleen gelogd in `analyses/`.

Optionele upgrade: TradingView-alerts per e-mail laten sturen — de Routine leest Gmail (Zapier) en neemt geraakte alertniveaus mee in de analyse.

## Semi-automatisch (huidige flow)

Zonder netwerkverruiming werkt de screenshot-flow altijd: stuur 1H + 15m charts in een sessie, Claude leest `CLAUDE_TRADE.md` en levert de setup in het vaste template.

## Disclaimer

Trade-ideeën en analyse, geen financieel advies. De beslissing en het risico zijn aan jou.
