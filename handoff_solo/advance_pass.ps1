# After a holding sync-byte pass: write the next team3_next_prompt.txt from
# pass_template.md (address+1, new pass id, heading tail from the trace).
# Does not call Ghidra, does not append the trace, does not rotate windows.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/advance_pass.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/advance_pass.ps1 -DryRun
#
# Refuses unless the last trace section's Address matches the open prompt
# address (evidence the current pass landed). Use -Force only to repair.

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$promptPath = Join-Path $repoRoot 'maps\vector_ownership\team3_next_prompt.txt'
$tracePath = Join-Path $repoRoot 'maps\vector_ownership\anomaly_begin_store_trace.txt'
$templatePath = Join-Path $PSScriptRoot 'pass_template.md'
$ledgerPath = Join-Path $PSScriptRoot '.advanced'
$lockDir = Join-Path $repoRoot 'v3d_files_uncomp_copy'
$AddrMin = [uint64]0x140001000
$AddrMax = [uint64]0x140d509ff
$HeadingAnchor = ' 89 75 67 '

function Format-Addr([uint64]$n) {
    return ('0x{0:x9}' -f $n)
}

function Get-TemplateBody {
    $raw = [System.IO.File]::ReadAllText($templatePath)
    $m = [regex]::Match($raw, '(?s)```\r?\n(.*)\r?\n```')
    if (-not $m.Success) { throw "no fenced template body in $templatePath" }
    return $m.Groups[1].Value.TrimEnd() + "`n"
}

function Get-PromptAddress {
    $text = [System.IO.File]::ReadAllText($promptPath)
    $m = [regex]::Match($text, 'Call `memory_read` once at `(0x[0-9a-fA-F]+)`')
    if (-not $m.Success) { throw "could not parse memory_read address from $promptPath" }
    $s = $m.Groups[1].Value.ToLowerInvariant()
    if ($s -notmatch '^0x[0-9a-f]{9}$') { throw "prompt address '$s' is not 0x + 9 hex digits" }
    return [uint64]::Parse($s.Substring(2), [System.Globalization.NumberStyles]::AllowHexSpecifier)
}

function Get-PromptPassId {
    foreach ($line in @(Get-Content -LiteralPath $promptPath -TotalCount 3)) {
        if ($line -match '^Pass id:\s*(\S+)\s*$') { return $Matches[1] }
    }
    throw "no Pass id line in $promptPath"
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

function Get-LastSectionAddress {
    # Walk to the last non-END heading, then take the next Address: `0x...` line.
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
    throw "no Address line in last trace section"
}

function Get-HeadingTail([string]$inner) {
    $idx = $inner.IndexOf($HeadingAnchor)
    if ($idx -ge 0) { return $inner.Substring($idx) }
    # Fallback: keep the prompt size bounded but exact.
    if ($inner.Length -gt 800) { return $inner.Substring($inner.Length - 800) }
    return $inner
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
    throw "lock present: $detail. Not advancing."
}

if (-not (Test-Path -LiteralPath $promptPath)) { throw "missing $promptPath" }
if (-not (Test-Path -LiteralPath $tracePath)) { throw "missing $tracePath" }
if (-not (Test-Path -LiteralPath $templatePath)) { throw "missing $templatePath" }

$prevAddr = Get-PromptAddress
$prevId = Get-PromptPassId
$sectionAddr = Get-LastSectionAddress
if (-not $Force -and $sectionAddr -ne $prevAddr) {
    throw ("last trace Address {0} does not match open prompt {1}. Finish the open pass (or pass -Force). Not advancing." -f (Format-Addr $sectionAddr), (Format-Addr $prevAddr))
}

$nextAddr = $prevAddr + [uint64]1
if ($nextAddr -lt $AddrMin -or $nextAddr -gt $AddrMax) {
    throw ("next address {0} is outside .text {1}..{2}. Sync walk bound reached." -f (Format-Addr $nextAddr), (Format-Addr $AddrMin), (Format-Addr $AddrMax))
}

$headingInner = Get-LastHeadingInner
$headingTail = Get-HeadingTail $headingInner
$passId = New-PassId
while (Test-IdUsed $passId) { Start-Sleep -Milliseconds 50; $passId = New-PassId }

$body = Get-TemplateBody
$body = $body.Replace('{{PASS_ID}}', $passId)
$body = $body.Replace('{{ADDRESS}}', (Format-Addr $nextAddr))
$body = $body.Replace('{{PREV_ADDRESS}}', (Format-Addr $prevAddr))
$body = $body.Replace('{{HEADING_TAIL}}', $headingTail)

if ($body -match '\{\{[A-Z_]+\}\}') {
    throw "unreplaced placeholder remains in filled template"
}

"advance: $prevId $(Format-Addr $prevAddr) -> $passId $(Format-Addr $nextAddr)"
"heading tail ends: ...$($headingTail.Substring([Math]::Max(0, $headingTail.Length - 80)))"

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
