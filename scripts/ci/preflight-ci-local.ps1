[CmdletBinding()]
param(
    [string]$BaseRef = "main",
    [ValidateSet("Quick", "Push", "Full")]
    [string]$Mode = "Push",
    [switch]$All,
    [switch]$ForceFrontend,
    [switch]$ForceFull,
    [switch]$SkipDocker,
    [switch]$SkipE2E
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "lib\repo-root.ps1")
$repoRoot = Get-RepoRoot -ScriptRoot $PSScriptRoot
Set-Location $repoRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

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
    param([string]$BaseRefValue)

    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    $sources = @(
        @("diff", "--name-only", "$BaseRefValue...HEAD"),
        @("diff", "--name-only"),
        @("diff", "--name-only", "--cached")
    )

    foreach ($args in $sources) {
        foreach ($line in (Get-GitOutput -Arguments $args)) {
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
        [Parameter(Mandatory = $true)][string[]]$Files,
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
        [Parameter(Mandatory = $true)][string[]]$Files,
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

$python = Resolve-PythonCommand
$npm = Resolve-NpmCommand

if ($All.IsPresent) {
    $Mode = "Full"
}

$changedFiles = @(Get-ChangedFiles -BaseRefValue $BaseRef)

Write-Host "preflight-ci-local: mode=$Mode base-ref=$BaseRef"
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
        $runFrontendFull = $frontendImpacted -or $forceFrontendChecks
        $runFrontendGuards = $frontendImpacted -or $forceFrontendChecks
        $runDocker = -not $SkipDocker.IsPresent -and $dockerChanged
        $runE2E = $false
    }
    "Full" {
        $runDocs = $true
        $runBackendFull = $backendChanged -or $forceAllChecks
        $runFrontendFull = $frontendImpacted -or $forceFrontendChecks
        $runFrontendGuards = $frontendImpacted -or $forceFrontendChecks
        $runDocker = -not $SkipDocker.IsPresent -and ($dockerChanged -or $forceAllChecks)
        $runE2E = -not $SkipE2E.IsPresent -and ($frontendImpacted -or $forceFrontendChecks)
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
    Write-Host " - Frontend checks skipped: no frontend-impact paths (use -ForceFrontend to override)"
}

if ($runBranchNameValidation) {
    Invoke-Step "Branch naming guard" {
        & (Join-Path $repoRoot "scripts/ci/validate-branch-name.ps1")
    }
}

if ($runDocs) {
    $branchName = (& git rev-parse --abbrev-ref HEAD).Trim()
    if (-not $branchName) {
        throw "Unable to resolve current branch name for doc classification path."
    }
    $safeBranchName = ($branchName -replace '[^A-Za-z0-9_.-]', '_')
    $classificationDir = Join-Path $env:TEMP "vmr-doc-classification"
    $classificationFile = Join-Path $classificationDir ("{0}.json" -f $safeBranchName)

    Invoke-Step "Classify doc changes" {
        & $python "scripts/docs/classify_doc_change.py" "--base-ref" $BaseRef "--output" $classificationFile
    }

    Invoke-Step "Docs canonical guard" {
        & $python "scripts/docs/check_no_canonical_router_refs.py"
    }

    Invoke-Step "Doc/test sync guard" {
        & $python "scripts/docs/check_doc_test_sync.py" "--base-ref" $BaseRef "--classification-file" $classificationFile
    }

    Invoke-Step "Doc/router parity guard" {
        & $python "scripts/docs/check_doc_router_parity.py" "--base-ref" $BaseRef
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
        Invoke-FrontendCommand {
            & $npm run test:e2e
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
