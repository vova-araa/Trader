# Trader

Deze repo bevat mijn discretionaire trading-workflow (SMC/ICT + Fib OTE) en de tooling om chart-analyses (semi-)automatisch te draaien.

## Verplicht voor elke analyse

Lees **CLAUDE_TRADE.md** volledig voordat je een chart of dataset analyseert — inclusief de Learned Rules onderaan. Elke setup volgt exact het template uit sectie 3 van dat bestand. Geen SL of invalidatie = geen setup. Minimum RR 1:2 tot TP1.

## Workflow

1. Haal data op (of ontvang een screenshot van de gebruiker):
   ```
   python3 scripts/fetch_xauusd.py
   ```
   Dit schrijft `data/snapshot.json` en print een compacte samenvatting (candles, swings, auto-fib op de laatste impuls). Vereist netwerk­toegang tot de datafeeds — zie README.md als dit 403's geeft.
2. Analyseer volgens de workflow in CLAUDE_TRADE.md sectie 6 (instrument → HTF-bias → structuur → fib/OTE → template).
3. Sla de analyse op in `analyses/YYYY-MM-DD-<instrument>-<richting>.md`.
4. Alleen bij een A- of B-setup de gebruiker actief notificeren; bij "geen setup" volstaat de log.

## Taal

Nederlands, concreet, met prijzen en RR. Trading-termen mogen in het Engels.
