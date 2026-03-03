param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$venvDir = Join-Path $repoRoot ".venv"
$bootstrapLog = Join-Path $repoRoot "tmp\bootstrap.log"
$processStateFile = Join-Path $repoRoot ".start-all-processes.json"

if (-not (Test-Path $backendDir)) {
    throw "No se encontro la carpeta backend en: $backendDir"
}

if (-not (Test-Path $frontendDir)) {
    throw "No se encontro la carpeta frontend en: $frontendDir"
}

$fixedWindowWidth = 50
$fixedWindowHeight = 40
$powershellExe = Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"
$backendWindowTitle = "US21 Backend Dev"
$frontendWindowTitle = "US21 Frontend Dev"
$scriptMutexName = "Global\US21StartAllMutex"
$backendDotEnvFile = Join-Path $backendDir ".env"
$confidencePolicyEnvKeys = @(
    "VET_RECORDS_CONFIDENCE_POLICY_VERSION",
    "VET_RECORDS_CONFIDENCE_LOW_MAX",
    "VET_RECORDS_CONFIDENCE_MID_MAX"
)

$resizeWindowCommand = @'
try {
    mode con: cols=__FIXED_WIDTH__ lines=__FIXED_HEIGHT__ > $null
} catch {}

try {
$rawUi = $Host.UI.RawUI
$currentWindow = $rawUi.WindowSize
$targetWidth = __FIXED_WIDTH__
$targetHeight = __FIXED_HEIGHT__
$buffer = $rawUi.BufferSize
if ($buffer.Width -lt $targetWidth) {
    $rawUi.BufferSize = New-Object System.Management.Automation.Host.Size($targetWidth, $buffer.Height)
}
$rawUi.WindowSize = New-Object System.Management.Automation.Host.Size($targetWidth, $targetHeight)
} catch {}
'@
$resizeWindowCommand = $resizeWindowCommand.Replace("__FIXED_WIDTH__", $fixedWindowWidth)
$resizeWindowCommand = $resizeWindowCommand.Replace("__FIXED_HEIGHT__", $fixedWindowHeight)

function Invoke-ExternalCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$StepName,
        [int]$TimeoutSeconds = 600
    )

    if (-not (Test-Path (Split-Path -Parent $bootstrapLog))) {
        New-Item -Path (Split-Path -Parent $bootstrapLog) -ItemType Directory -Force | Out-Null
    }
    Add-Content -Path $bootstrapLog -Value ("[{0}] {1}" -f (Get-Date -Format "s"), "$FilePath $($ArgumentList -join ' ')")

    $safeName = ($StepName -replace "[^a-zA-Z0-9_-]", "_")
    $stdoutFile = Join-Path $repoRoot ("tmp\bootstrap-{0}.out.log" -f $safeName)
    $stderrFile = Join-Path $repoRoot ("tmp\bootstrap-{0}.err.log" -f $safeName)

    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -PassThru -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile
    $completed = $true
    try {
        Wait-Process -Id $process.Id -Timeout $TimeoutSeconds -ErrorAction Stop
    } catch {
        $completed = $false
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }

    $stdout = if (Test-Path $stdoutFile) { Get-Content -Path $stdoutFile -Raw } else { "" }
    $stderr = if (Test-Path $stderrFile) { Get-Content -Path $stderrFile -Raw } else { "" }
    if ($stdout) { Add-Content -Path $bootstrapLog -Value $stdout }
    if ($stderr) { Add-Content -Path $bootstrapLog -Value $stderr }
    Remove-Item $stdoutFile, $stderrFile -ErrorAction SilentlyContinue

    if (-not $completed) {
        throw "Paso '$StepName' agotó el tiempo ($TimeoutSeconds s). Revisa: $bootstrapLog"
    }

    if ($process.ExitCode -ne 0) {
        throw "Paso '$StepName' falló (exit code $($process.ExitCode)). Revisa: $bootstrapLog"
    }
}

function Ensure-BackendPrerequisites {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $bootstrapLog) | Out-Null
    Set-Content -Path $bootstrapLog -Value ("Bootstrap iniciado {0}" -f (Get-Date -Format "s"))

    if (-not (Test-Path $venvPython)) {
        Write-Host "Preparando entorno Python (.venv)..."
        if (Get-Command py -ErrorAction SilentlyContinue) {
            Invoke-ExternalCommand -FilePath "py" -ArgumentList @("-3.11", "-m", "venv", $venvDir) -WorkingDirectory $repoRoot -StepName "create-venv" -TimeoutSeconds 180
        } else {
            Invoke-ExternalCommand -FilePath "python" -ArgumentList @("-m", "venv", $venvDir) -WorkingDirectory $repoRoot -StepName "create-venv" -TimeoutSeconds 180
        }
    }

    $fitzAvailable = $false
    try {
        & $venvPython -c "import fitz" *> $null
        $fitzAvailable = $true
    } catch {
        $fitzAvailable = $false
    }

    if (-not $fitzAvailable) {
        Write-Host "Instalando dependencias backend (requirements-dev)..."
        Invoke-ExternalCommand -FilePath $venvPython -ArgumentList @("-m", "pip", "install", "-r", "requirements-dev.txt") -WorkingDirectory $repoRoot -StepName "pip-install" -TimeoutSeconds 900
    }

    try {
        & $venvPython -c "import fitz"
    } catch {
        throw "No se pudo habilitar PyMuPDF (fitz) en .venv. Revisa: $bootstrapLog"
    }
}

function Ensure-FrontendPrerequisites {
    $nodeModules = Join-Path $frontendDir "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Write-Host "Instalando dependencias frontend (npm install)..."
        Invoke-ExternalCommand -FilePath "npm" -ArgumentList @("install") -WorkingDirectory $frontendDir -StepName "npm-install" -TimeoutSeconds 900
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

    # Stop children first, then the root process to close windows cleanly.
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
        $pid = 0
        if ([int]::TryParse($parts[-1], [ref]$pid) -and $pid -gt 0) {
            Stop-ProcessSubtree -RootPid $pid
        }
    }
}

function Stop-ExistingDevWindows {
    $targetTitles = @($backendWindowTitle, $frontendWindowTitle)
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $targetTitles -contains $_.MainWindowTitle } |
        ForEach-Object { Stop-ProcessSubtree -RootPid $_.Id }
}

function Stop-DevProcessesByCommandLine {
    $patterns = @(
        "npm run dev",
        "backend.app.main:create_app"
    )

    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $cmd = $_.CommandLine
            if (-not $cmd) { return $false }
            foreach ($pattern in $patterns) {
                if ($cmd -like "*$pattern*") { return $true }
            }
            return $false
        } |
        ForEach-Object { Stop-ProcessSubtree -RootPid ([int]$_.ProcessId) }
}

function Stop-TrackedProcesses {
    if (-not (Test-Path $processStateFile)) {
        return
    }

    try {
        $state = Get-Content $processStateFile -Raw | ConvertFrom-Json
        foreach ($pid in @($state.pids)) {
            if ($pid -is [int] -and $pid -gt 0) {
                Stop-ProcessSubtree -RootPid $pid
            }
        }
    } catch {
        # Ignore malformed state file and continue with port cleanup.
    } finally {
        Remove-Item $processStateFile -Force -ErrorAction SilentlyContinue
    }
}

function Start-DevConsole {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$CommandToRun,
        [Parameter(Mandatory = $true)][string]$WindowTitle
    )

    $composedCommand = "& { `$Host.UI.RawUI.WindowTitle = '$WindowTitle'; $resizeWindowCommand; Set-Location '$WorkingDirectory'; $CommandToRun }"

    return Start-Process $powershellExe -PassThru -ArgumentList @(
        "-NoExit",
        "-Command",
        $composedCommand
    )
}

function Read-DotEnvValues {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Keys
    )

    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }

    foreach ($line in Get-Content -Path $Path) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("#")) {
            continue
        }
        $parts = $trimmed.Split("=", 2)
        if ($parts.Count -ne 2) {
            continue
        }
        $key = $parts[0].Trim()
        if ($Keys -notcontains $key) {
            continue
        }
        $value = $parts[1].Trim()
        if (
            $value.Length -ge 2 -and
            (
                ($value.StartsWith("'") -and $value.EndsWith("'")) -or
                ($value.StartsWith('"') -and $value.EndsWith('"'))
            )
        ) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        $values[$key] = $value
    }

    return $values
}

$mutex = New-Object System.Threading.Mutex($false, $scriptMutexName)
$hasLock = $false
try {
    $hasLock = $mutex.WaitOne(0)
    if (-not $hasLock) {
        Write-Host "Ya hay una ejecucion de start-all en curso. Espera un momento y vuelve a intentarlo."
        exit 1
    }

    Stop-TrackedProcesses
    Stop-ExistingDevWindows
    Stop-DevProcessesByCommandLine
    Stop-PortProcess -Port 8000
    Stop-PortProcess -Port 5173
    Ensure-BackendPrerequisites
    Ensure-FrontendPrerequisites
    $confidencePolicyValues = Read-DotEnvValues -Path $backendDotEnvFile -Keys $confidencePolicyEnvKeys
    $backendEnvAssignments = @("`$env:VET_RECORDS_EXTRACTION_OBS='1'")
    foreach ($key in $confidencePolicyEnvKeys) {
        if (-not $confidencePolicyValues.ContainsKey($key)) {
            continue
        }
        $rawValue = [string]$confidencePolicyValues[$key]
        if ([string]::IsNullOrWhiteSpace($rawValue)) {
            continue
        }
        $escapedValue = $rawValue.Replace("'", "''")
        $backendEnvAssignments += "`$env:$key='$escapedValue'"
    }
    $backendEnvAssignments += "& '$venvPython' -m uvicorn backend.app.main:create_app --factory --reload"
    $backendCommand = $backendEnvAssignments -join "; "
    $backendProcess = Start-DevConsole -WorkingDirectory $repoRoot -CommandToRun $backendCommand -WindowTitle $backendWindowTitle
    $frontendProcess = Start-DevConsole -WorkingDirectory $frontendDir -CommandToRun "npm run dev" -WindowTitle $frontendWindowTitle

    @{
        pids = @($backendProcess.Id, $frontendProcess.Id)
        started_at = (Get-Date).ToString("o")
    } | ConvertTo-Json | Set-Content -Path $processStateFile -Encoding UTF8

    Write-Host "Entorno iniciado: backend + frontend."
}
finally {
    if ($hasLock) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
