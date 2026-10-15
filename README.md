# LLM_MCP — BirdEye Standalone Local MCP Environment

A standalone Model Context Protocol (MCP) environment and gateway configured for local LLM agents (Antigravity, Cursor, Claude Code, Cline, Windsurf, Continue, etc.).

## Overview

This repository contains the standalone BirdEye MCP server and template configuration:
- **`BirdEye/`**: Complete Python-based Model Context Protocol gateway server exposing 24 tools for workspace navigation, deterministic code inspection, live SHA-256 hash verification, knowledge routing, curated skills, and safe command execution.
- **`Knowledge/`**: Curated project reference and knowledge corpus.
- **`Skills/`**: Progressive-disclosure agent runbooks and skill workflows.
- **`Memory/`**: Historical conversation and session memory corpus.
- **`workspace/`**: Governed local target workspace.
- **`generated/`**: Pre-rendered launchers (`start-stdio.ps1`, `start-http.ps1`) and configuration schemas.
- **`scripts/`**: Configuration rendering utilities (`render_config.py`).
- **`templates/`**: Boilerplates for knowledge, skills, governance contracts, and acceptance verification.

---

## Exposed MCP Tools

The BirdEye gateway exposes 24 native MCP tools:
- **Knowledge & Navigation**: `knowledge_route`, `knowledge_read`, `local_projects`, `workspace_identity`, `revision_status`
- **File System & Retrieval**: `birdeye_search`, `birdeye_inspect`, `birdeye_verify_hash`, `birdeye_roots`, `birdeye_status`
- **Indexing & Queries**: `eyes_rebuild`, `eyes_retirement`
- **Skills**: `skills`
- **Memory**: `memory_recall`, `memory_search`, `memory_timeline`, `memory_conversation`, `memory_message`, `memory_related`, `memory_sources`
- **Governed Execution**: `workspace_run`, `workspace_run_sequence`, `workspace_command_history`, `desktop_action`

---

## Quick Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git

### 2. Environment Setup
```powershell
# Create virtual environment in BirdEye
cd BirdEye
python -m venv .venv

# Install dependencies
.\.venv\Scripts\python.exe -m pip install watchdog mcp uvicorn starlette httpx websockets PyYAML Pillow
```

### 3. Generate Configuration
```powershell
# In repository root
.\BirdEye\.venv\Scripts\python.exe scripts/render_config.py machine.local.json --out generated
```

### 4. Index Roots
```powershell
cd BirdEye
.\.venv\Scripts\python.exe agent.py trace
.\.venv\Scripts\python.exe agent.py status
```

---

## Agent Configuration

To configure the BirdEye MCP server in your agents, add the following entry to the agent's MCP config file:

```json
{
  "mcpServers": {
    "birdeye": {
      "command": "C:/Local MCP/BirdEye/.venv/Scripts/python.exe",
      "args": [
        "C:/Local MCP/BirdEye/mcp_server.py",
        "--stdio"
      ],
      "env": {
        "BIRDEYE_STATE_ROOT": "C:/Local MCP/BirdEye/state",
        "SKILLS_ROOT": "C:/Local MCP/Skills/curated",
        "MEMORY_ROOT": "C:/Local MCP/Memory",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Config File Locations on this Machine:
- **Antigravity**: `~/.gemini/config/mcp_config.json` and `.agents/mcp_config.json`
- **Cursor**: `~/.cursor/mcp.json`
- **Claude Code**: `~/.claude.json`
- **Cline (VS Code)**: `%APPDATA%/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windsurf**: `~/.codeium/windsurf/mcp_config.json`
- **Continue**: `~/.continue/config.json`
