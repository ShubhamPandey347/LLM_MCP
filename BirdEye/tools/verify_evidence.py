#!/usr/bin/env python3
"""Verify BirdEye's execution evidence chain on this machine.

Read-only with respect to the repository: it executes one bounded command that
writes a unique marker into a disposable directory, then proves the result
independently. It does not modify source, configuration or installed services.

Claims checked
  1. The real tool-call path executes a bounded argv command.
  2. The effect is real: the marker bytes are read back independently of BirdEye.
  3. A receipt exists and its on-disk hash matches the returned evidence.
  4. The journal record is correlated by request_id and task_id.
  5. The record survives a process restart and is readable by a new process.

Claims deliberately NOT checked here (they need the live client/service, and are
reported as UNVERIFIED rather than assumed):
  - stdio/HTTP MCP client wiring and tool listing through an actual client.
  - watcher indexing latency.
  - reboot/logon persistence of a background gateway.
  - Windows service or scheduled-task ownership.

Usage
  python tools/verify_evidence.py                 # uses BirdEye/config.json
  python tools/verify_evidence.py --json          # machine-readable summary
  python tools/verify_evidence.py --acceptance-dir D:\\acceptance-temp
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

BIRDEYE_DIR = Path(__file__).resolve().parents[1]
if str(BIRDEYE_DIR) not in sys.path:
    sys.path.insert(0, str(BIRDEYE_DIR))

RESULTS: list[tuple[str, str, str]] = []


def record(claim: str, status: str, detail: str) -> None:
    RESULTS.append((claim, status, detail))
    print(f"[{status:10}] {claim}\n             {detail}")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the BirdEye execution evidence chain")
    parser.add_argument("--config", default=str(BIRDEYE_DIR / "config.json"))
    parser.add_argument("--acceptance-dir", default=None,
                        help="Disposable directory for the marker (default: a new temp dir)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    print(f"BirdEye source: {BIRDEYE_DIR}")
    print(f"config:         {config_path}")
    for name in ("workspace_bridge.py", "execution_evidence.py", "mcp_server.py"):
        target = BIRDEYE_DIR / name
        if target.is_file():
            print(f"  {name:24} sha256={sha256_file(target)}")
    print()

    if not config_path.is_file():
        record("configuration present", "FAIL",
               f"{config_path} does not exist; run scripts/render_config.py and apply the candidate first")
        return _finish(args.json)
    record("configuration present", "PASS", f"{config_path} readable")

    if args.acceptance_dir:
        acceptance = Path(args.acceptance_dir).expanduser().resolve()
        acceptance.mkdir(parents=True, exist_ok=True)
        disposable = False
    else:
        acceptance = Path(tempfile.mkdtemp(prefix="birdeye-acceptance-"))
        disposable = True

    # Run in a fresh subprocess so the check exercises the same import path a client uses.
    marker = acceptance / f"marker-{uuid.uuid4().hex}.txt"
    token = f"bird-verify-{uuid.uuid4()}"
    request_id = f"req-{token}"
    task_id = f"task-{token}"

    payload = {"workspace": str(acceptance), "argv": [
        sys.executable, "-c",
        f"from pathlib import Path;Path({str(marker)!r}).write_text({token!r},encoding='utf-8')",
    ], "request_id": request_id, "task_id": task_id, "timeout_seconds": 60}

    call = (
        "import json,sys;"
        f"sys.path.insert(0,{str(BIRDEYE_DIR)!r});"
        "import mcp_server;"
        f"print(json.dumps(mcp_server.invoke('workspace_run', json.loads({json.dumps(json.dumps(payload))})),"
        "ensure_ascii=False))"
    )
    try:
        completed = subprocess.run([sys.executable, "-c", call], cwd=str(BIRDEYE_DIR),
                                   capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        record("execution completes", "FAIL", "tool call exceeded 300s")
        return _finish(args.json)

    if completed.returncode != 0 or not completed.stdout.strip():
        record("execution completes", "FAIL",
               f"exit={completed.returncode} stderr={completed.stderr.strip()[:300]}")
        return _finish(args.json)

    result = json.loads(completed.stdout.strip().splitlines()[-1])
    record("execution completes", "PASS" if result.get("ok") else "FAIL",
           f"exit_code={result.get('exit_code')} classification={result.get('classification')} "
           f"request_id={result.get('request_id')}")

    # 2. Independent effect check: read the bytes ourselves.
    actual = marker.read_text(encoding="utf-8") if marker.exists() else None
    record("effect is real and independently read", "PASS" if actual == token else "FAIL",
           f"marker={marker} bytes_match={actual == token}")

    # 3. Receipt integrity: hash on disk must equal the hash in the returned evidence.
    evidence = result.get("execution_evidence") or {}
    history = result.get("execution_history") or {}
    receipt_path = history.get("receipt_path")
    if receipt_path and Path(receipt_path).is_file():
        on_disk = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
        same = on_disk.get("execution_evidence_sha256") == evidence.get("execution_evidence_sha256")
        record("receipt persisted and hash matches", "PASS" if same else "FAIL",
               f"{receipt_path}\n             sha256={evidence.get('execution_evidence_sha256')} "
               f"overall_evidence={evidence.get('overall_evidence')}")
    else:
        record("receipt persisted and hash matches", "FAIL",
               f"no receipt file: {history.get('error') or receipt_path or 'execution_history missing'}")

    record("request identity preserved in receipt",
           "PASS" if evidence.get("request_id") == request_id else "FAIL",
           f"receipt.request_id={evidence.get('request_id')} expected={request_id}")

    # 4. Journal correlation, read from disk rather than through the tool.
    journal = result.get("journal") or {}
    journal_path = Path(journal.get("path") or "")
    records: list[dict] = []
    if journal_path.is_file():
        for line in journal_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    mine = [r for r in records if r.get("request_id") == request_id]
    record("journal records the operation", "PASS" if mine else "FAIL",
           f"{journal_path} persisted={journal.get('persisted')} matching_records={len(mine)}")
    if mine:
        record("journal correlates request_id and task_id",
               "PASS" if mine[-1].get("task_id") == task_id else "FAIL",
               f"request_id={mine[-1].get('request_id')} task_id={mine[-1].get('task_id')} "
               f"classification={mine[-1].get('classification')}")

    # 5. Restart: a brand-new process must read the same record back.
    verify = (
        "import json,sys;"
        f"sys.path.insert(0,{str(BIRDEYE_DIR)!r});"
        "from workspace_bridge import command_history;"
        f"from pathlib import Path;"
        f"print(json.dumps(command_history(Path({str(config_path)!r}), limit=200), ensure_ascii=False))"
    )
    env = os.environ.copy()
    for key in ("BIRDEYE_STATE_ROOT",):
        if journal_path.is_file() and journal.get("persisted"):
            # keep the child on the same evidence root that was just used
            env.setdefault(key, str(journal_path.parent))
    try:
        again = subprocess.run([sys.executable, "-c", verify], cwd=str(BIRDEYE_DIR),
                               capture_output=True, text=True, timeout=120, env=env)
        seen = json.loads(again.stdout.strip().splitlines()[-1]) if again.stdout.strip() else {}
        survived = any(r.get("request_id") == request_id for r in (seen.get("records") or []))
        record("history survives a process restart", "PASS" if survived else "FAIL",
               f"new process saw total={seen.get('count')} with this request_id={survived}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        record("history survives a process restart", "FAIL", f"{type(exc).__name__}: {exc}")

    for claim in (
        "MCP client wiring and tools/list through the real client",
        "watcher indexing latency for the changed marker",
        "reboot/logon persistence of the background gateway",
    ):
        record(claim, "UNVERIFIED", "requires the live client/service on this machine")

    if disposable:
        print(f"\ndisposable acceptance directory left for inspection: {acceptance}")
    return _finish(args.json)


def _finish(as_json: bool) -> int:
    failures = [r for r in RESULTS if r[1] == "FAIL"]
    if as_json:
        print(json.dumps({"results": [{"claim": c, "status": s, "detail": d} for c, s, d in RESULTS],
                          "failures": len(failures)}, indent=2, ensure_ascii=False))
    print(f"\nsummary: {len([r for r in RESULTS if r[1] == 'PASS'])} pass, "
          f"{len(failures)} fail, {len([r for r in RESULTS if r[1] == 'UNVERIFIED'])} unverified "
          f"(unverified is not a pass)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
