# Troubleshooting and bounded recovery

| Symptom | Inspect | Next action |
|---|---|---|
| MCP entry configured, no tools | Exact interpreter, wrapper path, working directory, client logs, stdout contamination | Invoke supported initialize/tools/list; fix actual startup owner |
| Old drive letters appear | All four root configs, active loader, fallback paths, project projections, client inheritance | Correct only active machine mapping; restart owner and inspect roots |
| Database locked | Database paths, writer/indexer/watcher owners, active transactions and leases | Preserve evidence; stop only identified redundant authorized writer, let legitimate transaction finish, use supported recovery; never delete canonical DB as first response |
| Empty search | Root selection, extension/path filters, completed index run, errors and coverage | Inspect known file directly and freshness; zero results do not establish absence |
| EYES generation lag | Canonical/applied generations and replay logs | Use installed supported projection replay/rebuild; canonical data remains intact |
| Missing imports | Selected revision's manifests/imports and isolated interpreter | Install matching documented dependencies; record actual versions |
| Skills missing | Actual SKILLS_ROOT and eye_skills root, discovery status | Fetch one known seeded SKILL.md through client |
| History indexed but memory APIs fail | Canonical importer/store, adapter path and provenance schema | Separate text indexing from conversation/semantic capability; report optional gap |
| Policy file present, actions unrestricted | Live request authority and controller call path | Classify unenforced policy; integrate actual owner before claiming LBE protection |
| DENY | Enforcing owner, principal/session, action and scope | Complete authorized prerequisites or use actual approval/change route; do not bypass |
| Timeout after write | Operation ID, history and effect | Reconcile before retry to prevent duplicate effects |
| Works locally but not in cloud | Connector protocol/auth/session and remote reachability | Prove a cloud-originated call; local health is insufficient |
| Doesn't resume after reboot | Boot vs logon trigger, account rights, working directory, secrets availability and duplicate owners | Correct selected lifecycle owner; reboot and verify actual client action |

Do not make unrelated MCP/browser adapters forbidden because of a past fault. Reuse legitimate specialized capabilities while keeping the required execution authority intact.
