# XAUUSD — kill zone-run NY, 2026-07-17 13:00 UTC (15:00 NL) — post-data

**Data**: Swissquote spot 3967,6/3968,3 (mid 3968,0) · GC=F 3968 — **future-spread ingeklapt naar ~0 (contract-roll)**, futures ≈ spot vanaf nu. Candles 15m (1d) vers.

## Marktanalyse

**TP1 geraakt: +2,3R.** De 12:30-data dumpte goud van ~3993 naar **3963** — dwars door de TP1 (3970) van de lopende short 4000. Positie dicht op TP1: **tweede winnaar**, scorebord nu **+1,8R** over 5 gevulde dry-run-trades. (Rule 12-discipline: de SL stond conform advies op breakeven het venster in — de TP won de race.)

**Structuur**: verse lower low onder de juli-low — derde bearish datadag op rij, D1-trend vol in controle. De pre-data range-bodem **3984** is nu de flip van bovenaf, en het 0.618/0.65-cluster van de dump-leg (3995,9 → 3963) valt er exact op: 0.618 = 3983,3 · 0.65 = 3984,4 · 0.705 = 3986,2 · 0.786 = 3988,9 · 0.886 = 3992,1. Prijs 3968, milde bounce vanaf de low.

**Boven**: 3984–3989 (flip + cluster), 3992–3994 (0.886), 4000 (oude entry, nu psych-deksel). **Onder**: 3963 (data-low), **3950**, 3930, 3910 (D1).

**Momentum (Rule 8)**: 15m DOWN (verse dump), de bounce levert de entry aan — mét de D1-bias. NY kill zone actief ✓. **Events**: 14:00 UTC UMich-sentiment (klein, binnen validity — genoteerd); **hard expiry 20:00 UTC: géén pending orders het weekend over** (gap-risico).

## Setup

```
SETUP — XAUUSD 1H short (vrijdag-flip na datadump)

Bias:         Short — D1-trend in controle (3e bearish datadag), verse BOS onder
              de juli-low; elke retracement naar de flip is verkoopwaar
Zone:         3983 – 3989 — pre-data range-bodem 3984 als flip + 0.618/0.65-cluster
Confluences:  0.618 = 3983,3 · 0.65 = 3984,4 (dump-leg 3995,9→3963) + S/R-flip van
              de ochtend-range + psych 4000 als hoger deksel + NY kill zone;
              15m-momentum UP (bounce) levert de entry aan

Entry:        3984
Stop Loss:    3994 — achter 0.886 (3992,1)
Take Profit 1:3963 — data-low (eerste liquidity)
Take Profit 2:3950 — ronde niveau
Take Profit 3:3930 — extensie (runner; 3910 D1 blijft de swing-magneet)

Risk:Reward:  2,1 (TP1) / 3,4 (TP2)
Invalidatie:  H1-close boven 3994 — dan is de dump gekocht en opent 4000/4013;
              hard expiry 20:00 UTC (weekend — geen carry)
Conviction:   B — HTF-aligned + kill zone + strak cluster; geen A: vrijdagmiddag
              na -130pt weekverlies = squeeze/short-covering-risico voor de close
```

**Long-scenario (alleen mét bevestiging, Rule 13)**: 15m bullish CHoCH op 3958–3963 → covering-bounce richting 3984 — advies, geen order.

## Alertniveaus

- **3984** — zone-touch (entry actief)
- **3994** — H1-close erboven = setup dood
- **3963** — TP1 / data-low; break = 3950 direct
- **20:00 UTC** — alles wat pending is gaat eruit (weekend)

## Orders & posities

| Item | Status |
|---|---|
| Fridayflip-short 3984 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: SHORT LIMIT 3984 / SL 3994 / TP 3963 |
| Lowflip-short 4000 | `closed_tp1` — **+2,3R** ✅ (gevuld 03:20, TP1 in de datadump) |
| Swing-short 4133 (B) | verloopt vanavond 20:00 UTC (nooit gevuld) |
| Dry-run scorebord | **+1,8R totaal**: +2,5R · +2,3R · -1R · -1R · -1R |

**Executie**: dry-run (credentials/netwerk wachten op gebruiker; cTrader-app wacht op KYC). Run gelogd. WhatsApp verstuurd (B-setup + TP-melding).
