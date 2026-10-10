# One-shot: wakes once for the current pass, then exits. Starting a new
# watcher stops any older one, so at most one is ever running.
# A reply headed with the pass id but with no new ===== heading in the trace
# prints AGENT_LOOP_PAUSE_team3 instead of a wake, and exits.
param([double]$MaxHours = 4)

$repoRoot = Split-Path $PSScriptRoot -Parent
$target = Join-Path $PSScriptRoot 'team3_response.md'
$promptPath = Join-Path $repoRoot 'maps\vector_ownership\team3_next_prompt.txt'
$tracePath = Join-Path $repoRoot 'maps\vector_ownership\anomaly_begin_store_trace.txt'
# Outside the repo. OpenCode lists every write under the workspace as a
# session change, and a revert of that change used to replace this process id.
$leaseDir = Join-Path $env:LOCALAPPDATA 'vision_3d_skips-team3a'
New-Item -ItemType Directory -Force -Path $leaseDir | Out-Null
$pidFile = Join-Path $leaseDir 'watcher.pid'
$legacyPidFiles = @((Join-Path $PSScriptRoot '.watcher.pid'), (Join-Path $PSScriptRoot 'watch_response.pid'))

function Get-PassId([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    foreach ($line in @(Get-Content -LiteralPath $path -TotalCount 8)) {
        if ($line -match '^Pass id: (\S+)\s*$') { return $Matches[1] }
    }
    return $null
}

# Team 3 may head the reply `Pass id: <id>`, `Pass <id>.`, or `# Pass <id>`.
function Get-ResponsePassId([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    foreach ($line in @(Get-Content -LiteralPath $path -TotalCount 8)) {
        if ($line -match '^\s*(?:#+\s*)?Pass(?:\s+id:)?\s+`?([0-9]{8}T[0-9]{6}Z-[0-9a-f]+)`?') { return $Matches[1] }
    }
    return $null
}

# END lines close a section; they are not evidence.
function Get-TraceLastHeading {
    if (-not (Test-Path -LiteralPath $tracePath)) { return '' }
    $text = [System.IO.File]::ReadAllText($tracePath)
    $found = [regex]::Matches($text, '(?m)^===== (?!END\b)(.+?) =====\s*$')
    if ($found.Count -eq 0) { return '' }
    return $found[$found.Count - 1].Groups[1].Value.Trim()
}

function Get-LeasePid([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $parsed = 0
    $text = $null
    try { $text = Get-Content -LiteralPath $path -TotalCount 1 -ErrorAction Stop } catch { return $null }
    if ([int]::TryParse($text, [ref]$parsed) -and $parsed -gt 0) { return $parsed }
    return $null
}

function Test-WatcherProcess([int]$procId) {
    if ($procId -eq $PID) { return $false }
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$procId" -ErrorAction SilentlyContinue
    return [bool]($proc -and $proc.CommandLine -match 'watch_response')
}

foreach ($oldPid in @(($legacyPidFiles | ForEach-Object { Get-LeasePid $_ }) + (Get-LeasePid $pidFile))) {
    if ($oldPid -and (Test-WatcherProcess $oldPid)) {
        Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
        Write-Output "stopped older watcher pid=$oldPid"
    }
}
foreach ($legacy in $legacyPidFiles) {
    if (Test-Path -LiteralPath $legacy) {
        Start-Sleep -Milliseconds 300
        Remove-Item -LiteralPath $legacy -Force -ErrorAction SilentlyContinue
    }
}
Set-Content -LiteralPath $pidFile -Value $PID

$passId = Get-PassId $promptPath
$baseHeading = Get-TraceLastHeading
$seen = $null
if (Test-Path -LiteralPath $target) {
    $item = Get-Item -LiteralPath $target
    $seen = '{0}|{1}' -f $item.Length, $item.LastWriteTimeUtc.Ticks
}
Write-Output "watching handoff/team3_response.md for pass $passId baseline=$seen heading='$baseHeading'"
$deadline = (Get-Date).AddHours($MaxHours)
try {
    while ((Get-Date) -lt $deadline) {
        $leasePid = Get-LeasePid $pidFile
        if ($leasePid -ne $PID) {
            if ($leasePid -and (Test-WatcherProcess $leasePid)) {
                Write-Output 'superseded by a newer watcher; exiting'
                return
            }
            Set-Content -LiteralPath $pidFile -Value $PID
        }
        if (Test-Path -LiteralPath $target) {
            $item = Get-Item -LiteralPath $target
            $stamp = '{0}|{1}' -f $item.Length, $item.LastWriteTimeUtc.Ticks
            if ($stamp -ne $seen -and $item.Length -gt 0) {
                Start-Sleep -Milliseconds 800
                $item2 = Get-Item -LiteralPath $target
                $stamp2 = '{0}|{1}' -f $item2.Length, $item2.LastWriteTimeUtc.Ticks
                if ($stamp2 -eq $stamp) {
                    $seen = $stamp2
                    $got = Get-ResponsePassId $target
                    if ($passId -and $got -eq $passId) {
                        # The trace append can land a moment after the response write.
                        $heading = Get-TraceLastHeading
                        foreach ($i in 1..10) {
                            if ($heading -ne $baseHeading) { break }
                            Start-Sleep -Seconds 3
                            $heading = Get-TraceLastHeading
                        }
                        if ($heading -eq $baseHeading) {
                            Write-Output "AGENT_LOOP_PAUSE_team3 {`"reason`":`"Team 3 answered pass $passId but the trace still ends at '$baseHeading'. No new evidence. Do not write a prompt, do not commit, and do not rotate. Tell the user.`"}"
                            return
                        }
                        Write-Output "AGENT_LOOP_WAKE_team3 {`"prompt`":`"Team 3 wrote handoff/team3_response.md for pass $passId and the trace heading moved to '$heading'. Follow .cursor/rules/vector-ownership-director.mdc. Read handoff/state.md, maps/vector_ownership/team3_next_prompt.txt, handoff/team3_response.md, and only the last ===== section of the trace before judging. If the section holds and the session is closed, write the next question with a new Pass id, update state, then run handoff/rotate_threads.ps1. Do not do their byte work.`"}"
                        return
                    }
                    Write-Output "ignored write headed '$got' (waiting for pass $passId)"
                }
            }
        }
        Start-Sleep -Seconds 3
    }
    Write-Output "no response for pass $passId within $MaxHours h; exiting"
} finally {
    if ((Get-LeasePid $pidFile) -eq $PID) {
        Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    }
}
