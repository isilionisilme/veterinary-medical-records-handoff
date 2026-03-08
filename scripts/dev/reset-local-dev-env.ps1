param(
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$resetScript = Join-Path $scriptDir "lib\reset-local-core.ps1"
$startAllScript = Join-Path $scriptDir "start-all.ps1"

if (-not (Test-Path $resetScript)) {
    throw "No se encontro script objetivo: $resetScript"
}

if (-not (Test-Path $startAllScript)) {
    throw "No se encontro script objetivo: $startAllScript"
}

# 1) Reset local data/state.
& $resetScript

if ($NoStart) {
    Write-Host "Reset local completado. Entorno no iniciado (NoStart)."
    exit 0
}

# 2) Start both backend + frontend in their dev consoles.
& $startAllScript
