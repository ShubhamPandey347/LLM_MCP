#!/bin/sh
set -eu
cd 'C:/Local MCP/BirdEye'
export BIRDEYE_STATE_ROOT='C:/Local MCP/BirdEye/state'
export SKILLS_ROOT='C:/Local MCP/Skills/curated'
exec 'C:/Local MCP/BirdEye/.venv/Scripts/python.exe' 'C:/Local MCP/BirdEye/http_mcp_server.py'
