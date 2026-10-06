# Bookkeeping for the Team 3 handoff. Dot-source this file.
# Running it directly prints the guard and does not start the loop.

$script:LoopGuardKeys = @(
    'status',
    'rotations_total',
    'rotations_this_hour',
    'hour_started_utc',
    'last_rotation_utc',
    'last_heading',
    'identical_stops',
    'last_stop_fingerprint',
    'last_stop_stamp',
    'max_rotations',
    'max_per_hour',
    'min_minutes_between',
    'allow_one_resume',
    'tracked_open_chats',
    'pause_reason'
)

function Get-LoopGuardPaths {
    $repo = Split-Path $PSScriptRoot -Parent
    return [pscustomobject]@{
        State    = Join-Path $PSScriptRoot 'state.md'
        Trace    = Join-Path $repo 'maps\vector_ownership\anomaly_begin_store_trace.txt'
        Response = Join-Path $PSScriptRoot 'team3_response.md'
        Locks    = Join-Path $repo 'v3d_files_uncomp_copy'
        Stale    = Join-Path $PSScriptRoot 'stale_locks'
        Alert    = Join-Path $PSScriptRoot 'LOOP_ALERT.txt'
        Pid      = Join-Path $PSScriptRoot 'watch_response.pid'
    }
}

function ConvertTo-GuardInt([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return 0 }
    return [int]$Value
}

function ConvertTo-GuardUtc([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    $parsed = [datetime]::Parse(
        $Text,
        [cultureinfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::RoundtripKind)
    return $parsed.ToUniversalTime()
}

function Read-LoopGuard {
    param([string]$StatePath = (Get-LoopGuardPaths).State)
    $raw = [System.IO.File]::ReadAllText($StatePath)
    $start = $raw.IndexOf('```text')
    if ($start -lt 0) { throw "loop guard block missing in $StatePath" }
    $nl = $raw.IndexOf("`n", $start)
    $end = $raw.IndexOf('```', $nl + 1)
    if ($end -lt 0) { throw "loop guard block has no closing fence in $StatePath" }
    $body = $raw.Substring($nl + 1, $end - ($nl + 1))
    $map = @{}
    foreach ($key in $script:LoopGuardKeys) { $map[$key] = '' }
    foreach ($line in ($body -split '\r?\n')) {
        if ($line -match '^([A-Za-z0-9_]+):\s*(.*)$') {
            $map[$Matches[1]] = $Matches[2]
        }
    }
    return $map
}

function Update-LoopGuardFields {
    param(
        [hashtable]$Fields,
        [string]$StatePath = (Get-LoopGuardPaths).State
    )
    $raw = [System.IO.File]::ReadAllText($StatePath)
    $start = $raw.IndexOf('```text')
    if ($start -lt 0) { throw "loop guard block missing in $StatePath" }
    $nl = $raw.IndexOf("`n", $start)
    $end = $raw.IndexOf('```', $nl + 1)
    if ($end -lt 0) { throw "loop guard block has no closing fence in $StatePath" }
    $body = $raw.Substring($nl + 1, $end - ($nl + 1))
    $map = @{}
    foreach ($key in $script:LoopGuardKeys) { $map[$key] = '' }
    foreach ($line in ($body -split '\r?\n')) {
        if ($line -match '^([A-Za-z0-9_]+):\s*(.*)$') {
            $map[$Matches[1]] = $Matches[2]
        }
    }
    foreach ($key in @($Fields.Keys)) {
        $map[$key] = [string]$Fields[$key]
    }
    $lines = foreach ($key in $script:LoopGuardKeys) {
        '{0}: {1}' -f $key, $map[$key]
    }
    $newBody = ($lines -join "`n") + "`n"
    $updated = $raw.Substring(0, $nl + 1) + $newBody + $raw.Substring($end)
    [System.IO.File]::WriteAllText($StatePath, $updated)
}

function Get-TraceLastHeading {
    param([string]$TracePath)
    if (-not (Test-Path -LiteralPath $TracePath)) { return '' }
    $text = [System.IO.File]::ReadAllText($TracePath)
    $found = [regex]::Matches($text, '(?m)^===== (?!END\b)(.+?) =====\s*$')
    if ($found.Count -eq 0) { return '' }
    return $found[$found.Count - 1].Groups[1].Value.Trim()
}

function Get-StopFingerprint {
    param([string]$Heading, [string]$Text)
    $norm = [string]$Text
    $norm = [regex]::Replace($norm, '\d{4}-\d{2}-\d{2}', '')
    $norm = [regex]::Replace($norm, '\d{1,2}:\d{2}(:\d{2})?\s*[AP]M', '', 'IgnoreCase')
    $norm = [regex]::Replace($norm, '\s+', ' ').Trim().ToLowerInvariant()
    $payload = ([string]$Heading).ToLowerInvariant() + '|' + $norm
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($payload))
    } finally {
        $sha.Dispose()
    }
    return ([BitConverter]::ToString($hash)).Replace('-', '').Substring(0, 16)
}

function Get-GhidraLockHolders {
    $procs = @(Get-CimInstance Win32_Process | Where-Object {
            $_.Name -match '^(java|javaw)(\.exe)?$' -or
            $_.Name -match '^(python|pythonw|py)(\.exe)?$' -or
            $_.Name -match 'ghidra|analyzeHeadless'
        })
    $hits = @()
    foreach ($proc in $procs) {
        $cmd = [string]$proc.CommandLine
        $name = [string]$proc.Name
        if ($name -match 'ghidra|analyzeHeadless' -or $cmd -match 'ghidra_headless_mcp|pyghidra|analyzeHeadless|ghidra\.Ghidra') {
            $hits += '{0}:{1}' -f $proc.ProcessId, $name
        }
    }
    return @($hits)
}

function Test-OsFileLocked {
    param([string]$Path)
    $stream = $null
    try {
        $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'None')
        return $false
    } catch {
        return $true
    } finally {
        if ($stream) { $stream.Dispose() }
    }
}

function Write-LoopAlert {
    param(
        [string]$Reason,
        [string]$AlertPath = (Get-LoopGuardPaths).Alert
    )
    $dir = Split-Path $AlertPath -Parent
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
    $text = "{0}`r`n{1}`r`n" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Reason
    [System.IO.File]::WriteAllText($AlertPath, $text)
    Write-Output "AGENT_LOOP_PAUSE_team3 $Reason"
    try {
        $shell = New-Object -ComObject WScript.Shell
        $null = $shell.Popup($Reason, 20, 'Team 3 handoff stopped', 48)
    } catch {
    }
}

function Enter-WatcherSingleton {
    param([string]$PidPath = (Get-LoopGuardPaths).Pid)
    try {
        $stream = [System.IO.File]::Open(
            $PidPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None)
    } catch {
        return [pscustomobject]@{ Acquired = $false; Stream = $null }
    }
    $stream.SetLength(0)
    $bytes = [Text.Encoding]::ASCII.GetBytes("$PID")
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Flush()
    $script:WatcherLockStream = $stream
    return [pscustomobject]@{ Acquired = $true; Stream = $stream }
}

function Exit-WatcherSingleton {
    param($Holder, [string]$PidPath = (Get-LoopGuardPaths).Pid)
    if (-not $Holder -or -not $Holder.Acquired) { return }
    if ($Holder.Stream) { $Holder.Stream.Dispose() }
    $script:WatcherLockStream = $null
    if (Test-Path -LiteralPath $PidPath) {
        Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
    }
}

function Test-LoopGuardRotation {
    param(
        [string]$StatePath = (Get-LoopGuardPaths).State,
        [string]$TracePath = (Get-LoopGuardPaths).Trace,
        [string]$ResponsePath = (Get-LoopGuardPaths).Response,
        [string]$LockDirectory = (Get-LoopGuardPaths).Locks,
        [string]$StaleLockRoot = (Get-LoopGuardPaths).Stale,
        [scriptblock]$GetHolders = { Get-GhidraLockHolders },
        [datetime]$UtcNow = [datetime]::UtcNow,
        [switch]$ForRotate,
        [switch]$Alert
    )

    $state = Read-LoopGuard -StatePath $StatePath
    $reason = [string]$state.pause_reason

    if ($state.status -ne 'running') {
        if (-not $reason) { $reason = "loop guard status is $($state.status)" }
        return [pscustomobject]@{ Result = 'stop'; Reason = $reason; WaitSeconds = 0 }
    }

    if ((ConvertTo-GuardInt $state.tracked_open_chats) -ge 2) {
        $reason = 'tracked_open_chats is already 2. Close the extra Cursor chat, then set tracked_open_chats to 1.'
        Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'stopped'; pause_reason = $reason }
        if ($Alert) { Write-LoopAlert -Reason $reason }
        return [pscustomobject]@{ Result = 'stop'; Reason = $reason; WaitSeconds = 0 }
    }

    $locks = @()
    if (Test-Path -LiteralPath $LockDirectory) {
        $locks = @(Get-ChildItem -LiteralPath $LockDirectory -Filter 'V3D_SKIP.lock*' -Force -ErrorAction SilentlyContinue)
    }
    if ($locks.Count -gt 0) {
        $holders = @(& $GetHolders)
        $osLocked = $false
        foreach ($lock in $locks) {
            if (Test-OsFileLocked -Path $lock.FullName) { $osLocked = $true }
        }
        if ($holders.Count -gt 0 -or $osLocked) {
            $who = if ($holders.Count -gt 0) { $holders -join ', ' } else { 'an unknown process has the file open' }
            $reason = "V3D_SKIP.lock is held ($who). Not rotating. Close that process before continuing."
            Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'stopped'; pause_reason = $reason }
            if ($Alert) { Write-LoopAlert -Reason $reason }
            return [pscustomobject]@{ Result = 'stop'; Reason = $reason; WaitSeconds = 0 }
        }
        if (-not (Test-Path -LiteralPath $StaleLockRoot)) {
            New-Item -ItemType Directory -Path $StaleLockRoot | Out-Null
        }
        $dest = Join-Path $StaleLockRoot (Get-Date -Format 'yyyyMMdd-HHmmss')
        New-Item -ItemType Directory -Path $dest | Out-Null
        foreach ($lock in $locks) {
            Move-Item -LiteralPath $lock.FullName -Destination (Join-Path $dest $lock.Name)
        }
        $reason = "Moved stale V3D_SKIP.lock files to $dest. Not rotating. Set status to running and allow_one_resume to yes to send the same question once."
        Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'paused'; pause_reason = $reason }
        if ($Alert) { Write-LoopAlert -Reason $reason }
        return [pscustomobject]@{ Result = 'pause'; Reason = $reason; WaitSeconds = 0 }
    }

    $total = ConvertTo-GuardInt $state.rotations_total
    $maxTotal = ConvertTo-GuardInt $state.max_rotations
    if ($maxTotal -lt 1) { $maxTotal = 10 }
    if ($total -ge $maxTotal) {
        $reason = "Round cap reached ($total of $maxTotal). A human must raise max_rotations or reset rotations_total, then set status to running."
        Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'stopped'; pause_reason = $reason }
        if ($Alert) { Write-LoopAlert -Reason $reason }
        return [pscustomobject]@{ Result = 'stop'; Reason = $reason; WaitSeconds = 0 }
    }

    $hourCount = ConvertTo-GuardInt $state.rotations_this_hour
    $hourStart = ConvertTo-GuardUtc $state.hour_started_utc
    if ($hourStart -and ($UtcNow - $hourStart).TotalHours -ge 1) { $hourCount = 0 }
    $maxHour = ConvertTo-GuardInt $state.max_per_hour
    if ($maxHour -lt 1) { $maxHour = 10 }
    if ($hourCount -ge $maxHour) {
        $reason = "Hour cap reached ($hourCount of $maxHour). A human must wait or raise max_per_hour, then set status to running."
        Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'stopped'; pause_reason = $reason }
        if ($Alert) { Write-LoopAlert -Reason $reason }
        return [pscustomobject]@{ Result = 'stop'; Reason = $reason; WaitSeconds = 0 }
    }

    $minMinutes = ConvertTo-GuardInt $state.min_minutes_between
    if ($minMinutes -lt 1) { $minMinutes = 3 }
    $lastRotation = ConvertTo-GuardUtc $state.last_rotation_utc
    if ($lastRotation) {
        $elapsed = ($UtcNow - $lastRotation).TotalMinutes
        if ($elapsed -lt $minMinutes) {
            $wait = [int][Math]::Ceiling(($minMinutes - $elapsed) * 60)
            $reason = "Rate limit: $wait seconds left before the next rotation."
            return [pscustomobject]@{ Result = 'wait'; Reason = $reason; WaitSeconds = $wait }
        }
    }

    $heading = Get-TraceLastHeading -TracePath $TracePath
    if ([string]::IsNullOrWhiteSpace($state.last_heading)) {
        $reason = "Recorded heading '$heading' as the baseline. Not rotating."
        Update-LoopGuardFields -StatePath $StatePath -Fields @{ last_heading = $heading; pause_reason = $reason }
        if ($Alert) { Write-LoopAlert -Reason $reason }
        return [pscustomobject]@{ Result = 'pause'; Reason = $reason; WaitSeconds = 0 }
    }

    if ($heading -ne $state.last_heading) {
        return [pscustomobject]@{ Result = 'allow'; Reason = "new heading: $heading"; WaitSeconds = 0 }
    }

    $responseText = ''
    if (Test-Path -LiteralPath $ResponsePath) {
        $responseText = [System.IO.File]::ReadAllText($ResponsePath)
    }
    $fingerprint = Get-StopFingerprint -Heading $heading -Text $responseText
    $stamp = ''
    if (Test-Path -LiteralPath $ResponsePath) {
        $responseItem = Get-Item -LiteralPath $ResponsePath
        $stamp = '{0}|{1}' -f $responseItem.Length, $responseItem.LastWriteTimeUtc.Ticks
    }
    $stops = ConvertTo-GuardInt $state.identical_stops
    $sameWrite = ($stamp -ne '' -and $stamp -eq $state.last_stop_stamp -and $fingerprint -eq $state.last_stop_fingerprint)
    if (-not $sameWrite) {
        $stops += 1
        Update-LoopGuardFields -StatePath $StatePath -Fields @{
            identical_stops       = "$stops"
            last_stop_fingerprint = $fingerprint
            last_stop_stamp       = $stamp
        }
        $state = Read-LoopGuard -StatePath $StatePath
    }

    if ($stops -ge 2) {
        $reason = 'Two identical stop replies in a row. Loop stopped. Set identical_stops to 0 before continuing.'
        Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'stopped'; pause_reason = $reason }
        if ($Alert) { Write-LoopAlert -Reason $reason }
        return [pscustomobject]@{ Result = 'stop'; Reason = $reason; WaitSeconds = 0 }
    }

    if ($ForRotate -and $state.allow_one_resume -eq 'yes') {
        return [pscustomobject]@{ Result = 'allow'; Reason = 'human allowed one resume of the same question'; WaitSeconds = 0 }
    }

    $reason = "No new trace heading ('$heading'). Not writing a prompt and not rotating. Set status to running and allow_one_resume to yes to send the same question once."
    Update-LoopGuardFields -StatePath $StatePath -Fields @{ status = 'paused'; pause_reason = $reason }
    if ($Alert) { Write-LoopAlert -Reason $reason }
    return [pscustomobject]@{ Result = 'pause'; Reason = $reason; WaitSeconds = 0 }
}

function Register-LoopRotation {
    param(
        [string]$StatePath = (Get-LoopGuardPaths).State,
        [string]$TracePath = (Get-LoopGuardPaths).Trace,
        [datetime]$UtcNow = [datetime]::UtcNow
    )
    $state = Read-LoopGuard -StatePath $StatePath
    $heading = Get-TraceLastHeading -TracePath $TracePath
    $hourCount = ConvertTo-GuardInt $state.rotations_this_hour
    $hourStart = ConvertTo-GuardUtc $state.hour_started_utc
    $hourText = [string]$state.hour_started_utc
    if (-not $hourStart -or ($UtcNow - $hourStart).TotalHours -ge 1) {
        $hourCount = 0
        $hourText = $UtcNow.ToString('o')
    }
    $stops = ConvertTo-GuardInt $state.identical_stops
    $fingerprint = [string]$state.last_stop_fingerprint
    $stopStamp = [string]$state.last_stop_stamp
    if ($heading -and $heading -ne $state.last_heading) {
        $stops = 0
        $fingerprint = ''
        $stopStamp = ''
    }
    Update-LoopGuardFields -StatePath $StatePath -Fields @{
        rotations_total        = "$((ConvertTo-GuardInt $state.rotations_total) + 1)"
        rotations_this_hour    = "$($hourCount + 1)"
        hour_started_utc       = $hourText
        last_rotation_utc      = $UtcNow.ToString('o')
        last_heading           = $heading
        identical_stops        = "$stops"
        last_stop_fingerprint  = $fingerprint
        last_stop_stamp        = $stopStamp
        allow_one_resume       = 'no'
        tracked_open_chats     = '1'
        pause_reason           = ''
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    $shown = Read-LoopGuard
    Write-Output 'loop guard (this command does not start the loop)'
    foreach ($key in $script:LoopGuardKeys) {
        Write-Output ("{0}: {1}" -f $key, $shown[$key])
    }
}
