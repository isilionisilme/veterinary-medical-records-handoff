param(
    [int]$DocsPort = 8081
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    $env:DOCS_PORT = "$DocsPort"
    docker compose -f docker-compose.yml -f docker-compose.evaluators.yml down
}
finally {
    Pop-Location
}
