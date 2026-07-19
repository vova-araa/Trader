#!/usr/bin/env python3
"""Positiegrootte-calculator voor XAUUSD op basis van accountrisico.

De enige regel die een account beschermt: risk NOOIT meer dan een vast klein
percentage van je saldo per trade. Deze tool rekent dat om naar lots en zegt
eerlijk of een setup te groot is voor je account.

Gebruik:
  python3 scripts/position_size.py --balance 500 --risk 1 --entry 4000 --sl 4013
  python3 scripts/position_size.py -b 500 -r 0.5 -e 3984 -s 3994

XAUUSD-contract: 1.00 lot = 100 oz → een prijsbeweging van $1 = $100 per lot.
Broker-minimum en -stap: 0.01 lot (aanpasbaar met --min-lot).
"""

import argparse
import sys

USD_PER_POINT_PER_LOT = 100.0  # $1 koersbeweging = $100 per 1.0 lot XAUUSD


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-b", "--balance", type=float, required=True,
                   help="accountsaldo in de accountvaluta (USD-equiv)")
    p.add_argument("-r", "--risk", type=float, default=1.0,
                   help="risico per trade in %% van saldo (default 1.0)")
    p.add_argument("-e", "--entry", type=float, required=True)
    p.add_argument("-s", "--sl", type=float, required=True)
    p.add_argument("--min-lot", type=float, default=0.01,
                   help="broker-minimum en -stap (default 0.01)")
    a = p.parse_args()

    sl_points = abs(a.entry - a.sl)
    if sl_points <= 0:
        sys.exit("SL-afstand is 0 — geen geldige trade.")

    risk_budget = a.balance * a.risk / 100.0
    loss_per_lot = sl_points * USD_PER_POINT_PER_LOT
    raw_lots = risk_budget / loss_per_lot
    # naar beneden afronden op de broker-stap: nooit méér risico dan gepland
    steps = int(raw_lots / a.min_lot)
    lots = round(steps * a.min_lot, 2)

    print(f"Saldo:            {a.balance:.2f}")
    print(f"Risico/trade:     {a.risk:.2f}%  =  {risk_budget:.2f}")
    print(f"SL-afstand:       {sl_points:.1f} punten (entry {a.entry} → SL {a.sl})")
    print(f"Verlies per 1 lot:{loss_per_lot:,.0f}")
    print("-" * 40)

    if lots < a.min_lot:
        min_loss = a.min_lot * loss_per_lot
        min_risk_pct = min_loss / a.balance * 100
        print(f"⛔ TE GROOT VOOR DIT ACCOUNT.")
        print(f"   Zelfs de minimale {a.min_lot} lot verliest {min_loss:,.0f} "
              f"= {min_risk_pct:.1f}% van je saldo bij SL.")
        print(f"   Dat is meer dan je {a.risk:.2f}%-limiet. Opties:")
        print(f"   - kies een setup met kleinere SL-afstand, of")
        print(f"   - accepteer het hogere risico bewust, of")
        print(f"   - dit account is te klein om deze setup verantwoord te traden.")
        sys.exit(2)

    actual_loss = lots * loss_per_lot
    actual_pct = actual_loss / a.balance * 100
    print(f"✅ Positiegrootte: {lots} lot")
    print(f"   Verlies bij SL: {actual_loss:,.2f}  ({actual_pct:.2f}% van saldo)")
    print(f"   → zelfs 10 verliezers op rij = {actual_pct * 10:.1f}% drawdown.")


if __name__ == "__main__":
    main()
