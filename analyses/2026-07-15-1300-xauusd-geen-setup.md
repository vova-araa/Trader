# XAUUSD — kill zone-run NY, 2026-07-15 13:00 UTC (15:00 NL) — geen setup

**Data**: Swissquote spot 4064,6/4065,3 (mid 4065,0) · GC=F future 4072,9 → spread ~8 (niveaus in spot). Candles 15m (2d) vers.

## Marktanalyse

Tweede news-spike in twee dagen: om **12:45 UTC** knalde de markt van ~4034 naar **4070 spot** (future high 4078,2; volume 7384 vs ~800 gemiddeld — duidelijk data-gedreven, het klassieke US 12:30-venster). Daarmee is het beeld wezenlijk veranderd:

- **Higher low staat**: 13-jul low 3981 → overnight low ~4016. De dip onder 4021 was een sweep, geen acceptatie.
- **Prijs heeft de 4052–4062 supply gereclaimd** en handelt erboven — de tweede krachtige bullish impuls vanaf de demand-regio 4004–4021.
- **H4-bias blijft formeel bearish** (lower highs 4394 → 4206 → 4143 intact), maar de bearish case verzwakt zichtbaar: twee violente rejections van de onderkant + higher low. Boven 4107 (CPI-high) is de korte-termijn omslag compleet; boven 4143 kantelt H4 echt.
- Boven ons: **4084–4093** (0.786/0.886-cluster van beide down-legs + gisteren-supply), **4107**, dan **4124–4143**. Onder ons: **4052** (gereclaimde flip), **4040**, **4021/4016**, **4004**.

**Momentum (Rule 8)**: 15m/H1 momentum sterk UP (verse impuls). **Geen setup nu** — 15 minuten na een news-spike een order plaatsen is chasen (Rule 4 + verse Rule 12). De markt zit mid-range tussen de spike-high en de flip.

## Dry-run journal — de vangrails verdienen zichzelf terug

```
15-07 XAUUSD Short 4048 | 4048 / 4058 / 4021 | -1R (dry-run) | PROCESFOUT → Learned Rule 12:
pending order liep onbeschermd het 12:30-14:00 UTC US-datavenster in en werd gesteamrolld
```

**Nieuwe Learned Rules toegevoegd aan CLAUDE_TRADE.md**:
- **Rule 12 [TIMING]**: pending orders nooit zonder event-check door het US-datavenster laten lopen (CPI-discipline van 14-07 werkte; 15-07 vergeten → -1R).
- **Rule 13 [ENTRY]**: counter-HTF entries nooit als blinde limit in de OTE — eerst 15m-CHoCH-bevestiging (les van de OTE-long 4046).

Dry-run totaal: 2 trades, -2R, beide procesfouten die nu regels zijn. Dit is precies waarom er eerst zonder geld wordt gedraaid.

## Scenario's + triggers (geen orders)

**Short-scenario (voorkeur zolang H4-bias staat)**: touch van **4084–4093** (0.786 leg 4102,6→4016 op 4084,1 + 0.886 op 4092,7 + supply van gisteren) gevolgd door een **15m bearish CHoCH** → short richting 4052/4040, runner 4021. Zonder rejection-bevestiging: niets doen — de swing-short 4133 dekt het diepere scenario al af.

**Long-scenario (alleen mét bevestiging, Rule 13)**: pullback naar **4042–4050** (OTE van de verse impuls 4033,8→4070,2: 0.618 = 4047,7 · 0.65 = 4046,5 · 0.705 = 4044,5) gevolgd door een **15m bullish CHoCH** → long richting 4085/4107. Blinde limit verboden.

**Omslag-signaal**: H1-close boven **4107** = CPI-high geveegd én geaccepteerd → dan is long-op-pullback het primaire speelboek en moet de swing-short 4133 kritisch herbeoordeeld worden (cancel-discipline blijft H1-close > 4143).

## Alertniveaus

- **4084** — onderkant short-zone; kijk naar rejection of acceptatie
- **4107** — CPI-high; H1-close erboven = omslag
- **4052** — gereclaimde flip; verlies = spike gefaald, terug naar 4040/4021
- **4133/4143** — swing-short zone + cancel-grens

## Orders & posities

| Item | Status |
|---|---|
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC — de route ernaartoe is door de spike een stuk korter geworden (~70 pt); cancel-discipline: H1-close boven 4143 |
| Retest-short 4048 | `stopped` — dry-run -1R in de 12:45-spike; les = Rule 12 |
| Open positie gebruiker | BUY 0.2 @ 4004,33 — als de SL gisteren naar 4038–4040 is opgetrokken: overnight uitgestopt ~+$680–700. Als hij nog loopt: nu ~+$1.200 — trek de SL dan NU minimaal naar 4052 (locked ~+$950) met de spike in de rug |

**Executie**: dry-run (geen CTRADER-credentials). Alleen de swing-short staat nog als pending signaal; run gelogd in `signals/execution_log.jsonl`. Geen WhatsApp (geen nieuwe A/B-setup, conform afspraak).
