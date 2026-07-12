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

### Vereiste: netwerkpolicy

De datafeeds (`query1.finance.yahoo.com`, `forex-data-feed.swissquote.com`, `stooq.com`) moeten bereikbaar zijn vanuit de Claude Code-omgeving. Op dit moment blokkeert de netwerkpolicy van de omgeving deze hosts (403 via de proxy). Oplossing: in de omgeving-instellingen op claude.ai/code de network policy verruimen (deze domeinen toestaan, of "all"). Zie https://code.claude.com/docs/en/claude-code-on-the-web.

Zodra dat staat kan de Routine aangezet worden (vraag Claude in een sessie in deze repo: "activeer de trade-routine") met schema bijv. `0 7,12 * * 1-5` (UTC ≈ London/NY kill zones, ma–vr).

## Semi-automatisch (huidige flow)

Zonder netwerkverruiming werkt de screenshot-flow altijd: stuur 1H + 15m charts in een sessie, Claude leest `CLAUDE_TRADE.md` en levert de setup in het vaste template.

## Disclaimer

Trade-ideeën en analyse, geen financieel advies. De beslissing en het risico zijn aan jou.
