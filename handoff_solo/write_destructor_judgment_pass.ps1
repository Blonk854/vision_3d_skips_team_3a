# After worker_to_capm judgment: mint a pass id and overwrite
# maps/vector_ownership/team3_next_prompt.txt with the destructor_vs_workers
# judgment assignment from judgment_destructor_vs_workers.md.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_destructor_judgment_pass.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_destructor_judgment_pass.ps1 -DryRun
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_destructor_judgment_pass.ps1 -Force
#
# Refuses unless the trace contains "Worker to CAPM judgment", unless -Force.

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$promptPath = Join-Path $repoRoot 'maps\vector_ownership\team3_next_prompt.txt'
$tracePath = Join-Path $repoRoot 'maps\vector_ownership\anomaly_begin_store_trace.txt'
$templatePath = Join-Path $PSScriptRoot 'judgment_destructor_vs_workers.md'
$ledgerPath = Join-Path $PSScriptRoot '.advanced'
$lockDir = Join-Path $repoRoot 'v3d_files_uncomp_copy'
$RequiredHeading = 'Worker to CAPM judgment'
$DoneHeading = 'Destructor vs workers judgment'

function Get-TemplateBody {
    $raw = [System.IO.File]::ReadAllText($templatePath)
    $m = [regex]::Match($raw, '(?s)```\r?\n(.*)\r?\n```')
    if (-not $m.Success) { throw "no fenced template body in $templatePath" }
    return $m.Groups[1].Value.TrimEnd() + "`n"
}

function Test-HeadingPresent([string]$inner) {
    $needle = "===== $inner ====="
    foreach ($line in [System.IO.File]::ReadLines($tracePath)) {
        if ($line -eq $needle) { return $true }
    }
    return $false
}

function Get-LastHeadingInner {
    $last = $null
    foreach ($line in [System.IO.File]::ReadLines($tracePath)) {
        if ($line -match '^===== .+ =====$' -and $line -ne '===== END =====') {
            $last = $line
        }
    }
    if (-not $last) { throw "no ===== heading found in $tracePath" }
    if ($last.StartsWith('===== ') -and $last.EndsWith(' =====')) {
        return $last.Substring(6, $last.Length - 12)
    }
    throw "malformed heading: $last"
}

function New-PassId {
    $utc = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $bytes = New-Object byte[] 4
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $hex = ($bytes | ForEach-Object { $_.ToString('x2') }) -join ''
    return "$utc-$hex"
}

function Test-IdUsed([string]$id) {
    foreach ($p in @(
            $ledgerPath,
            (Join-Path $repoRoot 'handoff\.rotated'),
            (Join-Path $repoRoot 'handoff_oc\.rotated')
        )) {
        if (-not (Test-Path -LiteralPath $p)) { continue }
        foreach ($line in Get-Content -LiteralPath $p) {
            if ($line.Trim() -eq $id) { return $true }
        }
    }
    return $false
}

$locks = @(Get-ChildItem -LiteralPath $lockDir -Filter 'V3D_SKIP.lock*' -Force -ErrorAction SilentlyContinue)
if ($locks.Count -gt 0) {
    $detail = ($locks | ForEach-Object { '{0} ({1} bytes, {2})' -f $_.Name, $_.Length, $_.LastWriteTime }) -join '; '
    throw "lock present: $detail. Not writing destructor judgment prompt."
}

if (-not (Test-Path -LiteralPath $tracePath)) { throw "missing $tracePath" }
if (-not (Test-Path -LiteralPath $templatePath)) { throw "missing $templatePath" }

if (-not $Force -and -not (Test-HeadingPresent $RequiredHeading)) {
    throw "trace missing ===== $RequiredHeading =====. Finish worker_to_capm judgment first (or pass -Force)."
}

$lastInner = Get-LastHeadingInner
if (-not $Force -and $lastInner -eq $DoneHeading) {
    throw "trace already ends with $DoneHeading. Judgment done (or pass -Force to rewrite the prompt)."
}

$passId = New-PassId
while (Test-IdUsed $passId) { Start-Sleep -Milliseconds 50; $passId = New-PassId }

$body = Get-TemplateBody
$body = $body.Replace('{{PASS_ID}}', $passId)
if ($body -match '\{\{[A-Z_]+\}\}') {
    throw "unreplaced placeholder remains in filled destructor judgment template"
}

"destructor judgment: pass $passId (prerequisite heading present)"

if ($DryRun) {
    'dry run: prompt not written'
    $body
    return
}

$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($promptPath, $body, $utf8)
Add-Content -LiteralPath $ledgerPath -Value $passId -Encoding utf8
"wrote $promptPath"
"recorded $passId in $ledgerPath"
"Next: open a fresh strong-model session and answer Pass $passId from maps/vector_ownership/team3_next_prompt.txt."
