# Live acceptance record
Run through the intended MCP client. Use a disposable directory explicitly included in this setup's authorized workspace. Keep target application files untouched. Do not fabricate receipts.

| Claim | Action | Required observation |
|---|---|---|
| Correct runtime | Initialize MCP and tools/list | Real client session, executable/entrypoint, protocol response and actual tool schemas |
| Correct target | Call roots and workspace identity | New PC path, target ID, current HEAD/branch/dirty state; no old PC roots |
| Current retrieval | Create a unique marker file in the disposable directory through authorized execution, allow indexing, search and inspect | Exact marker from correct virtual path, root completion time and live hash matching independent file bytes |
| Change freshness | Change marker once, await supported watcher/reconciliation, search/inspect/hash again | Updated bytes/hash, bounded measured refresh delay, no stale claim |
| Knowledge | Read a seeded project reference through advertised tool | Exact adapted document, source path and authority |
| Skills | Query and fetch the seeded SKILL.md | Correct content and provenance/hash where supported |
| History, if enabled | Import a small authorized known conversation and retrieve a known message | Actual canonical message, provenance and historical label; semantic recall tested separately |
| Execution ALLOW | Execute a bounded argv-array action writing a unique value only in the authorized acceptance directory | Same request/operation identity, actual authority decision, independent read of file, receipt, execution-history entry |
| Execution DENY, if policy exists | Use a documented harmless denied action, e.g. an unauthorized write to another acceptance-only directory | Policy owner and reason, no target effect, correlated denied receipt; do not use real protected files |
| Shared ownership | Connect two intended clients and retrieve the same changed marker | Same physical content/state and policy owner; no independent per-client index copies |
| Restart | Restart the chosen owner and reconnect | Correct process/listener identity, same content/authority/history, new real-client read and ALLOW effect |
| Reboot, if required | Reboot under chosen logon/boot model | Owner resumes when required and new end-to-end request succeeds |
| Remote, if enabled | Invoke from actual remote/cloud client | Correlated remote request → authenticated session → authority → execution → effect → receipt shown to client |

Use a UUID value per operation. Record client, request_id, operation_id, timestamp, target path, expected/observed value and receipt location/hash. Discover argument names from tools/list. Do not assume this reference runtime's private request authority is the target policy.

If a transport times out after a possible effect, inspect effect/history by operation identity before deciding whether to submit again. Verify request delivery, completion acknowledgement, cancellation behavior and duplicate suppression where supported. A successful isolated request does not establish zero-loss transport under all conditions; record the exercised bounds.

Classifications: RUNTIME_PROVEN, IMPLEMENTED, UNVERIFIED, DISPROVEN, BLOCKED, SOURCE_RUNTIME_DIVERGENCE. Overall core acceptance needs real-client retrieval + legitimate authorized effect + correlated receipt, with the required lifecycle. Missing LBE cannot be marked LBE_PROVEN. A denial alone is insufficient.

After review, remove only the explicitly disposable acceptance artifacts through authorized execution; retain the evidence record. Do not clean other work.
