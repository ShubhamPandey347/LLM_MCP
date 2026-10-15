$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'C:/Local MCP/BirdEye'
$env:BIRDEYE_STATE_ROOT = 'C:/Local MCP/BirdEye/state'
$env:SKILLS_ROOT = 'C:/Local MCP/Skills/curated'
$env:MEMORY_ROOT = 'C:/Local MCP/Memory'
$env:PYTHONUNBUFFERED = '1'
& 'C:/Local MCP/BirdEye/.venv/Scripts/python.exe' 'C:/Local MCP/BirdEye/mcp_server.py' --stdio
exit $LASTEXITCODE
