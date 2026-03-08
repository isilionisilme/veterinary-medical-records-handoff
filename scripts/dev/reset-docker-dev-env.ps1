param(
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetScript = Join-Path $scriptDir "lib\reset-docker-core.ps1"

if (-not (Test-Path $targetScript)) {
    throw "No se encontro script objetivo: $targetScript"
}

if ($NoBuild) {
    & $targetScript -NoBuild
} else {
    & $targetScript
}
