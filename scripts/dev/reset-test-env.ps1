param(
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendDataDir = if ([string]::IsNullOrWhiteSpace($env:BACKEND_DATA_DIR)) {
    ".\backend\data"
} else {
    $env:BACKEND_DATA_DIR
}
if (-not [System.IO.Path]::IsPathRooted($backendDataDir)) {
    $backendDataDir = Join-Path $repoRoot $backendDataDir
}
$dbPath = Join-Path $backendDataDir "documents.db"
$dbDir = Split-Path -Parent $dbPath
$frontendPort = if ([string]::IsNullOrWhiteSpace($env:FRONTEND_PORT)) {
    "5173"
} else {
    $env:FRONTEND_PORT
}
$frontendUrl = "http://localhost:$frontendPort"

function Invoke-Compose {
    param(
        [Parameter(Mandatory = $true)][string[]]$ComposeArgs
    )

    Push-Location $repoRoot
    try {
        & docker compose -f "docker-compose.yml" -f "docker-compose.dev.yml" @ComposeArgs
        if ($LASTEXITCODE -ne 0) {
            throw "docker compose falló con exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
}

function Wait-Http200 {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $status = (Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10).StatusCode
            if ($status -eq 200) {
                return
            }
        } catch {
            # retry
        }
        Start-Sleep -Seconds $DelaySeconds
    }

    throw "Timeout esperando HTTP 200 en $Url"
}

Write-Host "Parando entorno docker dev..."
Invoke-Compose -ComposeArgs @("down")

if (-not (Test-Path $dbDir)) {
    New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
}

if (Test-Path $dbPath) {
    cmd /c "del /f /q `"$dbPath`"" | Out-Null
    Write-Host "DB eliminada: $dbPath"
} else {
    Write-Host "DB no encontrada (ok): $dbPath"
}

$upArgs = @("up", "-d")
if (-not $NoBuild) {
    $upArgs += "--build"
}

Write-Host "Levantando entorno docker dev..."
Invoke-Compose -ComposeArgs $upArgs

Write-Host "Verificando servicios..."
Wait-Http200 -Url "http://localhost:8000/health"
Wait-Http200 -Url $frontendUrl

Write-Host ""
Write-Host "Entorno de pruebas reiniciado correctamente."
Write-Host "- Backend:  http://localhost:8000/health"
Write-Host "- Frontend: $frontendUrl"
