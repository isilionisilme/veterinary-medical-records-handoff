param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$defaultStorageDir = Join-Path $backendDir "storage"
$backendDotEnvPath = Join-Path $backendDir ".env"
$processStateFile = Join-Path $repoRoot ".start-all-processes.json"
$composeFiles = @("docker-compose.yml", "docker-compose.dev.yml")

if (-not (Test-Path $backendDir)) {
    throw "No se encontro la carpeta backend en: $backendDir"
}

function Get-DotEnvValue {
    param(
        [Parameter(Mandatory = $true)][string]$DotEnvPath,
        [Parameter(Mandatory = $true)][string]$Key
    )

    if (-not (Test-Path $DotEnvPath)) {
        return $null
    }

    $pattern = "^\s*$([regex]::Escape($Key))\s*=\s*(.+?)\s*$"
    foreach ($line in Get-Content -Path $DotEnvPath) {
        if ($line -match "^\s*#") {
            continue
        }
        if ($line -match $pattern) {
            $value = $Matches[1].Trim()
            if (
                ($value.StartsWith("'") -and $value.EndsWith("'")) -or
                ($value.StartsWith('"') -and $value.EndsWith('"'))
            ) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            if ([string]::IsNullOrWhiteSpace($value)) {
                return $null
            }
            return $value
        }
    }

    return $null
}

function Resolve-AbsolutePath {
    param(
        [Parameter(Mandatory = $true)][string]$PathValue,
        [Parameter(Mandatory = $true)][string]$BaseDir
    )

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return Join-Path $BaseDir $PathValue
}

$dbPaths = New-Object System.Collections.Generic.List[string]
$defaultDbPath = Join-Path $backendDir "data\documents.db"
$dbPaths.Add($defaultDbPath)

if (-not [string]::IsNullOrWhiteSpace($env:VET_RECORDS_DB_PATH)) {
    $dbPaths.Add((Resolve-AbsolutePath -PathValue $env:VET_RECORDS_DB_PATH -BaseDir $backendDir))
}

$dotenvDbPath = Get-DotEnvValue -DotEnvPath $backendDotEnvPath -Key "VET_RECORDS_DB_PATH"
if (-not [string]::IsNullOrWhiteSpace($dotenvDbPath)) {
    $dbPaths.Add((Resolve-AbsolutePath -PathValue $dotenvDbPath -BaseDir $backendDir))
}

$storageDirs = New-Object System.Collections.Generic.List[string]
$storageDirs.Add($defaultStorageDir)

if (-not [string]::IsNullOrWhiteSpace($env:VET_RECORDS_STORAGE_PATH)) {
    $storageDirs.Add(
        (Resolve-AbsolutePath -PathValue $env:VET_RECORDS_STORAGE_PATH -BaseDir $backendDir)
    )
}

$dotenvStoragePath = Get-DotEnvValue -DotEnvPath $backendDotEnvPath -Key "VET_RECORDS_STORAGE_PATH"
if (-not [string]::IsNullOrWhiteSpace($dotenvStoragePath)) {
    $storageDirs.Add((Resolve-AbsolutePath -PathValue $dotenvStoragePath -BaseDir $backendDir))
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

function Stop-DevProcessesByCommandLine {
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

function Remove-PathWithRetries {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [switch]$Directory,
        [int]$MaxAttempts = 5
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        if (-not (Test-Path $Path)) {
            return $true
        }
        try {
            if ($Directory) {
                Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            } else {
                attrib -R $Path 2>$null
                Remove-Item -Path $Path -Force -ErrorAction Stop
            }
            return $true
        } catch {
            Start-Sleep -Milliseconds 250
        }
    }

    return -not (Test-Path $Path)
}

function Stop-DockerDevProjectBestEffort {
    $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCmd) {
        Write-Host "Docker CLI no disponible. Continuando con reset local sin docker compose down."
        return
    }

    Push-Location $repoRoot
    try {
        $args = @("compose")
        foreach ($file in $composeFiles) {
            $args += @("-f", $file)
        }
        $args += @("down")

        $tmpDir = Join-Path $repoRoot "tmp"
        New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
        $stdoutFile = Join-Path $tmpDir "reset-local-compose-down.out.log"
        $stderrFile = Join-Path $tmpDir "reset-local-compose-down.err.log"

        $process = Start-Process -FilePath $dockerCmd.Source -ArgumentList $args -PassThru -Wait -NoNewWindow -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile
        if ($process.ExitCode -eq 0) {
            Write-Host "Entorno docker del proyecto detenido (compose down)."
        } else {
            Write-Host "No se pudo ejecutar compose down (continuando en modo local)."
        }

        Remove-Item $stdoutFile, $stderrFile -ErrorAction SilentlyContinue
    } finally {
        Pop-Location
    }
}

Write-Host "Reiniciando estado local de desarrollo..."
Stop-DockerDevProjectBestEffort
Stop-TrackedProcesses
Stop-DevProcessesByCommandLine
Stop-PortProcess -Port 8000
Stop-PortProcess -Port 5173

($dbPaths | Sort-Object -Unique) | ForEach-Object {
    $dbPath = $_
    if (Test-Path $dbPath) {
        if (Remove-PathWithRetries -Path $dbPath) {
            Write-Host "DB eliminada: $dbPath"
        } else {
            throw "No se pudo eliminar la DB (archivo en uso): $dbPath"
        }
    } else {
        Write-Host "DB no encontrada (ok): $dbPath"
    }
}

($storageDirs | Sort-Object -Unique) | ForEach-Object {
    $storageDir = $_
    if (Test-Path $storageDir) {
        if (-not (Remove-PathWithRetries -Path $storageDir -Directory)) {
            throw "No se pudo limpiar storage (ruta en uso): $storageDir"
        }
    }
    New-Item -ItemType Directory -Path $storageDir -Force | Out-Null
    Write-Host "Storage reiniciado: $storageDir"
}

Write-Host "Reset local de datos completado."
