#!/usr/bin/env python3
"""Trade-cycle orchestrator: één entrypoint voor de geautomatiseerde run.

Stappen per cycle:
  1. Signalen valideren (signals/active_setups.json):
     - verlopen setups krijgen status "expired"
     - A/B-setups met RR < 2.0 tot TP1 of onlogische niveaus worden geweigerd
       (status "rejected" + reden) — regel 1/2 uit CLAUDE_TRADE.md sectie 4
  2. Verse data proberen op te halen (scripts/fetch_xauusd.py, mag falen —
     in Claude Code-omgevingen loopt data via de Zapier MCP in de sessie)
  3. Executie: scripts/executor_ctrader.py
     - live zodra CTRADER_* env vars aanwezig zijn ÉN de API-host bereikbaar is
     - anders automatisch --dry-run (er gaat nooit stilletjes niets gebeuren:
       de gekozen modus staat in de output en in het executielog)
  4. Runrecord appenden aan signals/execution_log.jsonl (audit trail)

Kill switch:
  python3 scripts/trade_cycle.py --kill on|off
  Zet kill_switch in het signaalbestand. Bij "on" annuleert de eerstvolgende
  executor-run alle openstaande executor-orders en plaatst hij niets.

Overige flags:
  --dry-run   forceer dry-run, ook mét credentials
  --no-fetch  sla de datafetch over (bijv. als de sessie al verse data heeft)
"""

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import risk_guard  # noqa: E402  (mechanische vangrails, gedeeld met de executor)

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "signals" / "active_setups.json"
EXEC_LOG = ROOT / "signals" / "execution_log.jsonl"

MIN_RR = 2.0  # harde regel: minimaal 1:2 tot TP1
CRED_VARS = ("CTRADER_CLIENT_ID", "CTRADER_CLIENT_SECRET",
             "CTRADER_ACCESS_TOKEN", "CTRADER_ACCOUNT_ID")
HOSTS = {"demo": "demo.ctraderapi.com", "live": "live.ctraderapi.com"}
PORT = 5035


def now_utc():
    return datetime.now(timezone.utc)


def load():
    return json.loads(SIGNALS.read_text())


def save(data):
    data["updated_utc"] = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    SIGNALS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def set_kill_switch(state: bool):
    data = load()
    data["kill_switch"] = state
    save(data)
    print(f"kill_switch = {state} geschreven naar {SIGNALS}")


def validate_signals():
    """Markeer verlopen/ongeldige setups. Geeft (n_active, wijzigingen) terug."""
    data = load()
    changed, notes = False, []
    now = now_utc()
    for s in data.get("setups", []):
        if s.get("status") != "active":
            continue
        valid_until = datetime.fromisoformat(
            s["valid_until_utc"].replace("Z", "+00:00"))
        if valid_until <= now:
            s["status"] = "expired"
            notes.append(f"{s['id']}: verlopen ({s['valid_until_utc']})")
            changed = True
            continue
        risk = abs(s["entry"] - s["stop_loss"])
        tps = s.get("take_profits") or []
        reward = abs(tps[0] - s["entry"]) if tps else 0.0
        problem = None
        if risk <= 0 or not tps:
            problem = "geen geldige SL/TP"
        elif reward / risk < MIN_RR:
            problem = f"RR {reward / risk:.2f} < {MIN_RR} tot TP1"
        elif s["direction"] == "short" and not (
                s["stop_loss"] > s["entry"] > tps[0]):
            problem = "short maar niveaus niet SL > entry > TP1"
        elif s["direction"] == "long" and not (
                s["stop_loss"] < s["entry"] < tps[0]):
            problem = "long maar niveaus niet SL < entry < TP1"
        if not problem:
            problem = risk_guard.structural_reject_reason(s)  # regime/rand/min-stop
        if problem and s.get("conviction") in ("A", "B"):
            s["status"] = "rejected"
            s["rejected_reason"] = problem
            notes.append(f"{s['id']}: GEWEIGERD — {problem}")
            changed = True
    if changed:
        save(data)
    n_active = sum(1 for s in data.get("setups", [])
                   if s.get("status") == "active"
                   and s.get("conviction") in ("A", "B"))
    return data, n_active, notes


def try_fetch():
    try:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "fetch_xauusd.py")],
            capture_output=True, text=True, timeout=90)
        ok = r.returncode == 0
        return ok, (r.stdout if ok else r.stderr).strip()[-500:]
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def api_reachable(env: str) -> bool:
    try:
        socket.create_connection((HOSTS.get(env, HOSTS["demo"]), PORT),
                                 timeout=6).close()
        return True
    except OSError:
        return False


def run_executor(dry: bool):
    cmd = [sys.executable, str(ROOT / "scripts" / "executor_ctrader.py")]
    if dry:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    args = sys.argv[1:]
    if "--kill" in args:
        state = args[args.index("--kill") + 1].lower()
        if state not in ("on", "off"):
            sys.exit("gebruik: --kill on|off")
        set_kill_switch(state == "on")
        return

    record = {"time_utc": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")}

    data, n_active, notes = validate_signals()
    for n in notes:
        print(f"VALIDATIE: {n}")
    record["validation"] = notes
    record["active_ab_setups"] = n_active
    record["kill_switch"] = bool(data.get("kill_switch"))

    if "--no-fetch" not in args:
        ok, summary = try_fetch()
        print(f"DATA: {'ok' if ok else 'fetch faalde (sessie levert data via MCP)'}")
        record["data_fetch"] = "ok" if ok else "failed"

    # Circuit breaker (verlieslimiet) — rapporteer en blokkeer live plaatsing.
    can, halt_reason, rstate = risk_guard.can_trade()
    record["risk_state"] = rstate
    if not can:
        print(f"RISICO-HALT: {halt_reason} "
              f"(week {rstate['week_r']:+.2f}R / {rstate['week_pnl']:+.2f}, "
              f"{rstate['consecutive_losses']} verlies op rij). "
              f"Geen nieuwe orders tot hervat/weekrol.")

    env = os.environ.get("CTRADER_ENV", "demo")
    have_creds = all(os.environ.get(k) for k in CRED_VARS)
    forced_dry = "--dry-run" in args
    reachable = have_creds and not forced_dry and api_reachable(env)
    dry = forced_dry or not have_creds or not reachable

    if forced_dry:
        reason = "geforceerd via --dry-run"
    elif not have_creds:
        reason = "CTRADER_* credentials ontbreken in de omgeving"
    elif not reachable:
        reason = f"{HOSTS.get(env)}:{PORT} niet bereikbaar (netwerkpolicy)"
    else:
        reason = f"credentials + netwerk ok — LIVE op {env}"
    print(f"MODUS: {'dry-run' if dry else 'LIVE (' + env + ')'} — {reason}")
    record["mode"] = "dry-run" if dry else f"live-{env}"
    record["mode_reason"] = reason

    code, output = run_executor(dry)
    print(output)
    record["executor_exit"] = code
    record["executor_output"] = output[-1000:]

    EXEC_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EXEC_LOG.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Log: {EXEC_LOG}")
    if code != 0:
        sys.exit(code)


if __name__ == "__main__":
    main()
