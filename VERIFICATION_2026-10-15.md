# BirdEye — execution authority and evidence verification

**Date:** 2026-10-15 · **Branch:** `arena/c8a92263-llm-mcp` · **Status:** committed to this branch; nothing installed or applied

Scope note: this work ran on a Linux sandbox holding this repository. The installed
gateway is on the owner's Windows machine at `C:\Local MCP\BirdEye`. Everything marked
**PROVEN** below was executed here against the real source; everything requiring the
Windows install is marked **UNVERIFIED** and left for the owner to run.

---

## 1. Owner decisions recorded (binding for this work)

| # | Decision | Consequence |
|---|---|---|
| 1 | Personal gateway; trust own agents for owner-initiated tasks; prioritize capability + auditability | No deny-by-default gate was added |
| 2 | Task-level authorization; no repeated per-command prompts | No per-call approval layer |
| 3 | Any accessible directory, no workspace restriction | `resolve_workspace()` absolute-path acceptance left intact; `_path_escapes_workspace()` deliberately **not** wired into execution |
| 4 | Shared background + client-launched sessions, no duplicate instances | Lease semantics verified and documented rather than changed |

Consequently `_command_allowed()`, `_authority_gate()` and the dead `_is_dangerous_command()`
seam were **left exactly as found**. The work below is audit-integrity only: it does not
restrict what may be executed.

---

## 2. Verified against the real source

**Source identity.** `BirdEye/workspace_bridge.py` and `BirdEye/tests/test_workspace_bridge.py`
are byte-identical to public `main` of `Letterblack0306/Letterblack_BirdEye`
(sha256 `30c67239…` / `0c9714ce…`). `BirdEye/mcp_server.py` differs from public `main` by
exactly two path-portability lines (hardcoded `C:\MCP Local\…` → env/relative); no
security-relevant divergence.

**Tool surface.** `tools/list` over the real stdio protocol returns **24 tools**, matching
the README claim, serverInfo `{"name": "birdeye", "version": "0.1.0"}`.

**Execution path (PROVEN).** Driving the real server over stdio (`--stdio`, JSON-RPC):
`initialize` → `tools/list` → `tools/call workspace_run`. A bounded argv command wrote a
UUID marker into a disposable directory; the marker bytes were read back **independently of
BirdEye** and matched exactly. The watcher logged `[watcher] upserted acceptance/marker.txt`.

**Receipt integrity (PROVEN).** The returned evidence carried `command_hash`, before/after
diff state, `stdout_sha256`, `workspace_changed_by_command`; the on-disk
`executions/<execution_id>/receipt.json` hash matched the returned
`execution_evidence_sha256`.

**Restart persistence (PROVEN).** A newly spawned process read the same journal record back
by `request_id`; the marker survived unchanged.

**Shared ownership / "duplicate instances" (PROVEN, and narrower than it sounds).** Two
concurrent `--stdio` servers on one state root both served all 24 tools. Exactly one acquired
the lease (`birdeye-mcp.lock` = `pid=<first>`); the second logged
`another BirdEye MCP process owns the diagnostic marker; continuing without it` and
`incremental watcher already owned by another BirdEye MCP process`. So the exclusivity is over
the **watcher and lease marker**, not the server process — stdio mode is one process per
client by design, sharing durable state. This is the expected explanation for the two
`agy.exe`-spawned sessions observed earlier; it is not N duplicate gateway owners.

---

## 3. Defects found and fixed (audit integrity only)

1. **`request_id` was accepted and then silently dropped.** `RunRequest.request_id` was parsed
   and validated, but `run_command()` never passed it to `_execute_argv()`, so it appeared in
   neither the receipt nor the journal. Acceptance requires *"Same request/operation identity
   … receipt, execution-history entry"* — the chain could not be closed by request id.
2. **The journal path depended on the process working directory.** `_journal_path()` resolved a
   relative `state` against the client's cwd, while receipts went to `<BirdEye>/state`. With the
   shipped `.mcp.json` (absolute script path, cwd not controlled) a run reported **empty history
   for an execution that plainly happened**. Measured before/after on the same launch:
   `BIRDEYE_STATE_ROOT` journal lines `3 → 3` with the record landing in `<client-cwd>/state/…`
   (before), versus `5 → 6` with no stray cwd journal (after).
3. **A receipt-write failure raised *after* the command had already run**, discarding the
   result — the worst case for *"reconcile unknown side effects before any retry"*. Journal and
   receipt persistence failures are now reported in the result (`journal.persisted`,
   `EVIDENCE_PERSISTENCE_FAILED`) while the execution outcome is preserved.
4. **The test suite wrote into the machine's real evidence tree.** Running `pytest` appended
   synthetic "success" records (including for `git reset --hard`, `cmd /c del`) to
   `<BirdEye>/state/workspace_journal.jsonl`, where they would later read as real activity.

Also corrected, not changed: the failure **circuit breaker is inert**. `_record_circuit_result()`
has zero call sites, `_authority_gate()` never supplies `circuit_key`, and nothing reads
`tripped`. The earlier claim that execution is limited by "timeout **and** circuit-breaking on
repeated failures per intent" is therefore **DISPROVEN**: only the timeout applies. Wiring it
would introduce a *new* restriction, so it was left alone pending the owner's decision.

---

## 4. Changes made

| File | sha256 | Change |
|---|---|---|
| `BirdEye/workspace_bridge.py` | `119ec32c…` | `_evidence_state_root()` (config `state_dir` → `BIRDEYE_STATE_ROOT` → source `state`); `request_id` propagated to result/journal/receipt; journal, circuit and receipt persistence failures reported instead of swallowed or raised |
| `BirdEye/execution_evidence.py` | `35ae64d4…` | Receipt accepts optional `request_id`; **omitted from the canonical receipt when not supplied so existing published hashes stay valid** |
| `BirdEye/tests/test_audit_integrity.py` | `b3ce69ae…` | New: 8 regressions for request identity, evidence-root determinism, visible persistence failure, posture documentation |
| `BirdEye/tests/conftest.py` | `da1d700f…` | Autouse fixture isolates `BIRDEYE_STATE_ROOT` per test so the suite cannot pollute real evidence |
| `BirdEye/tests/test_workspace_run.py` | `b66dec07…` | Repaired 5 pre-existing failures: 4 fakes that assumed the command was the *last* `subprocess.run` call (receipt capture adds its own git probes) and 1 assertion pinned to a retired allowlist message |
| `BirdEye/tools/verify_evidence.py` | `e85ad7ee…` | New runnable verifier (see §6) |
| `GUIDE.md` | `2f880618…` | Documents the single evidence root, its resolution order, and that indexes/databases stay source-default |

Not changed on purpose: `_command_allowed()`, `_authority_gate()`, `resolve_workspace()`,
`_is_dangerous_command()` / `_path_escapes_workspace()` (still unwired), and every
index/database location.

---

## 5. Test status (same environment, before vs after)

| | Failed | Passed | Errors |
|---|---|---|---|
| Pristine `HEAD` | 10 | 143 | 5 |
| After these changes | **6** | **160** | **0** |

The 6 remaining failures are all pre-existing and unrelated to this work; 5 of them need
machine-local state the portable bundle deliberately excludes. Exact causes:

- `test_root_registry.py::test_production_config_*` (2) — require `BirdEye/config.json`, which is
  git-ignored and machine-local (`FileNotFoundError: …/BirdEye/config.json`). Expected to behave
  differently on the installed machine.
- `test_skills_tool.py::test_memory_mcp_has_no_skill_tools` — `ModuleNotFoundError: No module
  named 'memory'` (needs the Memory service source at `MEMORY_ROOT/src`).
- `test_trace_lifecycle.py::test_multi_root_trace_persists_terminal_state_when_memory_is_last` —
  same missing machine-local `config.json`.
- `test_local_mini_package.py::test_run_process_returns_evidence` — the optional mini bridge
  package's own local dependency path.
- `test_mcp_lazy_reconciliation.py::test_birdeye_search_uses_migrated_query_database_without_legacy_reconcile`
  — a genuine stale expectation in the repo: it asserts event order
  `[("eyes", …), ("search", …)]` but the code actually emits `("reconcile", …)` first. Not fixed
  here because it may indicate real behavior drift and is outside this scope.

Environment note: `watchdog` and `mcp` were missing from the interpreter used here and are
required (the README's install list documents them). With both installed the suite runs as above.

---

## 6. Verifier you can run on the Windows machine

`BirdEye/tools/verify_evidence.py` is portable Python and was validated here in both
directions (missing config → exit 1; healthy runtime → exit 0). It executes one bounded
command writing a unique marker into a disposable directory, then proves the chain
independently and prints PASS/FAIL/UNVERIFIED per claim:

```powershell
cd "C:\Local MCP\BirdEye"
.\.venv\Scripts\python.exe tools\verify_evidence.py
```

Measured here: **8 pass, 0 fail, 3 unverified**. The three deliberately unverified claims are
the ones needing the live client/service: MCP client wiring and `tools/list` through the real
client, watcher indexing latency, and reboot/logon persistence. "Unverified is not a pass."

---

## 7. Setup sequence for the Windows machine (in order)

```powershell
# 1. Dependencies (README list; watchdog and mcp are required for the stdio core)
cd "C:\Local MCP\BirdEye"
.\.venv\Scripts\python.exe -m pip install watchdog mcp uvicorn starlette httpx websockets PyYAML Pillow

# 2. Generate and apply configuration candidates (never bulk-overwrite an existing install)
cd "C:\Local MCP"          # repository root containing machine.local.json
.\BirdEye\.venv\Scripts\python.exe scripts\render_config.py machine.local.json --out generated-20261015
#    review generated-20261015\*, then apply config.json + eye_*.json into C:\Local MCP\BirdEye

# 3. Index, then verify the evidence chain
cd "C:\Local MCP\BirdEye"
.\.venv\Scripts\python.exe agent.py trace
.\.venv\Scripts\python.exe tools\verify_evidence.py
```

Then confirm through the actual client (Antigravity/Cline/Cursor/Continue) that `tools/list`
returns 24 tools and that one authorized action produces a receipt plus history entry. The
lease behaviour above predicts exactly one watcher owner regardless of how many clients connect.

---

## 8. Limitations of this record

- No Windows access: the installed `C:\Local MCP\BirdEye` source was **not** inspected, so this
  remains PROVEN for the repository revision only, not for the installed runtime.
- No install, service, scheduled task or client configuration was created or modified.
- Restart persistence was proven for durable state across process restarts here; **reboot/logon**
  persistence and background-service ownership were not exercised.
- Process IDs, ports and client sessions observed earlier remain owner-side observations; none
  could be reproduced or verified from this sandbox.
