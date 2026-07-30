# 24/7 live data + check elke 15 minuten

De Claude-Code-webomgeving kan dit **niet**: de sandbox-proxy blokkeert directe
HTTP naar de datafeeds (daarom Zapier, met task-quota) én web-Routines mogen maar
**1×/uur**. De oplossing is een **altijd-aan machine** — je laptop (moet aan blijven)
of een goedkope **VPS** (~€4/mnd, echt 24/7). Daar: vrij internet (geen Zapier),
cron elke 15 min, en cTrader poort 5035 bereikbaar voor live-executie.

VPS-opties: <https://www.hetzner.com/cloud> · <https://www.digitalocean.com/products/droplets>

## Twee smaken

**A. Data + executie-loop (zonder Claude)** — beheert/plaatst orders op de setups die
Claude in de repo heeft gezet, met de risk-guard/circuit breaker. Genereert zelf geen
nieuwe setups. Licht en robuust.

**B. Volledige Claude-check elke 15 min** — draait de hele analyse (nieuwe setups,
WhatsApp, executie) via de Claude-Code CLI op cron. Dít geeft "jij hebt 24/7 live data
en checkt elke 15 min" mét verse setups. Vereist de CLI + login op de machine.

---

## Eenmalige installatie (laptop of VPS, Ubuntu/macOS)

```bash
git clone <repo-url> trader && cd trader
git checkout claude/trading-automation-1955jq
pip install ctrader-open-api cffi service_identity
pip install --ignore-installed --upgrade pyopenssl cryptography   # SDK-versiefix
python3 scripts/fetch_xauusd.py     # test: schrijft data/snapshot.json (Zapier-vrij)
```

Env vars voor LIVE (anders dry-run; NOOIT in de repo):
```bash
export CTRADER_CLIENT_ID=...        CTRADER_CLIENT_SECRET=...
export CTRADER_ACCESS_TOKEN=...     CTRADER_ACCOUNT_ID=<ctid>
export CTRADER_ENV=demo             EXECUTOR_VOLUME_LOTS=0.01
```
(zet ze in `~/.bashrc` / `~/.profile` zodat cron ze ziet, of in het cron-blok zelf.)

---

## Smaak A — data + executie, elke 15 min

`scripts/run_local_loop.sh` doet: git pull → verse data (direct) → `trade_cycle.py`
(validatie + **risk-guard/circuit breaker** + executie live/dry + log).

```bash
chmod +x scripts/run_local_loop.sh
crontab -e
# voeg toe (elke 15 min):
*/15 * * * * BRANCH=claude/trading-automation-1955jq PUSH=1 /pad/trader/scripts/run_local_loop.sh >> ~/trader-loop.log 2>&1
```
Cron-hulp: <https://crontab.guru> · `PUSH=1` pusht het log terug naar git.

---

## Smaak B — volledige Claude-analyse, elke 15 min

Installeer de Claude-Code CLI en log in op de machine, dan cron:
```bash
*/15 * * * * cd /pad/trader && claude -p "$(cat docs/loop_prompt.txt)" >> ~/trader-claude.log 2>&1
```
Zet in `docs/loop_prompt.txt` exact de uurlijkse-check-instructie (dezelfde beslisboom
als nu), maar met "elke 15 min" en directe data via `python3 scripts/fetch_xauusd.py`
i.p.v. Zapier. 96 checks/dag valt binnen een normaal abonnement.

---

## Wat je hiermee wint
- **Geen Zapier meer** voor data (geen quota-stops zoals de −24u-blackout).
- **Elke 15 min** i.p.v. 1×/uur.
- **Echte cTrader-executie** (poort 5035 werkt op een vrije verbinding).
- De **risk-guard draait mee**: geen midden-trades, min. stop 12pt, en de circuit
  breaker stopt na 2 verliezen op rij of −3R/week — ook 24/7.

## Volgorde van ingebruikname
1. Eerst **smaak A op demo** (`CTRADER_ENV=demo`) een paar dagen — check of fills,
   SL/TP en de risk-guard kloppen met het log.
2. Dan pas `CTRADER_ENV=live` en klein `EXECUTOR_VOLUME_LOTS`.
3. Smaak B toevoegen als je ook 24/7 verse setups wilt (niet alleen beheer).
