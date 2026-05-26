$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"
$nodeModulesDir = Join-Path $frontendDir "node_modules"

Set-Location $frontendDir

if (-not (Test-Path -LiteralPath $nodeModulesDir)) {
    npm install
}

npm run dev -- --host 0.0.0.0
