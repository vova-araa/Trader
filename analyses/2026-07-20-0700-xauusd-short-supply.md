# XAUUSD — kill zone-run London open, 2026-07-20 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4005,1/4005,8 (mid 4005,4) · GC=F future 4006,9 → spread ~1,5 (roll — future ≈ spot). Candles 1h (5d) vers. Maandag-dagrange tot nu: high 4034,2 / low 3986,5.

## Marktanalyse

**Weekend-reopen zonder gap van betekenis**: goud opende ~4001 en handelt maandag in een strakke range **3986–4034**. Prijs 4005, midden-boven. De 4028–4034-supply (Friday-reversal-high 4029 + range-top) is bij de open getest — **high 4034,2, direct terug naar 4005**: eerste rejection is er al.

- **D1**: onverminderd bearish (top 5450, onder dalende MA's, RSI 39,6) — de bounce van 3963 is een correctie ín een downtrend.
- **H4**: lower highs intact; 4030–4052 is de supply waar de vorige twee legs ook draaiden.
- **M30/M15**: range 3963–4034; 4005 is mid. Geen edge op dit moment.

**Fib (multi-leg incl. 0.65) op de bounce-leg 3963 → 4034 (spot)**, retracement voor een short gemeten van de top omlaag — maar relevanter is de **supply-confluence**: 4028–4040 = Friday-high + range-top + dalende H4-MA. De 0.618/0.65 van de grotere daling (4090 → 3963) ligt op **4041/4046** — dat verzegelt de SL-zone.

**Momentum (Rule 8)**: H1 vlak rond 100, geen doorzettende koopdruk boven 4005. **Timing**: London kill zone actief ✓; maandag lichte agenda, geen groot US-datavenster gepland (Rule 12 blijft standaard: expiry 20:00 UTC).

## Setup

```
SETUP — XAUUSD 1H short (supply-retest, trend-mee)

Bias:         Short — D1 + H4 bearish; de bounce van 3963 is correctie, 4028-4040
              is de supply waar de vorige legs draaiden
Zone:         4028 – 4040 — Friday-high 4029 + range-top 4034 + dalende H4-MA
Confluences:  supply/OB van de vorige lower highs + 0.618/0.65 grotere daling op
              4041/4046 (verzegelt SL) + eerste rejection al geprint (4034→4005);
              H1-momentum vlak = geen koopdruk boven de zone

Entry:        4030
Stop Loss:    4046 — boven de 4034-high én de fib-zone
Take Profit 1:3986 — maandag-low (eerste liquidity)
Take Profit 2:3968 — range-bodem
Take Profit 3:3950 — extensie (runner)

Risk:Reward:  2,8 (TP1) / 3,9 (TP2)
Invalidatie:  H1-close boven 4046 — dan is de correctie groter en opent 4070/4090;
              expiry 20:00 UTC
Conviction:   B — trend-mee, clean level, ruime RR; A bij een nette 15m-rejection
              in de zone. Geen A nu omdat prijs mid-range staat, niet in de zone
```

**Long-scenario (alleen mét bevestiging, Rule 13)**: 15m bullish CHoCH op 3963–3986 → tegen-trend bounce richting 4005/4030 — advies, geen order (counter-D1).

## Alertniveaus

- **4030** — zone-touch (short actief)
- **4046** — H1-close erboven = setup dood, 4070 in beeld
- **4000** — mid-range scharnier
- **3986 / 3963** — maandag-low + range-bodem; break = continuation naar 3950

## Orders & posities

| Item | Status |
|---|---|
| Supply-short 4030 (B, nieuw) | `active` t/m 20:00 UTC; executor dry-run: SHORT LIMIT 4030 / SL 4046 / TP 3986 |
| Swing-short 4133 | `expired` (verlopen 17-07, nooit gevuld) |
| Open posities | geen |
| Dry-run scorebord (week 29) | +0,8R over 6 trades (2W/4L, avg win +2,4R / avg loss -1R) |

## Risk-note voor de gebruiker (account bijna leeg)

De gebruiker gaf aan dat één verlies het account leegt. Deze setup is trend-mee en clean, **maar dat verandert het advies niet**: bij een account dat geen enkele -1R kan hebben, is óók deze short te riskant om live te nemen. Verantwoorde route: op **demo** meelopen (waar deze pipeline al draait) en pas live met correcte size zodra 1 verlies ≤ ~1% van het saldo is (`scripts/position_size.py`). Ter illustratie: op een €2000-account met SL 16 pt = 0,01 lot = 0,80% risk (oké); op €500 zou zelfs 0,01 lot al ~3% zijn — dan is het account te klein voor deze setup.

**Executie**: dry-run (credentials/netwerk nog niet ingesteld; cTrader-app wacht op KYC). Run gelogd. WhatsApp verstuurd (B-setup, mét sizing-reminder).
