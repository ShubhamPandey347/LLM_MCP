from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _isolated_evidence_root(tmp_path, monkeypatch):
    """Keep test executions out of the machine's real evidence tree.

    Several tests drive the genuine execution path, which writes journal records,
    failure-circuit state and execution receipts. Without isolation those writes
    land in the gateway's own state directory, so a routine `pytest` run appends
    synthetic "success" entries that later appear in workspace_command_history as
    if they were real machine activity. Evidence must not be pollutable by tests.
    """
    monkeypatch.setenv("BIRDEYE_STATE_ROOT", str(tmp_path / "evidence-root"))
    yield