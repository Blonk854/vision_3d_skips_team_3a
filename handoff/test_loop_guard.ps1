# Exercises handoff/loop_guard.ps1 against temp files. Does not arm the loop.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'loop_guard.ps1')

$failures = 0
function Assert-True($cond, [string]$message) {
    if (-not $cond) {
        Write-Output "FAIL $message"
        $script:failures++
    }
}

function New-GuardFixture {
    $root = Join-Path $env:TEMP ('loop-guard-' + [guid]::NewGuid().ToString('n'))
    New-Item -ItemType Directory -Path $root | Out-Null
    $state = Join-Path $root 'state.md'
    $trace = Join-Path $root 'trace.txt'
    $response = Join-Path $root 'response.md'
    $locks = Join-Path $root 'locks'
    $stale = Join-Path $root 'stale'
    New-Item -ItemType Directory -Path $locks | Out-Null
    @'
# fixture

```text
status: running
rotations_total: 0
rotations_this_hour: 0
hour_started_utc:
last_rotation_utc:
last_heading: Completion signal target
identical_stops: 0
last_stop_fingerprint:
last_stop_stamp:
max_rotations: 10
max_per_hour: 10
min_minutes_between: 3
allow_one_resume: no
tracked_open_chats: 1
pause_reason:
```
'@ | Set-Content -LiteralPath $state -Encoding utf8
    @(
        '===== Completion signal target ====='
        '===== END Completion signal target ====='
    ) | Set-Content -LiteralPath $trace -Encoding utf8
    'stopped at 1:00:00 AM' | Set-Content -LiteralPath $response -Encoding utf8
    return [pscustomobject]@{
        Root = $root; State = $state; Trace = $trace; Response = $response; Locks = $locks; Stale = $stale
    }
}

function Invoke-Guard($fx, [hashtable]$extra) {
    $params = @{
        StatePath     = $fx.State
        TracePath     = $fx.Trace
        ResponsePath  = $fx.Response
        LockDirectory = $fx.Locks
        StaleLockRoot = $fx.Stale
        GetHolders    = { @() }
        UtcNow        = [datetime]::SpecifyKind([datetime]'2026-10-06T06:00:00', 'Utc')
    }
    foreach ($key in $extra.Keys) { $params[$key] = $extra[$key] }
    return Test-LoopGuardRotation @params
}

$fx = New-GuardFixture
Update-LoopGuardFields -StatePath $fx.State -Fields @{ status = 'off'; pause_reason = 'off' }
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'stop') 'status off stops'
Assert-True ((Read-LoopGuard -StatePath $fx.State).status -eq 'off') 'status off is not rewritten to running'

$fx = New-GuardFixture
Add-Content -LiteralPath $fx.Trace -Value '===== SetEvent return read =====' -Encoding utf8
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'allow') 'new heading allows'
Assert-True ((Read-LoopGuard -StatePath $fx.State).status -eq 'running') 'allow leaves status running'

$fx = New-GuardFixture
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'pause') 'unchanged heading pauses'
Assert-True ((Read-LoopGuard -StatePath $fx.State).identical_stops -eq '1') 'first stop counts as 1'
Assert-True ((Read-LoopGuard -StatePath $fx.State).status -eq 'paused') 'first stop pauses'
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'stop') 'paused guard does not rotate again'
Assert-True ((Read-LoopGuard -StatePath $fx.State).identical_stops -eq '1') 'same write is not counted twice'

$fx = New-GuardFixture
Invoke-Guard $fx @{} | Out-Null
Update-LoopGuardFields -StatePath $fx.State -Fields @{ status = 'running' }
'stopped at 1:05:00 AM' | Set-Content -LiteralPath $fx.Response -Encoding utf8
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'stop') 'second identical stop stops the loop'
Assert-True ((Read-LoopGuard -StatePath $fx.State).identical_stops -eq '2') 'identical stops reach 2'
Assert-True ((Read-LoopGuard -StatePath $fx.State).status -eq 'stopped') 'second stop sets stopped'

$fx = New-GuardFixture
Update-LoopGuardFields -StatePath $fx.State -Fields @{ rotations_total = '10' }
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'stop') 'round cap stops'
Assert-True ((Read-LoopGuard -StatePath $fx.State).status -eq 'stopped') 'round cap sets stopped'

$fx = New-GuardFixture
Update-LoopGuardFields -StatePath $fx.State -Fields @{ last_rotation_utc = '2026-10-06T05:59:00.0000000Z' }
Add-Content -LiteralPath $fx.Trace -Value '===== SetEvent return read =====' -Encoding utf8
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'wait') 'rate limit waits'
Assert-True ($decision.WaitSeconds -gt 0) 'rate limit reports seconds'
Assert-True ((Read-LoopGuard -StatePath $fx.State).status -eq 'running') 'rate limit does not stop the loop'

$fx = New-GuardFixture
'lock' | Set-Content -LiteralPath (Join-Path $fx.Locks 'V3D_SKIP.lock') -Encoding ascii
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'pause') 'stale lock pauses'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $fx.Locks 'V3D_SKIP.lock'))) 'stale lock is moved'
Assert-True ((Get-ChildItem -LiteralPath $fx.Stale -Recurse -Filter 'V3D_SKIP.lock').Count -eq 1) 'stale lock is kept aside'

$fx = New-GuardFixture
'lock' | Set-Content -LiteralPath (Join-Path $fx.Locks 'V3D_SKIP.lock') -Encoding ascii
$decision = Invoke-Guard $fx @{ GetHolders = { @('999:python.exe') } }
Assert-True ($decision.Result -eq 'stop') 'held lock stops'
Assert-True (Test-Path -LiteralPath (Join-Path $fx.Locks 'V3D_SKIP.lock')) 'held lock is not removed'

$fx = New-GuardFixture
$lockPath = Join-Path $fx.Locks 'V3D_SKIP.lock'
'lock' | Set-Content -LiteralPath $lockPath -Encoding ascii
$held = [System.IO.File]::Open($lockPath, 'Open', 'Read', 'Read')
try {
    $decision = Invoke-Guard $fx @{}
    Assert-True ($decision.Result -eq 'stop') 'os-locked file stops'
    Assert-True (Test-Path -LiteralPath $lockPath) 'os-locked file is not removed'
} finally {
    $held.Dispose()
}

$fx = New-GuardFixture
Update-LoopGuardFields -StatePath $fx.State -Fields @{ tracked_open_chats = '2' }
$decision = Invoke-Guard $fx @{}
Assert-True ($decision.Result -eq 'stop') 'two tracked chats stop'

$fx = New-GuardFixture
Invoke-Guard $fx @{} | Out-Null
Update-LoopGuardFields -StatePath $fx.State -Fields @{ status = 'running'; allow_one_resume = 'yes' }
$decision = Invoke-Guard $fx @{ ForRotate = $true }
Assert-True ($decision.Result -eq 'allow') 'human resume allows one rotation'
Assert-True ((Read-LoopGuard -StatePath $fx.State).identical_stops -eq '1') 'resume does not count the same write again'

$fx = New-GuardFixture
Add-Content -LiteralPath $fx.Trace -Value '===== SetEvent return read =====' -Encoding utf8
$now = [datetime]::SpecifyKind([datetime]'2026-10-06T06:00:00', 'Utc')
Register-LoopRotation -StatePath $fx.State -TracePath $fx.Trace -UtcNow $now
$after = Read-LoopGuard -StatePath $fx.State
Assert-True ($after.rotations_total -eq '1') 'register counts a rotation'
Assert-True ($after.last_heading -eq 'SetEvent return read') 'register stores the new heading'
Assert-True ($after.identical_stops -eq '0') 'progress clears the stop streak'
Assert-True ($after.allow_one_resume -eq 'no') 'register clears the resume flag'

if ($failures -gt 0) {
    Write-Output "$failures failed"
    exit 1
}
Write-Output 'loop guard tests passed'
