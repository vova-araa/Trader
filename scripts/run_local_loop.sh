#!/usr/bin/env bash
# 24/7 lokale runner — draai elke 15 min via cron op een altijd-aan machine
# (laptop of VPS). Haalt data DIRECT op (geen Zapier, geen task-quota), draait de
# trade-cycle mét risk-guard/circuit breaker, en plaatst live cTrader-orders zodra
# de CTRADER_*-env vars staan. Zonder credentials: dry-run.
#
# Waarom lokaal: de Claude-Code-webomgeving blokkeert directe HTTP naar de
# datafeeds (vandaar Zapier) en web-Routines mogen maar 1x/uur. Een eigen machine
# lost beide op: vrij internet + cron elke 15 min + cTrader poort 5035 bereikbaar.
#
# Installatie (eenmalig):
#   git clone <repo> trader && cd trader && git checkout claude/trading-automation-1955jq
#   pip install ctrader-open-api cffi service_identity
#   pip install --ignore-installed --upgrade pyopenssl cryptography   # SDK-fix
#
# Env vars voor LIVE (anders dry-run) — NOOIT in de repo:
#   CTRADER_CLIENT_ID CTRADER_CLIENT_SECRET CTRADER_ACCESS_TOKEN
#   CTRADER_ACCOUNT_ID CTRADER_ENV=demo|live  EXECUTOR_VOLUME_LOTS=0.01
#
# Cron (elke 15 min):
#   */15 * * * * BRANCH=claude/trading-automation-1955jq /pad/trader/scripts/run_local_loop.sh >> ~/trader-loop.log 2>&1
#
# Optioneel: zet PUSH=1 om het executielog terug te pushen naar git.
set -uo pipefail
cd "$(dirname "$0")/.."

BRANCH="${BRANCH:-claude/trading-automation-1955jq}"
STAMP="$(date -u +%FT%TZ)"

echo "[$STAMP] run-local-loop start (branch $BRANCH)"

# 1. Laatste signalen/regels ophalen (die Claude vanuit de analyse commit)
git pull --quiet --ff-only origin "$BRANCH" 2>/dev/null || echo "  git pull overgeslagen"

# 2. Circuit-breaker-status tonen (informational; de cycle dwingt hem af)
python3 scripts/risk_guard.py status 2>/dev/null | grep -E 'halted|week_r|consecutive' || true

# 3. Cyclus: verse data (direct), validatie + risk-guard, executie (live/dry), log
python3 scripts/trade_cycle.py
CODE=$?

# 4. Optioneel het log terugpushen
if [ "${PUSH:-0}" = "1" ]; then
  git add signals/execution_log.jsonl signals/monitor_log.jsonl 2>/dev/null || true
  git commit -q -m "local-loop: run $STAMP" 2>/dev/null && \
    git push -q origin "$BRANCH" 2>/dev/null || true
fi

echo "[$STAMP] run-local-loop klaar (exit $CODE)"
exit $CODE
