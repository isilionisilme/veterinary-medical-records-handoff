param(
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$backendDataDir = if ([string]::IsNullOrWhiteSpace($env:BACKEND_DATA_DIR)) {
    ".\backend\data"
} else {
    $env:BACKEND_DATA_DIR
}
if (-not [System.IO.Path]::IsPathRooted($backendDataDir)) {
    $backendDataDir = Join-Path $repoRoot $backendDataDir
}
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$dbPath = Join-Path $backendDataDir "documents.db"
$dbDir = Split-Path -Parent $dbPath
$processStateFile = Join-Path $repoRoot ".start-all-processes.json"
$scriptMutexName = "Global\VetRecordsResetDockerDevMutex"
$frontendPort = if ([string]::IsNullOrWhiteSpace($env:FRONTEND_PORT)) {
    "5173"
} else {
    $env:FRONTEND_PORT
}
$frontendUrl = "http://localhost:$frontendPort"

function Get-DockerCommand {
    return (Get-Command docker -ErrorAction SilentlyContinue)
}

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

function Get-DockerDesktopExecutable {
    $candidates = @(
        (Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"),
        (Join-Path $env:ProgramW6432 "Docker\Docker\Docker Desktop.exe"),
        (Join-Path $env:LocalAppData "Programs\Docker\Docker\Docker Desktop.exe")
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Wait-DockerEngineReady {
    param(
        [int]$TimeoutSeconds = 180,
        [int]$PollSeconds = 3
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            & docker info *> $null
            if ($LASTEXITCODE -eq 0) {
                return $true
            }
        } catch {
            # retry
        }

        Start-Sleep -Seconds $PollSeconds
    }

    return $false
}

function Ensure-DockerAvailable {
    $dockerCmd = Get-DockerCommand
    if (-not $dockerCmd) {
        throw "Docker CLI is not available. Install Docker Desktop and ensure 'docker' is in PATH."
    }

    try {
        & docker info *> $null
    } catch {
        # Handle not-ready engine below.
    }

    if ($LASTEXITCODE -eq 0) {
        return
    }

    $desktopExe = Get-DockerDesktopExecutable
    if (-not $desktopExe) {
        throw "Docker engine is not running and Docker Desktop executable was not found. Start Docker Desktop manually and retry."
    }

    Write-Host "Docker engine no disponible. Intentando arrancar Docker Desktop..."
    Start-Process -FilePath $desktopExe | Out-Null
    Write-Host "Esperando a que Docker esté listo..."

    if (-not (Wait-DockerEngineReady)) {
        throw "Docker Desktop did not become ready in time. Open Docker Desktop and retry once engine status is running."
    }
}

function Get-DescendantProcessIds {
    param(
        [Parameter(Mandatory = $true)][int]$RootPid
    )

    $visited = New-Object 'System.Collections.Generic.HashSet[int]'
    $queue = New-Object System.Collections.Queue
    $queue.Enqueue([int]$RootPid)

    while ($queue.Count -gt 0) {
        $currentPid = [int]$queue.Dequeue()
        if (-not $visited.Add($currentPid)) {
            continue
        }

        Get-CimInstance Win32_Process -Filter "ParentProcessId = $currentPid" -ErrorAction SilentlyContinue |
            ForEach-Object { $queue.Enqueue([int]$_.ProcessId) }
    }

    return @($visited)
}

function Stop-ProcessSubtree {
    param(
        [Parameter(Mandatory = $true)][int]$RootPid
    )

    $all = Get-DescendantProcessIds -RootPid $RootPid
    if (-not $all -or $all.Count -eq 0) {
        return
    }

    $ordered = $all | Sort-Object -Descending
    foreach ($pidToStop in $ordered) {
        Stop-Process -Id $pidToStop -Force -ErrorAction SilentlyContinue
    }
}

function Stop-PortProcess {
    param(
        [Parameter(Mandatory = $true)][int]$Port
    )

    $lines = netstat -ano -p TCP | Select-String -Pattern "LISTENING" | Select-String -Pattern "[:\.]$Port\s"
    foreach ($line in $lines) {
        $parts = ($line.Line -replace "\s+", " ").Trim().Split(" ")
        if ($parts.Count -lt 5) {
            continue
        }
        $portPid = 0
        if ([int]::TryParse($parts[-1], [ref]$portPid) -and $portPid -gt 0) {
            Stop-ProcessSubtree -RootPid $portPid
        }
    }
}

function Stop-TrackedProcesses {
    if (-not (Test-Path $processStateFile)) {
        return
    }

    try {
        $state = Get-Content $processStateFile -Raw | ConvertFrom-Json
        foreach ($trackedPid in @($state.pids)) {
            if ($trackedPid -is [int] -and $trackedPid -gt 0) {
                Stop-ProcessSubtree -RootPid $trackedPid
            }
        }
    } catch {
        # Ignore malformed state file and continue with fallback cleanup.
    } finally {
        Remove-Item $processStateFile -Force -ErrorAction SilentlyContinue
    }
}

function Stop-LocalDevProcesses {
    $patterns = @(
        "backend.app.main:create_app",
        "uvicorn",
        "npm run dev"
    )

    $repoMarkers = @(
        $repoRoot,
        $backendDir,
        $frontendDir,
        $venvPython
    ) | ForEach-Object { ([string]$_).ToLowerInvariant().Replace("/", "\") }

    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $cmd = $_.CommandLine
            if (-not $cmd) { return $false }
            $cmdNormalized = ([string]$cmd).ToLowerInvariant().Replace("/", "\")
            $isRepoScoped = $false
            foreach ($marker in $repoMarkers) {
                if (-not [string]::IsNullOrWhiteSpace($marker) -and $cmdNormalized.Contains($marker)) {
                    $isRepoScoped = $true
                    break
                }
            }
            if (-not $isRepoScoped) { return $false }
            foreach ($pattern in $patterns) {
                if ($cmd -like "*$pattern*") { return $true }
            }
            return $false
        } |
        ForEach-Object { Stop-ProcessSubtree -RootPid ([int]$_.ProcessId) }
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

$mutex = New-Object System.Threading.Mutex($false, $scriptMutexName)
$hasLock = $false
try {
    $hasLock = $mutex.WaitOne(0)
    if (-not $hasLock) {
        Write-Host "Ya hay una ejecucion de reset-docker-dev-env en curso. Espera a que termine e intentalo de nuevo."
        exit 1
    }

    Write-Host "Parando procesos locales de dev (si existen)..."
    Stop-TrackedProcesses
    Stop-LocalDevProcesses

    Ensure-DockerAvailable

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
    Write-Host "Entorno docker de desarrollo reiniciado correctamente."
    Write-Host "- Backend:  http://localhost:8000/health"
    Write-Host "- Frontend: $frontendUrl"
}
finally {
    if ($hasLock) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
