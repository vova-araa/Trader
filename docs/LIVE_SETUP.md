# Live executie aanzetten — stap voor stap

De pipeline (analyse → `signals/active_setups.json` → `scripts/trade_cycle.py` →
`scripts/executor_ctrader.py`) draait al elke kill zone-run. Hij plaatst échte
limit orders (mét SL + TP1) zodra de vier stappen hieronder zijn gedaan.
Tot die tijd: dry-run.

## Stap 1 — cTrader Open API-app aanmaken (~5 min)

1. Ga naar **https://openapi.ctrader.com** en log in met je cTrader ID
   (zelfde login als je FP Markets cTrader-app).
2. "Applications" → "Add new app". Naam: bijv. `trader-executor`.
   Redirect URI: `https://openapi.ctrader.com/apps/playground` (nodig voor stap 2).
3. Na goedkeuring (meestal direct) heb je een **Client ID** en **Client Secret**.

## Stap 2 — Access token met trading-scope (~5 min)

1. Open op dezelfde site de **Playground** ("Try it now" bij je app).
2. Kies scope **trading** (niet alleen accounts) en doorloop de OAuth-flow;
   selecteer je FP Markets-account (demo én live verschijnen allebei).
3. Je krijgt een **Access Token** (en een Refresh Token — bewaar die ook).
   Let op: het access token verloopt na ±30 dagen; vernieuwen kan met het
   refresh token via dezelfde playground of een curl-call — zet een reminder.

## Stap 3 — ctidTraderAccountId vinden

In de playground: call `ProtoOAGetAccountListByAccessTokenReq` → de response
bevat per account een numeriek `ctidTraderAccountId`. Noteer het ID van je
**demo-account** (eerst demo!) en van je live-account voor later.

## Stap 4 — Omgeving configureren op claude.ai/code

In de **environment settings** van deze omgeving:

1. **Environment variables** (secrets — NOOIT in de chat of repo plakken):
   ```
   CTRADER_CLIENT_ID=...
   CTRADER_CLIENT_SECRET=...
   CTRADER_ACCESS_TOKEN=...
   CTRADER_ACCOUNT_ID=<ctid van je DEMO-account>
   CTRADER_ENV=demo
   EXECUTOR_VOLUME_LOTS=0.07        # jouw gewenste ordergrootte (default 0.01)
   ```
2. **Network policy**: sta `demo.ctraderapi.com` en `live.ctraderapi.com` toe
   op poort **5035** (raw TLS — dit loopt níét via de HTTPS-proxy, dus de
   domein-allowlist moet dit expliciet toestaan of de policy moet ruimer).
3. **Setup script** van de omgeving toevoegen:
   `pip install ctrader-open-api cffi service_identity && pip install --ignore-installed --upgrade pyopenssl cryptography`
   (de laatste twee lossen een versieconflict met de systeem-cryptography op).
4. Container herstarten zodat de nieuwe env vars en policy actief zijn.

## Wat er daarna gebeurt (vanzelf)

- Elke kill zone-run (09:00 & 15:00 NL) én elke on-demand analyse draait
  `trade_cycle.py`. Die detecteert de credentials + bereikbare API-host en
  schakelt zelf naar **LIVE**: A/B-setups worden limit orders met SL en TP1,
  verlopen/geïnvalideerde setups worden geannuleerd op het account.
- De WhatsApp meldt voortaan "order geplaatst @ ..." i.p.v. "dry-run".
- Elke run blijft gelogd in `signals/execution_log.jsonl`.

## Vangrails (blijven altijd actief)

| Vangrail | Waarde |
|---|---|
| Alleen conviction | A of B, status `active` |
| Minimum RR tot TP1 | 1:2 (anders `rejected`) |
| Max risico entry→SL | 30 punten |
| Max gelijktijdige orders | 3 |
| Zonder SL/TP | geen order, punt |
| US-datavenster (Rule 12) | orders expireren vóór 12:00 UTC op data-dagen |
| Kill switch | zeg "stop trading" → alles wordt geannuleerd |
| Idempotent | order-label = setup-id, nooit dubbel geplaatst |

## Volgorde van ingebruikname (advies)

1. **Demo, minimaal 3–5 handelsdagen**: check of fills, SL/TP en cancels op je
   demo-account kloppen met het executielog en de WhatsApp-berichten.
2. Pas daarna `CTRADER_ENV=live` + `CTRADER_ACCOUNT_ID` van je live-account.
3. Begin live met kleine `EXECUTOR_VOLUME_LOTS` en schaal pas op na een week
   zonder verrassingen.

## Wat de executor bewust NIET doet

- TP2/TP3-management en partials: de order krijgt TP1 mee; runners en
  break-even-verplaatsingen blijven handmatig (of latere uitbreiding).
- Marktorders: alles gaat als limit — geen chasing.
- C-setups en trigger-setups ("pas na 15m-CHoCH"): blijven advies totdat de
  bevestiging er is en het signaal als A/B in het bestand staat.
