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

## Taal

Nederlands, concreet, met prijzen en RR. Trading-termen mogen in het Engels.

## Executie-pipeline (geautomatiseerd; live pas na credentials van de gebruiker)

Bij elke A/B-setup:

1. `signals/active_setups.json` bijwerken (zelfde niveaus als het template;
   C-setups NIET — die blijven advies).
2. `python3 scripts/trade_cycle.py` draaien. Die valideert de signalen
   (verlopen → expired, RR < 1:2 tot TP1 → rejected), kiest zelf de modus —
   LIVE zodra de CTRADER_*-credentials in de omgeving staan én de API-host
   bereikbaar is, anders automatisch dry-run — en logt elke run in
   `signals/execution_log.jsonl`. Commit het log en het signaalbestand mee.

Credentials als env vars (NOOIT in code/repo): CTRADER_CLIENT_ID/SECRET/
ACCESS_TOKEN/ACCOUNT_ID, CTRADER_ENV=demo|live. Voor live executie moet de
netwerkpolicy van de omgeving `demo.ctraderapi.com`/`live.ctraderapi.com`
poort 5035 toestaan (raw TLS, niet via de HTTPS-proxy).

Kill switch: `python3 scripts/trade_cycle.py --kill on` zodra de gebruiker
"stop trading" zegt — de eerstvolgende run annuleert alle executor-orders.
