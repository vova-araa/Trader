# XAUUSD — kill zone-run NY, 2026-07-23 13:00 UTC (15:00 NL)

**Data**: Swissquote spot 4041,4/4042,1 (mid 4041,4) · GC=F future ~4064 → **spread verbreed naar ~22 (contract-roll Aug→Dec; future onbetrouwbaar als niveau, alles op SPOT gekalibreerd)**. 1h-candles vers.

## Marktanalyse — de omkering kwam, precies op 4090

**De 4090-scheidslijn brak en de pullback werd een omkering.** Vanochtend stond de vraag scherp: hold 4107-OTE → long, of 15m-close onder 4090 → short. Het werd het tweede: rond 12:30 UTC (US-data-venster) zakte de prijs door **4090** én door de **4052-flip**, tot **4041 spot** — een daling van ~66 pt vanaf de OTE. De 3-daagse uptrend-structuur is gebroken; het intraday-beeld is **bearish gedraaid**.

- **Intraday/H1: nu bearish** — verlies van 4090/4052, lower low.
- **D1: bearish hoofdstructuur bevestigd** — de lower-high-break bleef uit, verkopers verdedigden.
- **Weekly: bearish** — dit is trend-mee op zowel het snelle als het hoogste tijdsframe. De hele weekrange **3963–4052** is weer open.

**Fib (drop-leg 4107 → 4041, incl. 0.65)** — retracement voor een short-entry: 0.382 = 4066,2 · 0.5 = 4074 · 0.618 = 4081,8. De gebroken **4052-flip** + de 0.382/0.5-bounce-zone **4055–4066** = retest-short-zone (oude support → resistance).

**Momentum (Rule 8)**: 15m/H1 DOWN. Een bounce naar de gebroken zone is de entry — niet chasen op 4041 vlak boven het eerste target.

## Setup — ACTIEF in de pipeline (trend-mee, retest)

```
SETUP — XAUUSD 1H short (breakdown-retest van 4052/4090)

Bias:         Short — weekly + intraday-reversal aligned; 4090/4052 verloren, hele
              weekrange 3963-4052 heropend
Zone:         4052 – 4066 — gebroken flip 4052 + 0.382/0.5 bounce-zone
Confluences:  S/R-flip (weekpivot 4052 nu resistance) + 0.5-retr (4074=SL-grens) +
              verse bearish BOS onder 4090; trend-mee weekly (Rule 13 niet beperkend)

Entry:        4058 (sell limit — retest van bovenaf)
Stop Loss:    4074 — boven 0.5-retr en terug in de gebroken zone
Take Profit 1:4006 — mid-weekrange / oude flip (eerste liquidity)
Take Profit 2:3980 — juli-low-zone
Take Profit 3:3963 — weekrange-bodem (runner)

Risk:Reward:  3,3 (TP1) / 4,7 (TP2)
Invalidatie:  H1-close boven 4074 — dan is de breakdown teruggekocht, terug naar
              4090; expiry 20:00 UTC (geen carry na de US-sessie)
Conviction:   B — trend-mee + clean retest + ruime RR. Geen A omdat de move al
              66 pt oud is (bounce kan ondiep blijven en de fill missen)
```

**Continuation-risico (geen fill)**: zakt de prijs direct door zonder bounce naar 4055 → order vult niet, geen chase (Rule 4); dan is 4006/3980 al bereikt zonder ons en wachten we op de volgende retest.

## Alertniveaus

- **4055 / 4058** — retest-zone (short-entry)
- **4074** — H1-close erboven = setup dood, terug naar 4090
- **4006** — TP1 / mid-weekrange
- **3980 / 3963** — weekrange-bodem (TP2/TP3)

## Orders & posities

| Item | Status |
|---|---|
| Breakdown-retest-short 4058 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: SHORT LIMIT 4058 / SL 4074 / TP 4006 |
| Geprimede long 4107 (ochtend) | vervallen — 4090 brak, long-scenario dood, short-scenario geactiveerd zoals vooraf beschreven |
| Open posities gebruiker | geen bekend |
| Dry-run scorebord | +0,8R over 7 trades; discipline intact |

**Executie**: dry-run (credentials/netwerk niet ingesteld; cTrader-app wacht op KYC). Run gelogd. WhatsApp verstuurd (actieve B-setup). NB: future-spot spread ~22 door contract-roll — future-prijzen deze/komende runs onbetrouwbaar als niveau, **spot is de anker**.
