# Source evidence and limitations
Prepared 2026-10-15 from read-only BirdEye calls and live source reads. No changes were made to the reference gateway source.

Observed reference:
- Canonical repository named by local README: Letterblack0306/Letterblack_BirdEye.
- Local HEAD: 7addcdf726856862ceafcca2500ffc4bd62d6e6f, branch main, dirty owner files including mcp_server.py, agent.py, http_mcp_server.py, workspace_bridge.py, execution_evidence.py and authority/.
- Local source read receipt: bird-20261015-090755-8a6f2d42. A clone at this HEAD is not evidence-equivalent to that dirty runtime.
- README and docs/REPOSITORY_GUIDE.md establish stdio entrypoint, optional HTTP entrypoint, configured roots, evidence hierarchy and source/runtime distinction.
- config.json schema_version 2; eye_workspace.json roots; eye_memory.json and eye_skills.json schema_version 1 with kind/root were read directly. Included configs are newly generated, sanitized candidates.
- agent.py source exposes roots, trace, status, inspect and search commands.
- http_mcp_server.py source uses mcp/uvicorn/Starlette and BIRDEYE_HTTP_HOST/PORT/TOKEN. README names loopback port 8766 and tools/smoke_birdeye_http.py.
- Source imports establish candidate dependency names, not tested compatible pins. No top-level requirements.txt or pyproject.toml was found in the inspected root listing.
- BIRDEYE_WATCH.md describes per-state-root watcher lease and 300-second default interval. The named birdeye-watch.ps1 was not present at the inspected root; therefore this bundle uses the Python trace command and does not ship that missing wrapper.
- BirdEye roots call succeeded, but indexed search failed with OperationalError: database is locked. Do not inherit a claim of healthy reference retrieval.
- GPT-K reference `project-engineering/letterblack-birdeye-local-evidence-and-governed-execution.md` was read. It contains dated topology/validation and later bridge lifecycle notes; these are context, not new-machine proof.
- Live workspace_run authority response was `birdeye-mcp-user`, decision ALLOW, request_authority private-personal-mcp. Strict LBE gating was not proven by that call. This differs from some older workspace-restriction descriptions; the guide explicitly requires discovery of the selected installation's actual enforcement owner.

Not bundled: BirdEye implementation, third-party packages, private memory, session logs, databases, tokens, old tunnel profiles, old workspace mappings, paid services or an LBE installer. Source access and new-machine acceptance remain required.

Validation performed for this archive: generator syntax/execution, JSON parsing of emitted candidates, relative archive layout and ZIP CRC checks. No claim of Windows execution, client compatibility, current dependency compatibility, LBE integration or reboot persistence is made.
