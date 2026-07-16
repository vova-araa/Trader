#!/usr/bin/env python3
"""Preflight-check voor live executie: verifieert alle voorwaarden en print
een checklist met wat er nog mist. Draai na elke setup-stap opnieuw.

Gebruik: python3 scripts/check_live_ready.py
Exit 0 = alles klaar voor live; exit 1 = er mist nog iets (zie output).
"""

import json
import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRED_VARS = ("CTRADER_CLIENT_ID", "CTRADER_CLIENT_SECRET",
             "CTRADER_ACCESS_TOKEN", "CTRADER_ACCOUNT_ID")
HOSTS = {"demo": "demo.ctraderapi.com", "live": "live.ctraderapi.com"}
PORT = 5035

ok_all = True


def check(label, passed, hint=""):
    global ok_all
    mark = "OK " if passed else "MIS"
    print(f"[{mark}] {label}" + ("" if passed else f"  ->  {hint}"))
    if not passed:
        ok_all = False
    return passed


env = os.environ.get("CTRADER_ENV", "demo")
print(f"=== Preflight live executie (CTRADER_ENV={env}) ===\n")

# 1. Credentials
for var in CRED_VARS:
    check(f"env var {var}", bool(os.environ.get(var)),
          "zet deze in de omgevingsinstellingen (claude.ai/code) en herstart de container")
check("CTRADER_ENV geldig", env in HOSTS, "zet CTRADER_ENV=demo of live")
if os.environ.get("CTRADER_ACCOUNT_ID"):
    check("CTRADER_ACCOUNT_ID numeriek",
          os.environ["CTRADER_ACCOUNT_ID"].isdigit(),
          "gebruik het numerieke ctidTraderAccountId uit de playground, niet je loginnaam")

# 2. SDK
try:
    import ctrader_open_api  # noqa: F401
    check("ctrader-open-api SDK geïnstalleerd", True)
except BaseException as e:  # noqa: BLE001 — pyo3 kan met PanicException crashen
    check("ctrader-open-api SDK geïnstalleerd", False,
          "voeg 'pip install ctrader-open-api cffi service_identity' toe aan "
          f"het setup-script van de omgeving ({type(e).__name__})")

# 3. Netwerk
host = HOSTS.get(env, HOSTS["demo"])
try:
    socket.create_connection((host, PORT), timeout=6).close()
    check(f"netwerk {host}:{PORT} bereikbaar", True)
except OSError as e:
    check(f"netwerk {host}:{PORT} bereikbaar", False,
          f"verruim de netwerkpolicy van de omgeving voor poort 5035 ({e})")

# 4. Signaalbestand + volume
sig = ROOT / "signals" / "active_setups.json"
try:
    data = json.loads(sig.read_text())
    n = sum(1 for s in data.get("setups", [])
            if s.get("status") == "active" and s.get("conviction") in ("A", "B"))
    check(f"signaalbestand geldig ({n} actieve A/B-setups)", True)
    check("kill_switch uit", not data.get("kill_switch"),
          "python3 scripts/trade_cycle.py --kill off")
except Exception as e:  # noqa: BLE001
    check("signaalbestand geldig", False, str(e))

vol = os.environ.get("EXECUTOR_VOLUME_LOTS", "0.01")
print(f"\nOrdergrootte: {vol} lots (aanpasbaar via EXECUTOR_VOLUME_LOTS)")

print("\n=== Resultaat ===")
if ok_all:
    print(f"KLAAR VOOR {'LIVE' if env == 'live' else 'DEMO'}: de eerstvolgende "
          "trade_cycle-run plaatst echte orders.")
    if env == "live":
        print("LET OP: CTRADER_ENV=live — weet je zeker dat demo al getest is?")
else:
    print("Nog niet klaar — los de [MIS]-punten hierboven op en draai dit "
          "script opnieuw (vraag: 'check live').")
sys.exit(0 if ok_all else 1)
