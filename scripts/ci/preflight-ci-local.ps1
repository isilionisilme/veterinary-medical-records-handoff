[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [ValidateSet("Quick", "Push", "Full")]
    [string]$Mode = "Push",
    [switch]$All,
    [switch]$ForceFrontend,
    [switch]$ForceFull,
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    # Restrict changed-file detection to the commit range only (mirrors what
    # GitHub Actions sees on push/PR). Excludes staged/unstaged local edits.
    [switch]$ParityMode
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib\repo-root.ps1")
$repoRoot = Get-RepoRoot -ScriptRoot $PSScriptRoot
Set-Location $repoRoot

function Resolve-RemoteBranchName {
    param(
        [Parameter(Mandatory = $true)][string]$BaseRefValue
    )

    $normalized = $BaseRefValue.Trim()

    if ($normalized.StartsWith("refs/heads/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $normalized.Substring("refs/heads/".Length)
    }

    if ($normalized.StartsWith("origin/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $normalized.Substring("origin/".Length)
    }

    return $normalized
}

function Assert-RemoteBaseUpToDate {
    param(
        [Parameter(Mandatory = $true)][string]$BaseRefValue
    )

    $remoteBranchName = Resolve-RemoteBranchName -BaseRefValue $BaseRefValue

    $currentBranch = (& git rev-parse --abbrev-ref HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $currentBranch) {
        throw "Unable to resolve current branch while checking remote base sync."
    }

    # Skip sync check on main; this guard is intended for feature branches before push.
    if ($currentBranch -eq "main") {
        Write-Host "Remote base sync guard skipped on 'main'."
        return
    }

    & git fetch --quiet origin $remoteBranchName
    if ($LASTEXITCODE -ne 0) {
        throw "Remote base sync guard failed: could not fetch origin/$remoteBranchName."
    }

    & git show-ref --verify --quiet ("refs/remotes/origin/{0}" -f $remoteBranchName)
    if ($LASTEXITCODE -ne 0) {
        throw "Remote base sync guard failed: origin/$remoteBranchName does not exist locally after fetch."
    }

    & git merge-base --is-ancestor ("origin/{0}" -f $remoteBranchName) HEAD
    if ($LASTEXITCODE -ne 0) {
        throw (
            "Remote base sync guard failed: branch '$currentBranch' is behind origin/$remoteBranchName. " +
            "Rebase or merge origin/$remoteBranchName before pushing."
        )
    }

    Write-Host "Remote base sync guard passed: HEAD contains origin/$remoteBranchName."
}
function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

    function Compare-ConfigWithReference {
        $configMappings = @(
            @{ Source = "backend/requirements.txt"; Reference = "requirements.txt" },
            @{ Source = "package.json"; Reference = "package.json" },
            @{ Source = "Dockerfile.backend"; Reference = "Dockerfile.backend" },
            @{ Source = "Dockerfile.frontend"; Reference = "Dockerfile.frontend" },
            @{ Source = ".env.example"; Reference = ".env.example" }
        )
        $referenceDir = Join-Path $repoRoot ".ci-config-reference"
        if (-not (Test-Path $referenceDir)) {
            Write-Host "No reference config directory found: $referenceDir. Skipping config sync check."
            return
        }

        $missingFiles = @()
        $differences = @()
        foreach ($mapping in $configMappings) {
            $sourcePath = Join-Path $repoRoot $mapping.Source
            $referencePath = Join-Path $referenceDir $mapping.Reference
            $hasSource = Test-Path $sourcePath
            $hasReference = Test-Path $referencePath

            if (-not $hasSource -or -not $hasReference) {
                if (-not $hasSource) {
                    $missingFiles += "source:$($mapping.Source)"
                }
                if (-not $hasReference) {
                    $missingFiles += "reference:$($mapping.Reference)"
                }
                continue
            }

            $sourceHash = Get-FileHash $sourcePath | Select-Object -ExpandProperty Hash
            $referenceHash = Get-FileHash $referencePath | Select-Object -ExpandProperty Hash
            if ($sourceHash -ne $referenceHash) {
                $differences += "$($mapping.Source) -> $($mapping.Reference)"
            }
        }

        if ($missingFiles.Count -gt 0) {
            $message = "Config sync guard failed: Missing required config files: $($missingFiles -join ', ')"
            Write-Error $message
            throw $message
        }

        if ($differences.Count -gt 0) {
            $message = "Config sync guard failed: Config files differ from CI reference: $($differences -join ', ')"
            Write-Error $message
            throw $message
        } else {
            Write-Host "Config sync guard passed: Local config matches CI reference."
        }
    }
    Write-Host "`n==> $Name" -ForegroundColor Cyan
    $global:LASTEXITCODE = 0
    & $Action
    if (-not $?) {
        throw "Step failed: $Name"
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed with exit code ${LASTEXITCODE}: $Name"
    }
}

function Get-GitOutput {
    param([string[]]$Arguments)

    $output = & git @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) {
        return @()
    }

    if (-not $output) {
        return @()
    }

    return @($output | ForEach-Object { $_.ToString().Trim() } | Where-Object { $_ })
}

function Get-ChangedFiles {
    param(
        [string]$BaseRefValue,
        [bool]$CommitDiffOnly = $false
    )

    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    if ($CommitDiffOnly) {
        # Parity mode: only the commit-range diff; mirrors what GitHub Actions sees.
        $sources = @(
            @("diff", "--name-only", "$BaseRefValue...HEAD")
        )
    } else {
        $sources = @(
            @("diff", "--name-only", "$BaseRefValue...HEAD"),
            @("diff", "--name-only"),
            @("diff", "--name-only", "--cached")
        )
    }

    foreach ($gitArgs in $sources) {
        foreach ($line in (Get-GitOutput -Arguments $gitArgs)) {
            $normalized = $line.Replace("\", "/")
            [void]$set.Add($normalized)
        }
    }

    $files = @($set | Sort-Object)
    if ($null -eq $files) {
        return @()
    }

    return $files
}

function Filter-ChangedFiles {
    param(
        [Parameter()][AllowEmptyCollection()][string[]]$Files = @(),
        [Parameter(Mandatory = $true)][string[]]$Patterns
    )

    $result = @()

    foreach ($filePath in $Files) {
        if (Test-MatchesAny -Path $filePath -Patterns $Patterns) {
            $result += $filePath
        }
    }

    return @($result)
}

function Filter-ChangedExtensions {
    param(
        [Parameter()][AllowEmptyCollection()][string[]]$Files = @(),
        [Parameter(Mandatory = $true)][string[]]$Extensions
    )

    $result = @()

    foreach ($filePath in $Files) {
        foreach ($ext in $Extensions) {
            if ($filePath.EndsWith($ext, [System.StringComparison]::OrdinalIgnoreCase)) {
                $result += $filePath
                break
            }
        }
    }

    return @($result)
}

function Convert-ToFrontendRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ($Path.StartsWith("frontend/", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Substring("frontend/".Length)
    }

    return $Path
}

function Invoke-FrontendCommand {
    param([Parameter(Mandatory = $true)][scriptblock]$Action)

    Push-Location (Join-Path $repoRoot "frontend")
    try {
        & $Action
    }
    finally {
        Pop-Location
    }
}

function Test-MatchesAny {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        if ($Path -like $pattern) {
            return $true
        }
    }

    return $false
}

function Resolve-PythonCommand {
    $localVenvPython = Join-Path $repoRoot ".venv/Scripts/python.exe"
    if (Test-Path $localVenvPython) {
        return $localVenvPython
    }

    if ($env:VIRTUAL_ENV) {
        $activeVenvPython = Join-Path $env:VIRTUAL_ENV "Scripts/python.exe"
        if (Test-Path $activeVenvPython) {
            return $activeVenvPython
        }
    }

    return "python"
}

function Resolve-NpmCommand {
    $npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue)
    if ($npmCmd) {
        return $npmCmd.Source
    }

    return "npm"
}

function Get-ListeningProcessIds {
    param([Parameter(Mandatory = $true)][int]$Port)

    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $listeners) {
        return @()
    }

    return @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
}

function Stop-ManagedPortProcesses {
    param([Parameter(Mandatory = $true)][int[]]$Ports)

    foreach ($port in $Ports) {
        foreach ($processId in (Get-ListeningProcessIds -Port $port)) {
            try {
                $process = Get-Process -Id $processId -ErrorAction Stop
            }
            catch {
                continue
            }

            if ($process.ProcessName -in @("python", "node")) {
                Stop-Process -Id $processId -Force -ErrorAction Stop
                Write-Host "Stopped lingering $($process.ProcessName) PID $processId on port $port"
            }
        }
    }
}

function Test-PortAvailable {
    param([Parameter(Mandatory = $true)][int]$Port)

    return (Get-ListeningProcessIds -Port $Port).Count -eq 0
}

function Select-LocalE2EPortPair {
    $candidates = @(
        @{ Backend = 18000; Frontend = 15173 },
        @{ Backend = 28000; Frontend = 25173 },
        @{ Backend = 38000; Frontend = 35173 }
    )

    foreach ($candidate in $candidates) {
        if ((Test-PortAvailable -Port $candidate.Backend) -and (Test-PortAvailable -Port $candidate.Frontend)) {
            return $candidate
        }

        Write-Host "Skipping occupied local E2E port pair $($candidate.Backend)/$($candidate.Frontend)."
    }

    throw "Unable to find a clean local E2E port pair. Checked: 18000/15173, 28000/25173, 38000/35173."
}

$python = Resolve-PythonCommand
$npm = Resolve-NpmCommand

if ($All.IsPresent) {
    $Mode = "Full"
}

$changedFiles = @(Get-ChangedFiles -BaseRefValue $BaseRef -CommitDiffOnly:$ParityMode.IsPresent)

Write-Host "preflight-ci-local: mode=$Mode base-ref=$BaseRef parity-mode=$($ParityMode.IsPresent)"
if ($changedFiles.Count -eq 0) {
    Write-Host "No changed files detected (branch diff + staged + unstaged)."
}
else {
    Write-Host "Changed files:"
    $changedFiles | ForEach-Object { Write-Host " - $_" }
}

$backendPatterns = @(
    "backend/*",
    "requirements*.txt",
    "pyproject.toml",
    "pytest.ini"
)

$frontendPatterns = @(
    "frontend/*"
)

$frontendImpactPatterns = @(
    "frontend/*",
    "shared/*",
    "package.json",
    "frontend/package.json",
    "frontend/package-lock.json",
    "backend/app/api/*",
    "backend/app/domain/models.py",
    "backend/app/application/global_schema.py",
    "backend/app/main.py",
    "backend/app/config.py",
    "backend/app/settings.py",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    ".env.example",
    "Dockerfile.frontend"
)

$docsPatterns = @(
    "docs/*",
    "*.md",
    "scripts/*"
)

$dockerPackagingPatterns = @(
    ".dockerignore",
    ".env.example",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    ".github/workflows/ci.yml",
    "shared/*",
    "backend/*",
    "frontend/*"
)

$backendChangedFiles = Filter-ChangedFiles -Files $changedFiles -Patterns $backendPatterns
$frontendChangedFiles = Filter-ChangedFiles -Files $changedFiles -Patterns $frontendPatterns
$frontendImpactFiles = Filter-ChangedFiles -Files $changedFiles -Patterns $frontendImpactPatterns
$docsChangedFiles = Filter-ChangedFiles -Files $changedFiles -Patterns $docsPatterns
$dockerChangedFiles = Filter-ChangedFiles -Files $changedFiles -Patterns $dockerPackagingPatterns

$backendChanged = [bool]($backendChangedFiles | Select-Object -First 1)
$frontendChanged = [bool]($frontendChangedFiles | Select-Object -First 1)
$frontendImpacted = [bool]($frontendImpactFiles | Select-Object -First 1)
$docsChanged = [bool]($docsChangedFiles | Select-Object -First 1)
$dockerChanged = [bool]($dockerChangedFiles | Select-Object -First 1)

$forceFrontendChecks = $ForceFrontend.IsPresent -or $ForceFull.IsPresent
$forceAllChecks = $All.IsPresent -or $ForceFull.IsPresent

$runDocs = $false
$runBackendQuick = $false
$runBackendFull = $false
$runFrontendQuick = $false
$runFrontendFull = $false
$runFrontendGuards = $false
$runDocker = $false
$runE2E = $false
$runBranchNameValidation = $false

switch ($Mode) {
    "Quick" {
        $runDocs = $docsChanged
        $runBackendQuick = $backendChanged
        $runFrontendQuick = $frontendChanged
        $runFrontendGuards = $false
        $runDocker = $false
        $runE2E = $false
    }
    "Push" {
        $runBranchNameValidation = $true
        $runDocs = $docsChanged
        $runBackendFull = $backendChanged
        # Mirror remote: frontend_test_build fires when backend OR frontend changed.
        $runFrontendFull = $frontendImpacted -or $backendChanged -or $forceFrontendChecks
        # Mirror remote frontend guards: frontend-only unless explicitly forced.
        $runFrontendGuards = $frontendImpacted -or $forceFrontendChecks
        $runDocker = -not $SkipDocker.IsPresent -and $dockerChanged
        $runE2E = $false
    }
    "Full" {
        $runDocs = $true
        $runBackendFull = $backendChanged -or $forceAllChecks
        # Mirror remote: frontend_test_build and e2e fire when backend OR frontend changed.
        $runFrontendFull = $frontendImpacted -or $backendChanged -or $forceFrontendChecks
        # Mirror remote frontend guards: frontend-only unless explicitly forced.
        $runFrontendGuards = $frontendImpacted -or $forceFrontendChecks
        $runDocker = -not $SkipDocker.IsPresent -and ($dockerChanged -or $forceAllChecks)
        $runE2E = -not $SkipE2E.IsPresent -and ($frontendImpacted -or $backendChanged -or $forceFrontendChecks)
    }
}

Write-Host "`nExecution plan:"
Write-Host " - Docs guards:      $runDocs"
Write-Host " - Backend quick:    $runBackendQuick"
Write-Host " - Backend full:     $runBackendFull"
Write-Host " - Frontend quick:   $runFrontendQuick"
Write-Host " - Frontend full:    $runFrontendFull"
Write-Host " - Frontend guards:  $runFrontendGuards"
Write-Host " - Docker guard:     $runDocker"
Write-Host " - E2E:              $runE2E"
Write-Host " - Branch naming:    $runBranchNameValidation"
Write-Host " - Frontend impacted:$frontendImpacted"
Write-Host " - Force frontend:   $forceFrontendChecks"

if ($frontendImpactFiles.Count -gt 0) {
    Write-Host " - Frontend impact matches:"
    $frontendImpactFiles | ForEach-Object { Write-Host "   - $_" }
}
else {
    Write-Host " - Frontend impact matches: none"
}

if (($Mode -eq "Push" -or $Mode -eq "Full") -and -not $runFrontendFull) {
    Write-Host " - Frontend checks skipped: no frontend/backend-impact paths (use -ForceFrontend to override)"
}

if ($ParityMode.IsPresent) {
    Write-Host " - Parity mode: file detection restricted to commit range only (staged/unstaged excluded)"
}

if ($runBranchNameValidation) {
    Invoke-Step "Branch naming guard" {
        & (Join-Path $repoRoot "scripts/ci/validate-branch-name.ps1")
    }
}

if ($runDocs) {
    # Note: Doc governance checks (canonical router, test sync, parity, directionality, drift) have been
    # moved to .github/workflows/doc-governance.yml. They run automatically on all PRs and can be triggered
    # manually via workflow_dispatch. For local validation, run that workflow manually or review the PR checks.
    Invoke-Step "Docs QA (lint/format/links/frontmatter)" {
        & $python "scripts/docs/run_docs_qa.py" "--base-ref" $BaseRef
    }
}

if ($Mode -eq "Push") {
    Invoke-Step "Remote base sync guard" {
        Assert-RemoteBaseUpToDate -BaseRefValue $BaseRef
    }
}

if ($Mode -eq "Push" -or $Mode -eq "Full") {
        Invoke-Step "Config sync guard (local vs CI reference)" {
            Compare-ConfigWithReference
        }
}

if ($runBackendQuick) {
    $backendPythonFiles = Filter-ChangedExtensions -Files $backendChangedFiles -Extensions @(".py")
    if ($backendPythonFiles.Count -gt 0) {
        Invoke-Step "Backend quick lint (Ruff changed files)" {
            foreach ($backendPythonFile in $backendPythonFiles) {
                & $python -m ruff check $backendPythonFile
                if (-not $?) {
                    throw "Ruff lint failed for $backendPythonFile"
                }
                if ($LASTEXITCODE -ne 0) {
                    throw "Ruff lint failed for $backendPythonFile with exit code ${LASTEXITCODE}"
                }
            }
        }

        Invoke-Step "Backend quick format check (Ruff changed files)" {
            foreach ($backendPythonFile in $backendPythonFiles) {
                & $python -m ruff format --check $backendPythonFile
                if (-not $?) {
                    throw "Ruff format check failed for $backendPythonFile"
                }
                if ($LASTEXITCODE -ne 0) {
                    throw "Ruff format check failed for $backendPythonFile with exit code ${LASTEXITCODE}"
                }
            }
        }
    }
    else {
        Write-Host "No changed Python backend files for quick backend checks."
    }
}

if ($runBackendFull) {
    Invoke-Step "Backend lint (Ruff)" {
        & $python -m ruff check .
    }

    Invoke-Step "Backend format check (Ruff)" {
        & $python -m ruff format --check .
    }

    Invoke-Step "Backend tests (Pytest + coverage)" {
        & pytest -x --tb=short --cov=backend/app --cov-report=term-missing
    }

    Invoke-Step "Backend security audit (pip-audit)" {
        & pip-audit --requirement backend/requirements.txt --strict --ignore-vuln GHSA-2c2j-9gv5-cj73 --ignore-vuln GHSA-7f5h-v6xp-fcq8
    }

    Invoke-Step "Backend complexity prerequisites" {
        & $python -m radon --version
    }

    Invoke-Step "Backend complexity gate" {
        & $python "scripts/quality/architecture_metrics.py" --check --base-ref $BaseRef --warn-cc 11 --max-cc 30 --max-loc 500
    }
}

if ($runFrontendQuick) {
    $frontendLintFiles = Filter-ChangedExtensions -Files $frontendChangedFiles -Extensions @(".ts", ".tsx", ".js", ".jsx")
    $frontendFormatFiles = Filter-ChangedExtensions -Files $frontendChangedFiles -Extensions @(".ts", ".tsx", ".js", ".jsx", ".css")

    if ($frontendLintFiles.Count -gt 0) {
        Invoke-Step "Frontend quick lint (changed files)" {
            foreach ($frontendLintFile in $frontendLintFiles) {
                $frontendRelativePath = Convert-ToFrontendRelativePath $frontendLintFile
                Invoke-FrontendCommand {
                    & $npm exec eslint $frontendRelativePath
                }
                if (-not $?) {
                    throw "ESLint failed for $frontendLintFile"
                }
                if ($LASTEXITCODE -ne 0) {
                    throw "ESLint failed for $frontendLintFile with exit code ${LASTEXITCODE}"
                }
            }
        }
    }
    else {
        Write-Host "No changed frontend lint-target files for quick lint."
    }

    if ($frontendFormatFiles.Count -gt 0) {
        Invoke-Step "Frontend quick format check (changed files)" {
            foreach ($frontendFormatFile in $frontendFormatFiles) {
                $frontendRelativePath = Convert-ToFrontendRelativePath $frontendFormatFile
                Invoke-FrontendCommand {
                    & $npm exec prettier --check $frontendRelativePath
                }
                if (-not $?) {
                    throw "Prettier check failed for $frontendFormatFile"
                }
                if ($LASTEXITCODE -ne 0) {
                    throw "Prettier check failed for $frontendFormatFile with exit code ${LASTEXITCODE}"
                }
            }
        }
    }
    else {
        Write-Host "No changed frontend format-target files for quick format check."
    }
}

if ($runFrontendFull) {
    Invoke-Step "Frontend dependencies" {
        Invoke-FrontendCommand {
            & $npm ci
        }
    }

    Invoke-Step "Frontend lint" {
        Invoke-FrontendCommand {
            & $npm run lint
        }
    }

    Invoke-Step "Frontend format check" {
        Invoke-FrontendCommand {
            & $npm run format:check
        }
    }

    Invoke-Step "Frontend tests (coverage)" {
        Invoke-FrontendCommand {
            & $npm run test:coverage
        }
    }

    Invoke-Step "Frontend build" {
        Invoke-FrontendCommand {
            & $npm run build
        }
    }
}

if ($runE2E) {
    Invoke-Step "Frontend E2E (Playwright)" {
        $selectedPorts = Select-LocalE2EPortPair
        $runtimeRoot = Join-Path $env:TEMP ("vmr-playwright-e2e-{0}-{1}" -f $PID, $selectedPorts.Backend)
        $storageRoot = Join-Path $runtimeRoot "storage"
        $dbPath = Join-Path $runtimeRoot "documents.db"

        New-Item -ItemType Directory -Force -Path $storageRoot | Out-Null

        $previousBackendPort = $env:PLAYWRIGHT_BACKEND_PORT
        $previousFrontendPort = $env:PLAYWRIGHT_FRONTEND_PORT
        $previousBackendBaseUrl = $env:PLAYWRIGHT_BACKEND_BASE_URL
        $previousBaseUrl = $env:PLAYWRIGHT_BASE_URL
        $previousDbPath = $env:VET_RECORDS_DB_PATH
        $previousStoragePath = $env:VET_RECORDS_STORAGE_PATH
        $previousExternalServers = $env:PLAYWRIGHT_EXTERNAL_SERVERS

        $env:PLAYWRIGHT_BACKEND_PORT = "$($selectedPorts.Backend)"
        $env:PLAYWRIGHT_FRONTEND_PORT = "$($selectedPorts.Frontend)"
        $env:PLAYWRIGHT_BACKEND_BASE_URL = "http://127.0.0.1:$($selectedPorts.Backend)"
        $env:PLAYWRIGHT_BASE_URL = "http://127.0.0.1:$($selectedPorts.Frontend)"
        $env:VET_RECORDS_DB_PATH = $dbPath
        $env:VET_RECORDS_STORAGE_PATH = $storageRoot
        $env:PLAYWRIGHT_EXTERNAL_SERVERS = "0"

        Write-Host "Local E2E runtime selected backend port $($selectedPorts.Backend) and frontend port $($selectedPorts.Frontend)."

        try {
            Invoke-FrontendCommand {
                & $npm run test:e2e
            }
        }
        finally {
            $env:PLAYWRIGHT_BACKEND_PORT = $previousBackendPort
            $env:PLAYWRIGHT_FRONTEND_PORT = $previousFrontendPort
            $env:PLAYWRIGHT_BACKEND_BASE_URL = $previousBackendBaseUrl
            $env:PLAYWRIGHT_BASE_URL = $previousBaseUrl
            $env:VET_RECORDS_DB_PATH = $previousDbPath
            $env:VET_RECORDS_STORAGE_PATH = $previousStoragePath
            $env:PLAYWRIGHT_EXTERNAL_SERVERS = $previousExternalServers
            Stop-ManagedPortProcesses -Ports @($selectedPorts.Backend, $selectedPorts.Frontend)
        }
    }
}

if ($runFrontendGuards) {
    Invoke-Step "Brand guard (frontend changed)" {
        & $python "scripts/quality/check_brand_compliance.py" "--base-ref" $BaseRef
    }

    Invoke-Step "Frontend design system guard" {
        Invoke-FrontendCommand {
            & $npm run check:design-system
        }
    }
}

if ($runDocker) {
    Invoke-Step "Build backend image" {
        & docker build -f Dockerfile.backend -t vetrecords-backend:ci .
    }

    Invoke-Step "Assert backend shared contract in image" {
        $backendCid = (& docker create vetrecords-backend:ci).Trim()
        try {
            $backendContract = Join-Path $env:TEMP "backend_global_schema_contract.json"
            if (Test-Path $backendContract) {
                Remove-Item $backendContract -Force
            }
            & docker cp "${backendCid}:/app/shared/global_schema_contract.json" $backendContract
            if (-not (Test-Path $backendContract)) {
                throw "backend global schema contract missing in image"
            }
        }
        finally {
            & docker rm -f $backendCid | Out-Null
        }
    }

    Invoke-Step "Build frontend image" {
        & docker build -f Dockerfile.frontend -t vetrecords-frontend:ci .
    }

    Invoke-Step "Assert frontend shared contract in image" {
        $frontendCid = (& docker create vetrecords-frontend:ci).Trim()
        try {
            $frontendContract = Join-Path $env:TEMP "frontend_global_schema_contract.json"
            if (Test-Path $frontendContract) {
                Remove-Item $frontendContract -Force
            }
            & docker cp "${frontendCid}:/app/shared/global_schema_contract.json" $frontendContract
            if (-not (Test-Path $frontendContract)) {
                throw "frontend global schema contract missing in image"
            }
        }
        finally {
            & docker rm -f $frontendCid | Out-Null
        }
    }
}

if (-not ($runDocs -or $runBackendQuick -or $runBackendFull -or $runFrontendQuick -or $runFrontendFull -or $runFrontendGuards -or $runDocker -or $runE2E)) {
    Write-Host "No checks selected for mode $Mode with current changed paths."
}

Write-Host "`npreflight-ci-local: PASS" -ForegroundColor Green
