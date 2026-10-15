"""Audit-integrity regressions.

Scope: these tests protect *evidence* behavior only. They deliberately do not
assert any authorization/allowlist policy: the owner selected a private
personal-gateway posture where reaching workspace_run with a resolved workspace
and argv is the execution authority. If that posture ever changes, these tests
should fail loudly rather than silently drift.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from execution_evidence import build_execution_receipt, empty_diff_state
from workspace_bridge import (
    RunSequenceStep,
    RunRequest,
    RunSequenceRequest,
    command_history,
    run_command,
    run_sequence,
)


def _config(tmp_path: Path, workspace: Path | None = None, state_dir: str | None = None) -> Path:
    ws = workspace or tmp_path / "workspace"
    ws.mkdir(exist_ok=True)
    config = tmp_path / "config.json"
    payload: dict = {"roots": [{"id": "demo", "path": str(ws), "class": "workspace"}]}
    if state_dir is not None:
        payload["state_dir"] = state_dir
    config.write_text(json.dumps(payload), encoding="utf-8")
    return config


def _fake_subprocess(monkeypatch, calls: list[list[str]]):
    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(args, **kwargs):
        calls.append(list(args))
        return Completed()

    monkeypatch.setattr("workspace_bridge.subprocess.run", fake_run)


# --- request identity ------------------------------------------------------

def test_request_id_is_preserved_in_result_journal_and_receipt(tmp_path, monkeypatch):
    config = _config(tmp_path)
    calls: list[list[str]] = []
    _fake_subprocess(monkeypatch, calls)

    result = run_command(
        RunRequest("demo", ("python", "-m", "pytest"), request_id="req-1234", task_id="task-9"),
        config,
    )

    assert result["request_id"] == "req-1234"
    assert result["task_id"] == "task-9"
    assert result["execution_evidence"]["request_id"] == "req-1234"

    records = command_history(config, workspace="demo")["records"]
    mine = [r for r in records if r.get("request_id") == "req-1234"]
    assert len(mine) == 1
    assert mine[0]["task_id"] == "task-9"


def test_receipt_hash_covers_request_id_only_when_supplied():
    common = dict(
        root=Path("."),
        argv=("git", "status"),
        exit_code=0,
        timed_out=False,
        stdout="ok",
        stderr="",
        started_at="2026-01-01T00:00:00+00:00",
        completed_at="2026-01-01T00:00:01+00:00",
        elapsed_seconds=1.0,
        before=empty_diff_state(),
        after=empty_diff_state(),
    )
    without = build_execution_receipt(**common)
    with_one = build_execution_receipt(**common, request_id="req-a")
    with_other = build_execution_receipt(**common, request_id="req-b")

    # No request id supplied -> unchanged legacy shape and hash.
    assert "request_id" not in without
    # Supplying one binds the receipt to that operation identity.
    assert with_one["request_id"] == "req-a"
    assert with_one["execution_evidence_sha256"] != without["execution_evidence_sha256"]
    assert with_one["execution_evidence_sha256"] != with_other["execution_evidence_sha256"]


# --- deterministic evidence location --------------------------------------

def test_journal_follows_state_root_not_process_cwd(tmp_path, monkeypatch):
    config = _config(tmp_path)
    state_root = tmp_path / "durable-state"
    elsewhere = tmp_path / "client-cwd"
    elsewhere.mkdir()
    monkeypatch.setenv("BIRDEYE_STATE_ROOT", str(state_root))
    monkeypatch.chdir(elsewhere)

    result = run_command(RunRequest("demo", ("git", "status")), config)

    journal_path = Path(result["journal"]["path"])
    assert result["journal"]["persisted"] is True
    assert journal_path == (state_root / "workspace_journal.jsonl").resolve()
    assert journal_path.exists()
    assert not (elsewhere / "state" / "workspace_journal.jsonl").exists()

    # The same state root must be readable back regardless of cwd.
    records = command_history(config)["records"]
    assert any(r["argv"][:2] == ["git", "status"] for r in records)


def test_explicit_config_state_dir_wins_over_state_root(tmp_path, monkeypatch):
    explicit = tmp_path / "explicit-state"
    config = _config(tmp_path, state_dir=str(explicit))
    monkeypatch.setenv("BIRDEYE_STATE_ROOT", str(tmp_path / "env-state"))

    result = run_command(RunRequest("demo", ("git", "status")), config)

    assert Path(result["journal"]["path"]) == (explicit / "workspace_journal.jsonl").resolve()
    assert result["journal"]["persisted"] is True


def test_relative_config_state_dir_is_config_relative(tmp_path, monkeypatch):
    config = _config(tmp_path, state_dir="var/state")
    elsewhere = tmp_path / "client-cwd"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.delenv("BIRDEYE_STATE_ROOT", raising=False)

    result = run_command(RunRequest("demo", ("git", "status")), config)

    assert Path(result["journal"]["path"]) == (tmp_path / "var" / "state" / "workspace_journal.jsonl").resolve()


# --- persistence failures are visible -------------------------------------

def test_journal_persistence_failure_is_reported_not_swallowed(tmp_path, monkeypatch):
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    config = _config(tmp_path, state_dir=str(blocker / "nested"))
    calls: list[list[str]] = []
    _fake_subprocess(monkeypatch, calls)

    result = run_command(RunRequest("demo", ("git", "status")), config)

    # The execution itself is real and must still be reported. Raising here would
    # hide a possible side effect from the caller after the command had run.
    assert result["ok"] is True
    # ...but it must not be presented as fully audited when it is not.
    assert result["journal"]["persisted"] is False
    assert "EVIDENCE_PERSISTENCE_FAILED" in result["journal"]["error"]
    assert "EVIDENCE_PERSISTENCE_FAILED" in result["execution_history"]["error"]


# --- posture documentation (capability-first, chosen by the owner) ---------

def test_unregistered_absolute_workspace_and_arbitrary_executable_still_run(tmp_path, monkeypatch):
    """Records the selected posture: no allowlist, any existing absolute dir.

    This is intentional current behavior, not an oversight: the owner chose a
    private personal gateway with task-level authorization. The test exists so
    that any future change to this model is an explicit, visible decision.
    """
    config = _config(tmp_path)
    outside = tmp_path / "outside-root"
    outside.mkdir()
    calls: list[list[str]] = []
    _fake_subprocess(monkeypatch, calls)

    result = run_command(RunRequest(str(outside.resolve()), ("StarDesk.exe", "--open")), config)

    assert result["ok"] is True
    assert ["StarDesk.exe", "--open"] in calls
    assert result["authority"]["decision"] == "ALLOW"


def test_sequence_propagates_request_id_to_every_step(tmp_path, monkeypatch):
    config = _config(tmp_path)
    calls: list[list[str]] = []
    _fake_subprocess(monkeypatch, calls)

    response = run_sequence(
        RunSequenceRequest(
            "demo",
            (
                RunSequenceStep(("git", "status")),
                RunSequenceStep(("git", "diff", "--stat")),
            ),
            request_id="seq-77",
        ),
        config,
    )

    assert response["status"] == "completed"
    assert [step["request_id"] for step in response["commands"]] == ["seq-77", "seq-77"]
    records = command_history(config)["records"]
    assert sum(1 for r in records if r.get("request_id") == "seq-77") == 2
