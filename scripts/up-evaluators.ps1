param(
    [int]$DocsPort = 8081,
    [switch]$Detached
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    $env:DOCS_PORT = "$DocsPort"
    $composeArgs = @("-f", "docker-compose.yml", "-f", "docker-compose.evaluators.yml", "up", "--build")
    if ($Detached) {
        $composeArgs += "-d"
    }
    docker compose @composeArgs
}
finally {
    Pop-Location
}
