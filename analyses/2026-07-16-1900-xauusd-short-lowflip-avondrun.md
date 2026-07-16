# XAUUSD — avondrun, 2026-07-16 19:00 UTC (21:00 NL; uitgevoerd ~20:50 na sessieherstart)

**Data**: GC=F 3979,7 · broker ~3976 (spread ~3,7; niveaus in broker-spot). Screenshot gebruiker (M1, 21:44 NL) bevestigt: 3976,04, doorzak met wick naar 3969.

## Marktanalyse

**De reclaim is mislukt en de daily close bevestigt de breakdown**: na de middag-rally naar 4018 gleed de prijs de hele avond omlaag — door de sweep-low (3975,5), wick naar **3969,7**, en de daily sluit ~3976: **onder de juli-low 3981, onder 4000**. Het hammer-scenario van gistermiddag is daarmee dood; dit is een bearish daily close op het laagste niveau van de maand. D1-momentum <100, alle MA's dalend: **volledige bearish alignment de nacht in**.

- Boven ons: **3981–3990** (oude juli-low = verse flip), **3999–4008** (0.618/0.65-cluster + de 4004-flip), **4013** (0.886).
- Onder ons: **3969,7** (vandaag-low), **3950** (rond), **3910** (D1-niveau), daarna 3812-territorium.

**Fib (multi-leg incl. 0.65) op de avond-leg 4018,1 → 3969,7 (broker)**:
0.618 = **3999,6** · 0.65 = **4001,2** · 0.705 = 4003,8 · 0.786 = 4007,7 · 0.886 = 4012,5
Cluster **3999,6–4004**: 0.618/0.65 + de 4004-flip (drie dagen kantelzone) + psych 4000.

**Momentum (Rule 8)**: 15m licht opverend vanaf 3970 (UP-tick) — levert de retracement; entry mét de D1-bias. Timing: buiten kill zones (futures-pauze 21:00–22:00 UTC) — dit is bewust een overnight/Asia-limit, herbeoordeling bij de London-run 07:00 UTC (Rule 12: hard cancel 12:00 UTC vóór het vrijdag-datavenster).

## Dry-run scorebord — eerste winnaar

```
16-07 XAUUSD Short 4016 | 4016 / 4030 / 3981 | +2,5R (dry-run) | bracket-short: gevuld op rally 4018, TP1 geraakt 21:45 NL
16-07 XAUUSD Long  3984 | 3984 / 3972 / 4013 | -1R (dry-run)   | reclaim juli-low faalde: acceptatie eronder i.p.v. squeeze
```

Bracket netto **+1,5R vandaag**; dry-run totaal nu **-0,5R** over 4 gevulde trades (2 procesfout-verliezen die regels werden, 1 structuurverlies, 1 winnaar). Het systeem doet wat het moet doen.

## Setup (overnight)

```
SETUP — XAUUSD 1H short (retest van de gebroken juli-low)

Bias:         Short — bearish daily close onder de juli-low; D1 + intraday aligned;
              elke retracement is tot nader order verkoopwaar
Zone:         3996 – 4008 — 0.618/0.65-cluster + 4004-flip + psych 4000 + de
              gebroken low-zone 3981-3990 als eerste verdediging eronder
Confluences:  0.618 = 3999,6 · 0.65 = 4001,2 (leg 4018→3969,7) + 4004-flip (drie
              dagen dé kantelzone) + psych 4000 + daily breakdown-close;
              15m-momentum UP levert de entry aan

Entry:        4000
Stop Loss:    4013 — achter 0.886 (4012,5)
Take Profit 1:3970 — vandaag-low
Take Profit 2:3950 — ronde niveau / eerstvolgende liquidity
Take Profit 3:3910 — D1-niveau (runner)

Risk:Reward:  2,3 (TP1) / 3,8 (TP2)
Invalidatie:  H1-close boven 4013 — dan is de breakdown-retest gefaald en opent
              4030/4052; hard cancel 17-07 12:00 UTC (Rule 12)
Conviction:   B — volledige alignment + sterk cluster; geen A: Asia is dun, en
              een tweedaagse -60pt-move nodigt uit tot een technische bounce
```

**Long-scenario (alleen mét bevestiging, Rule 13)**: 15m bullish CHoCH boven 3990 → terug-in-range-long naar 4004/4016 — advies, geen order.

## Alertniveaus

- **3990** — eerste flip; acceptatie erboven = bounce krijgt ruimte
- **4000** — zone-touch (entry actief)
- **4013** — H1-close erboven = setup dood
- **3969** — verlies = directe continuation naar 3950

## Orders & posities

| Item | Status |
|---|---|
| Lowflip-short 4000 (B, nieuw) | `active` t/m 17-07 12:00 UTC; executor dry-run: SHORT LIMIT 4000 / SL 4013 / TP 3970 |
| Breakdown-short 4016 | `closed_tp1` — **+2,5R dry-run** ✅ |
| Sweep-long 3984 | `stopped` — -1R dry-run; reclaim faalde |
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC (157 pt boven markt; cancel-discipline H1 > 4143) |
| Open posities gebruiker | geen bekend |

**Executie**: dry-run — netwerkpolicy (poort 5035) en CTRADER-credentials nog niet ingesteld; cTrader-app wacht op KYC ("Submitted" → "Active"). Run gelogd in `signals/execution_log.jsonl`. WhatsApp verstuurd (B-setup).
