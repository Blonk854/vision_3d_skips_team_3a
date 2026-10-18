# After the sync-byte walk stops: mint a pass id and overwrite
# maps/vector_ownership/team3_next_prompt.txt with the worker_to_capm
# judgment assignment from judgment_worker_to_capm.md.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_judgment_pass.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_judgment_pass.ps1 -DryRun
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_judgment_pass.ps1 -Force
#
# Refuses unless the last trace Address is the last sync-walk byte
# (0x1406a2fff) or the open prompt is already past the +1 template, unless
# -Force. Does not call Ghidra, does not append the trace.

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$promptPath = Join-Path $repoRoot 'maps\vector_ownership\team3_next_prompt.txt'
$tracePath = Join-Path $repoRoot 'maps\vector_ownership\anomaly_begin_store_trace.txt'
$templatePath = Join-Path $PSScriptRoot 'judgment_worker_to_capm.md'
$ledgerPath = Join-Path $PSScriptRoot '.advanced'
$lockDir = Join-Path $repoRoot 'v3d_files_uncomp_copy'
$SyncWalkEnd = [uint64]0x1406a3000
$LastSyncAddr = $SyncWalkEnd - [uint64]1

function Format-Addr([uint64]$n) {
    return ('0x{0:x9}' -f $n)
}

function Get-TemplateBody {
    $raw = [System.IO.File]::ReadAllText($templatePath)
    $m = [regex]::Match($raw, '(?s)```\r?\n(.*)\r?\n```')
    if (-not $m.Success) { throw "no fenced template body in $templatePath" }
    return $m.Groups[1].Value.TrimEnd() + "`n"
}

function Get-LastSectionAddress {
    $lines = [System.IO.File]::ReadAllLines($tracePath)
    $headingIdx = -1
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '^===== .+ =====$' -and $lines[$i] -ne '===== END =====') {
            $headingIdx = $i
        }
    }
    if ($headingIdx -lt 0) { throw "no heading in trace" }
    for ($i = $headingIdx + 1; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -eq '===== END =====') { break }
        if ($lines[$i] -match '^Address:\s*`(0x[0-9a-fA-F]+)`\s*$') {
            $s = $Matches[1].ToLowerInvariant()
            if ($s -notmatch '^0x[0-9a-f]{9}$') { throw "trace Address '$s' is not 0x + 9 hex digits" }
            return [uint64]::Parse($s.Substring(2), [System.Globalization.NumberStyles]::AllowHexSpecifier)
        }
    }
    throw "no Address line in last trace section (sync walk may not be finished)"
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
    throw "lock present: $detail. Not writing judgment prompt."
}

if (-not (Test-Path -LiteralPath $tracePath)) { throw "missing $tracePath" }
if (-not (Test-Path -LiteralPath $templatePath)) { throw "missing $templatePath" }

$headingInner = Get-LastHeadingInner
if ($headingInner -eq 'Worker to CAPM judgment') {
    if (-not $Force) {
        throw "trace already ends with Worker to CAPM judgment. Judgment done (or pass -Force to rewrite the prompt)."
    }
}

$sectionAddr = $null
try {
    $sectionAddr = Get-LastSectionAddress
} catch {
    if (-not $Force) { throw }
}

if (-not $Force) {
    if ($null -eq $sectionAddr) {
        throw "could not read last sync Address from trace. Finish the sync walk (or pass -Force)."
    }
    if ($sectionAddr -lt $LastSyncAddr) {
        throw ("last trace Address {0} is before sync-walk end byte {1}. Finish the sync walk (or pass -Force)." -f (Format-Addr $sectionAddr), (Format-Addr $LastSyncAddr))
    }
    if ($sectionAddr -ge $SyncWalkEnd) {
        throw ("last trace Address {0} is at/past sync-walk end {1}. Unexpected; pass -Force only if repairing." -f (Format-Addr $sectionAddr), (Format-Addr $SyncWalkEnd))
    }
}

$passId = New-PassId
while (Test-IdUsed $passId) { Start-Sleep -Milliseconds 50; $passId = New-PassId }

$body = Get-TemplateBody
$body = $body.Replace('{{PASS_ID}}', $passId)
if ($body -match '\{\{[A-Z_]+\}\}') {
    throw "unreplaced placeholder remains in filled judgment template"
}

$addrNote = if ($null -ne $sectionAddr) { Format-Addr $sectionAddr } else { '(forced, no Address)' }
"judgment: pass $passId (last sync Address $addrNote)"

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
