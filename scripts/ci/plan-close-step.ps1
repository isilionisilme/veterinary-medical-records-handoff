[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [Parameter(Mandatory = $true)]
    [string]$StepId
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $PlanPath -PathType Leaf)) {
    Write-Error "Plan file not found: $PlanPath"
    exit 1
}

$content = Get-Content -LiteralPath $PlanPath -Raw -Encoding UTF8
$lines = $content -split "`r?`n"

$escapedStepId = [Regex]::Escape($StepId)
$targetRegex = "^\s*- \[ \].*\b$escapedStepId\b.*IN PROGRESS"
$checkboxRegex = "^\s*- \[[ xX]\]"
$sectionHeaderRegex = "^\s*##\s+"
$evidenceRegex = "^\s*(?:[-*]\s*)?(?:[—-]\s*)?(?:✅|Evidence:|Evidencia:|CI run:|Code commit:|Plan commit:)"

$targetIndex = -1
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match $targetRegex) {
        $targetIndex = $i
        break
    }
}

if ($targetIndex -lt 0) {
    Write-Error "Step $StepId not found or not IN PROGRESS in $PlanPath."
    exit 1
}

$hasEvidence = $false
for ($j = $targetIndex + 1; $j -lt $lines.Length; $j++) {
    $line = $lines[$j]
    if ($line -match $checkboxRegex) {
        break
    }
    if ($line -match $sectionHeaderRegex) {
        break
    }
    if ($line -match $evidenceRegex) {
        $hasEvidence = $true
        break
    }
}

if (-not $hasEvidence) {
    Write-Error "Step $StepId cannot be closed: no evidence found. Add a ✅ evidence line after the step before closing."
    exit 1
}

$updatedLine = $lines[$targetIndex] -replace "- \[ \]", "- [x]"
$updatedLine = $updatedLine -replace "\s*⏳\s*IN PROGRESS(?:\s*\([^\)]*\))?", ""
$updatedLine = $updatedLine -replace "\s{2,}", " "
$lines[$targetIndex] = $updatedLine.TrimEnd()

Set-Content -LiteralPath $PlanPath -Value ($lines -join [Environment]::NewLine) -Encoding UTF8
Write-Host "Step $StepId closed successfully in $PlanPath."
exit 0
