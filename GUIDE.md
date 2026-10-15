# End-to-end setup

## 1. Discover this machine before choosing installation settings
Record OS, CPU/architecture, available disk, Python executable/version, Git version, agent clients, existing MCP entries, existing gateway processes, existing source checkout and target repository. On Windows use PowerShell:

```powershell
$PSVersionTable
Get-Command python,py,git -ErrorAction SilentlyContinue
py --list-paths
git --version
whoami /user
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'birdeye|mcp_server|http_mcp_server' } | Select-Object ProcessId,ExecutablePath,CommandLine
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```

The SID is identity evidence; a display name is metadata. Do not paste unrelated process command lines or secrets into public reports. On macOS/Linux use `uname -a`, `command -v python3`, `python3 --version`, `git --version`, and the platform's process/socket tools. Core portability must be verified on the selected source; Windows desktop adapters are separate capabilities.

Inspect the target's existing instructions, nested governance documents, manifests and root documentation/HTML navigators. Record HEAD, branch and dirty state using `git -C <target> rev-parse HEAD`, `git -C <target> branch --show-current`, and `git -C <target> status --short`. Do not initialize, pull, reset, clean, rebase or overwrite existing work as a setup side effect.

## 2. Choose layout and source
Example layout, fully replaceable:
- gateway source: `<base>/BirdEye`
- shared knowledge: `<base>/Knowledge`
- shared curated skills: `<base>/Skills/curated`
- historical content: `<base>/Memory`
- target: any existing unrelated repository
- generated candidates: this template's `generated/`

Keep gateway state on a local disk and outside indexed source roots when possible. Never index an entire user profile by default. Exclude secrets, generated dependencies, database files, caches and build output according to source-supported exclusion semantics. Knowledge and history are separate semantic authorities.

Canonical BirdEye source identified on the reference installation:
https://github.com/Letterblack0306/Letterblack_BirdEye

For a fresh destination only:
```powershell
git clone https://github.com/Letterblack0306/Letterblack_BirdEye.git "<base>\BirdEye"
git -C "<base>\BirdEye" rev-parse HEAD
git -C "<base>\BirdEye" status --short
```
Use normal authenticated Git access if private. If unavailable, obtain an authorized source archive; do not invent a package URL. A clone does not include uncommitted changes from another PC. Record the selected revision and inspect its README, repository guide, current status, dependency manifests and source before applying this template. The reference PC had dirty files; its live behavior is not guaranteed by its HEAD alone.

If rebuilding an analogous gateway from another repository, retain the outcomes and contracts in this bundle, but discover that repository's entrypoints/schema. Do not pretend BirdEye filenames are universal.

## 3. Create the isolated runtime
Use a Python version supported by the selected source. The reference checkout did not have a top-level requirements.txt or pyproject.toml, so no fully pinned supported dependency set was established. Inspect the new revision for manifests first.

```powershell
Set-Location "<base>\BirdEye"
& "<discovered-python.exe>" -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip --version
```

If a manifest exists, install through its documented mechanism. If none exists, a **candidate** dependency set inferred from current source imports is:
```powershell
& ".\.venv\Scripts\python.exe" -m pip install watchdog mcp uvicorn starlette httpx websockets PyYAML Pillow
& ".\.venv\Scripts\python.exe" -m pip check
```
These names are not a tested compatibility lock. Resolve actual import/API failures against the selected source, record versions, then save a lock snapshot with `python -m pip freeze` after acceptance. Do not install unrelated agent frameworks, models, embedding services, Node or browser relays just to boot the core. Some adapters may need their own documented dependencies.

On POSIX the interpreter is `.venv/bin/python`. Always configure clients with the absolute interpreter path, not an ambiguous global `python`.

## 4. Generate fresh configuration
Copy machine.example.json to machine.local.json. Set existing gateway/target paths and intended knowledge/skills/memory directories. Create those three content directories locally; seed knowledge and one curated skill from templates. Set `python` to the gateway venv's absolute executable. Select `transport`: `stdio` or `http`.

```text
python scripts/render_config.py machine.local.json --out generated
```
The generator only writes a new output directory. It emits schema candidates based on inspected reference files:
- config.json: schema_version 2 and explicit roots.
- eye_workspace.json: workspace + knowledge roots.
- eye_memory.json: historical root, no imported sources by default.
- eye_skills.json: curated root.
- mcp-client.stdio.example.json and start scripts.

Compare candidates with the selected revision's loaders (`agent.py`, `eye.py`, `mcp_server.py`) and any schema/tests. Back up existing configs; apply candidates deliberately. Do not overwrite an existing installation's configuration as a bulk copy. The generator does not claim all revisions accept its schema. Keep the four root declarations consistent; the inspected system merges EYES configuration with legacy configuration.

Review ALL other source configs for old machine paths, including governance.json and birdeye_projection_config.json, plus Memory/GPT-K adapters and launchers. Do not carry old project projections into the new environment. Configure only the services that actually exist. Search source for absolute path fallbacks and verify which loader is active. Empty content directories do not prove semantic memory retrieval works.

Use the source-default gateway state location initially. BIRDEYE_STATE_ROOT is documented for watcher/MCP behavior, but do not assume it relocates every database or adapter; inspect actual paths returned by runtime status. All clients must resolve the same durable state/authority ownership.

## 5. Bootstrap shared content
Copy templates/knowledge files into Knowledge and adapt them to the actual target. Copy the example skill into Skills/curated/example/SKILL.md. Keep current-position claims dated and evidence-linked. Copy no old project's completion claims.

Memory can begin empty. Add only authorized existing exports/session directories through the source-supported `sources` array. Record source ID, source path, source_class, agent, timestamp/provenance and historical authority. Rebuild derived indexes through the installed importer/indexer. Merely indexing JSON text does not prove canonical conversations or semantic recall work. Treat each Memory capability as optional until exercised.

## 6. Index and inspect before clients
From the gateway directory with the venv interpreter:
```text
python eye.py --json
python agent.py --help
python agent.py trace
python agent.py status
python agent.py roots
```
These commands were observed in reference source. Verify the selected revision still provides them. First indexing writes local machine state. Wait for a completed run; inspect per-root status, skipped/unreadable/oversized files and hashes. Run one initial index owner; do not run parallel rebuilds. EYES may have separate canonical/query generations: inspect both and use only installed replay/rebuild operations if lag exists. Never delete canonical state to fix a query failure.

## 7. Attach clients
### stdio
The generated JSON uses the common `mcpServers` wrapper. Some clients use TOML or different keys: translate command/args/env through that client's current supported UI/schema; do not overwrite its whole configuration. Generated launcher sets working directory, shared state and skills root. It emits only MCP traffic on stdout; diagnostics must go to stderr. The absolute venv interpreter launches `mcp_server.py --stdio`.

A stdio client owns a session process. Several such processes may be legitimate transport sessions, but must share machine state and the supported singleton watcher/authority owner. Do not invent independent per-client databases or policy services.

### shared HTTP service
For clients supporting Streamable HTTP, one gateway service can accept multiple clients. Run the generated HTTP launcher and configure the client with `http://127.0.0.1:8766/mcp` unless the selected runtime config changes that endpoint. Inspect port ownership first. Reference source supports BIRDEYE_HTTP_HOST/PORT and refuses non-loopback binds.

Run the source's `tools/smoke_birdeye_http.py` if present. It checks MCP initialize/discovery/status; its PASS does not prove execution, other tools or remote connector use.

Use the client's actual tools/list result. Require root/status/search/inspect; exercise knowledge, skills, memory and execution only if exposed and supported. A terminal diagnostic command is not evidence that a client can call MCP.

## 8. Prove execution authority
Read templates/execution-contract.md and inspect installed workspace_bridge/authority code. The reference private runtime reported `birdeye-mcp-user` ALLOW with request authority `private-personal-mcp`; this is evidence about that installation, not proof of LBE enforcement. Older documents described a stricter workspace policy. Discover the selected runtime's real enforcing owner.

Where LBE is required, prove the request reaches LBE, uses trusted OS identity, binds authentication to server-owned sessions and checks the authorized action before execution. If LBE is absent, report that gap; a JSON policy, AGENTS.md or transport token cannot fill it. Do not create a second semantic planner or silently weaken a DENY to complete setup.

Use ACCEPTANCE.md through the real client. Indexing/status alone is not final acceptance.

## 9. Persistent lifecycle
stdio normally starts/stops with its owning client; this is intentional, not a broken daemon. For HTTP choose one existing service manager or user-logon task on Windows, or a supported systemd/launchd owner on the actual OS. Use the generated launcher as the action, stable working directory, least required account access, one-instance behavior, logs, and deliberate shutdown. Do not add both a service and duplicate startup task.

On Windows configure the discovered account, not the old PC's username/SID. User-logon startup and boot-before-login startup are different requirements; configure and test the one wanted. After registration: stop/start owner, verify exact listener/PID/executable/args, reconnect client, repeat a real read and legitimate ALLOW effect. Reboot and repeat. Task registration alone is UNVERIFIED persistence.

## 10. Optional remote access
First pass local acceptance. Keep the HTTP service loopback-bound. Reuse an existing authenticated private tunnel/proxy when available. Record transport owner, account authorization, endpoint, credential storage and client compatibility. Do not copy old tunnel profiles, IPs, tokens or task names. Environment variables may carry configured secrets; they must not be treated as cross-process session identity.

A local stdio configuration cannot directly connect a cloud ChatGPT client to a PC. Cloud use requires its supported remote connector plus a reachable authenticated endpoint. Prove a real cloud-client request, not merely tunnel health. Do not assume the old bridge/tunnel is distributed in this ZIP.

## 11. Maintenance, backup and recovery
Keep content sources separate from disposable projections. Back up reviewed configuration, knowledge, skills and canonical historical data. Back up SQLite through an application-supported backup API or stopped-owner consistent snapshot, including appropriate WAL handling. Copying one live .db file is not a consistency guarantee. Encrypt/protect backups according to their content; leave secrets and canonical sessions out of Git.

Before an update record runtime executable, source revision, dirty state, dependency snapshot, policy and client configuration. Use authorized update procedures; preserve local changes. Stage a new runtime, compare schema, run focused checks and live acceptance, then switch one lifecycle owner. Roll back to the recorded prior source/runtime/config together; database schema rollback requires a compatible backup/migration plan. No automatic pull/rebase/cleanup is part of this template.

Final report: installed source + dirty state; runtime interpreter/entrypoint; shared state owner; client request IDs; authority/effect/receipt; root freshness; restart result; optional capability gaps; evidence classification.
