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

## Executie-pipeline

Bij elke A/B-setup ook `signals/active_setups.json` bijwerken (zelfde niveaus
als het template; C-setups NIET — die blijven advies). `kill_switch: true`
zetten als de gebruiker "stop trading" zegt.

De echte executie loopt via **`scripts/superbot.py`** — één persistent
proces (géén cron/Routine-cyclus) dat op FP Markets/IC Markets (cTrader Open
API) tegelijk (1) de SMC/ICT-limit-orders uit `active_setups.json` plaatst/
annuleert en (2) een losse, in code vastgelegde HFT/scalp-strategie draait.
Dit script moet 24/5 op eigen infrastructuur (VPS) draaien — een
Claude-Routine kan alleen de kill zone-analyse blijven verzorgen (schrijft
naar `active_setups.json`), niet de HFT-tak, want die moet continu reageren.

Vangrails in de superbot (zie de docstring van het script voor alle env
vars): marge-check voor elke order, een consecutive-loss circuit breaker die
per strategie (SMC/HFT apart) pauzeert na een verlies-reeks, een automatische
dag-verlieslimiet die `kill_switch` zet, en `EXECUTOR_ARMED=yes` als extra
vangrail bovenop credentials voor live. `kill_switch: true` sluit zowel
pending orders als open posities van de bot.

Credentials (nooit in code/repo, alleen als env var in de omgeving die de
bot host): `CTRADER_CLIENT_ID/SECRET/ACCESS_TOKEN/ACCOUNT_ID`,
`CTRADER_ENV=demo|live`. Zolang die er niet zijn, kan de bot niet verbinden.

`scripts/executor_ctrader.py` (de oudere, eenmalige executor) blijft bestaan
voor handmatige `--dry-run`-checks maar is niet meer de primaire route.
