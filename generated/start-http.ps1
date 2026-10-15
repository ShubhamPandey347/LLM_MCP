$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'C:/Local MCP/BirdEye'
$env:BIRDEYE_STATE_ROOT = 'C:/Local MCP/BirdEye/state'
$env:SKILLS_ROOT = 'C:/Local MCP/Skills/curated'
& 'C:/Local MCP/BirdEye/.venv/Scripts/python.exe' 'C:/Local MCP/BirdEye/http_mcp_server.py'
exit $LASTEXITCODE
