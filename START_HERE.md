# BirdEye environment — standalone replication template
Version 1.0 • 15 October 2026

Create a similar environment on a different computer for any repository. Read this file, follow GUIDE.md in order, then give AGENT_HANDOFF.md to the agent on that computer.

This ZIP is a complete guide/template, not a bundled BirdEye binary or offline installer. Installation requires access to the BirdEye source and its dependencies. No access to the old PC is needed after obtaining a suitable source revision. No old database, account, drive letter, private history or project is required. The target repository stays separate from the gateway installation.

## Included
- GUIDE.md: installation through client acceptance, restart, maintenance and recovery.
- scripts/render_config.py: creates fresh per-machine configuration candidates and launchers; does not overwrite source or client settings.
- machine.example.json: the only input file to adapt first.
- AGENT_HANDOFF.md: ready-to-use instruction for the new PC's agent.
- templates/: project knowledge, status, policy contract, agent instructions, acceptance evidence and skill examples.
- ACCEPTANCE.md: request → authority → execution → effect → receipt proof.
- TROUBLESHOOTING.md and SOURCE_EVIDENCE.md.

## Target result
One machine-level BirdEye gateway serves clients; one shared root registry, knowledge corpus, historical memory corpus and skills corpus. LBE owns execution authority where integrated; MCP exposes capabilities. Agents retain reasoning responsibility. Use the installed authority path rather than assuming that a policy document enforces anything.

Start with one repository and lexical retrieval. Add historical import, semantic retrieval, desktop/browser adapters and remote connectivity only after the local foundation works. These are optional layers, not prerequisite services.

## First actions
1. Read GUIDE.md sections 1–4; obtain the actual source.
2. Copy machine.example.json to machine.local.json and enter paths from this PC.
3. Run `python scripts/render_config.py machine.local.json --out generated`.
4. Review generated files; follow GUIDE.md to install candidates and dependencies.
5. Connect the real client and complete ACCEPTANCE.md.

New-PC runtime status: UNVERIFIED. This archive was checked for JSON validity, generator execution and ZIP integrity in Linux; it has not installed or verified a Windows gateway.
