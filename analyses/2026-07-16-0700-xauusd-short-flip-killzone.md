# XAUUSD — kill zone-run London open, 2026-07-16 07:00 UTC (09:00 NL)

**Data**: Swissquote spot 4029,3/4029,9 (mid 4029,6). Volledige structuuranalyse: zie `2026-07-16-0640-xauusd-short-flip.md` (20 min eerder, on-demand n.a.v. screenshots gebruiker) — beeld onveranderd, deze run bevestigt en executeert.

## Samenvatting

- **D1 bearish** (momentum 98,7, prijs onder dalende 50-MA); 4× rejection van de 4070-deksel; intraday base 4028 gebroken; overnight low 4018,7; 4041-retest van onderaf verkocht.
- Prijs 4029,6 — onder de flip-zone. Setup van deze kill zone: **flip-short 4052** (zone 4050–4059, 0.618/0.65-cluster op de leg 4070 → 4018,7).
- **Rule 12 actief**: hard cancel 12:00 UTC (US-datavenster 12:30, donderdag jobless claims).

```
SETUP — XAUUSD 1H short (flip-retest na base-break) — B

Entry 4052 | SL 4066 (achter 0.886 op 4064,1) | TP 4019 / 4004 / 3981
RR 2,4 / 3,4 | Invalidatie: H1-close boven 4066; cancel 12:00 UTC
```

Long-scenario alleen mét 15m-CHoCH-bevestiging op 4016–4019 of 4004 (Rule 13).

## Alertniveaus

4052 (zone) · 4066 (dood) · 4019 (TP1) · 4004 (range-onderkant).

## Orders & posities

| Item | Status |
|---|---|
| Flip-short 4052 (B) | `active` t/m 12:00 UTC; executor dry-run: SHORT LIMIT 4052 / SL 4066 / TP 4019 |
| Swing-short 4133 (B) | `active` t/m 17-07 20:00 UTC (gebruiker gaf nog geen bevestiging of de broker-limit nog staat) |
| Open posities | geen — user-long gesloten op -$77 (SL-lock) |

**Executie**: dry-run (geen CTRADER-credentials). WhatsApp met setup + executiestatus verstuurd (B-setup).
