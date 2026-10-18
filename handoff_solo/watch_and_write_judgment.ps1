# Poll until the sync-byte walk lands 0x1406a2fff, then run write_judgment_pass.ps1.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/watch_and_write_judgment.ps1
#
# Prints AGENT_LOOP_WAKE_handoff_solo_judgment lines for status. Exits 0 after
# a successful write. Ctrl+C to cancel.

[CmdletBinding()]
param(
    [int]$PollSeconds = 60
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$promptPath = Join-Path $repoRoot 'maps\vector_ownership\team3_next_prompt.txt'
$responsePath = Join-Path $repoRoot 'handoff\team3_response.md'
$tracePath = Join-Path $repoRoot 'maps\vector_ownership\anomaly_begin_store_trace.txt'
$writeScript = Join-Path $PSScriptRoot 'write_judgment_pass.ps1'
$LastSyncAddr = [uint64]0x1406a2fff

function Format-Addr([uint64]$n) { return ('0x{0:x9}' -f $n) }

function Get-LastSectionAddress {
    $fs = [System.IO.File]::Open($tracePath, 'Open', 'Read', 'ReadWrite')
    try {
        $sr = New-Object System.IO.StreamReader($fs)
        $text = $sr.ReadToEnd()
        $sr.Close()
    } finally {
        $fs.Close()
    }
    $addrs = [regex]::Matches($text, 'Address: `(0x[0-9a-fA-F]+)`') | ForEach-Object { $_.Groups[1].Value.ToLowerInvariant() }
    if ($addrs.Count -eq 0) { return $null }
    $s = $addrs[-1]
    if ($s -notmatch '^0x[0-9a-f]{9}$') { return $null }
    return [uint64]::Parse($s.Substring(2), [System.Globalization.NumberStyles]::AllowHexSpecifier)
}

function Get-FilePassId([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    foreach ($line in @(Get-Content -LiteralPath $path -TotalCount 3 -ErrorAction SilentlyContinue)) {
        if ($line -match '^Pass id:\s*(\S+)\s*$') { return $Matches[1] }
    }
    return $null
}

function Get-PromptAddress {
    if (-not (Test-Path -LiteralPath $promptPath)) { return $null }
    $text = [System.IO.File]::ReadAllText($promptPath)
    if ($text -match 'worker_to_capm judgment') { return 'judgment' }
    $m = [regex]::Match($text, 'Call `memory_read` once at `(0x[0-9a-fA-F]+)`')
    if (-not $m.Success) { return $null }
    $s = $m.Groups[1].Value.ToLowerInvariant()
    if ($s -notmatch '^0x[0-9a-f]{9}$') { return $null }
    return [uint64]::Parse($s.Substring(2), [System.Globalization.NumberStyles]::AllowHexSpecifier)
}

function Wake([string]$event, [string]$notes) {
    $payload = [ordered]@{
        event = $event
        notes = $notes
        time  = [DateTime]::UtcNow.ToString('o')
    }
    $json = ($payload | ConvertTo-Json -Compress)
    Write-Output ("AGENT_LOOP_WAKE_handoff_solo_judgment {0}" -f $json)
}

Wake 'baseline' 'watching for last sync Address 0x1406a2fff then write_judgment_pass.ps1'

$lastReportAddr = $null
while ($true) {
    try {
        $traceAddr = Get-LastSectionAddress
        $promptAddr = Get-PromptAddress
        $promptPass = Get-FilePassId $promptPath
        $respPass = Get-FilePassId $responsePath

        if ($promptAddr -eq 'judgment') {
            Wake 'already_judgment' ("prompt already judgment pass {0}" -f $promptPass)
            exit 0
        }

        if ($null -ne $traceAddr -and $traceAddr -ne $lastReportAddr) {
            $remain = if ($traceAddr -le $LastSyncAddr) { $LastSyncAddr - $traceAddr } else { 0 }
            Wake 'progress' ("trace={0} remain_to_2fff={1} promptPass={2} respPass={3}" -f (Format-Addr $traceAddr), $remain, $promptPass, $respPass)
            $lastReportAddr = $traceAddr
        }

        $ready = ($null -ne $traceAddr) -and ($traceAddr -eq $LastSyncAddr) -and
            ($null -ne $promptAddr) -and ($promptAddr -eq $LastSyncAddr) -and
            ($null -ne $promptPass) -and ($promptPass -eq $respPass)

        if ($ready) {
            Wake 'ready' '0x1406a2fff held; running write_judgment_pass.ps1'
            & powershell -NoProfile -ExecutionPolicy Bypass -File $writeScript
            if ($LASTEXITCODE -ne 0) {
                Wake 'write_failed' ("write_judgment_pass.ps1 exit {0}" -f $LASTEXITCODE)
                exit $LASTEXITCODE
            }
            $newPass = Get-FilePassId $promptPath
            Wake 'written' ("judgment prompt written pass={0}" -f $newPass)
            exit 0
        }
    } catch {
        Wake 'poll_error' $_.Exception.Message
    }

    Start-Sleep -Seconds $PollSeconds
}
