# OpenCode Dev coordinator flow. Opens a new Team 3 session in the stable
# OpenCode window, closes the previous one, and sends a short notice. Then
# opens a new OpenCode Dev session, pastes opencode_bootstrap.md, sends it,
# and closes the OpenCode Dev session tab(s) that were open before, including
# the coordinator that launched this script.
# Requires powershell -STA. The two windows stay where they are.
#
# Both apps are Electron windows titled "OpenCode", so they are told apart by
# exact process name: 'OpenCode' is Team 3, 'OpenCode Dev' is the coordinator.
# A wildcard 'OpenCode*' matches both; never use it here.
#
# Both windows are driven through UI Automation by control name, not by
# fixed pixel offsets. Session tabs are only found when their top edge is
# within 46 logical pixels of the screen top (see prepare_windows.ps1).
#
# This process is per-monitor DPI aware, so UI Automation rects, window
# rects, clicks, and screenshots are all physical pixels.

param(
    [switch]$WorkerOnly,
    [switch]$CoordinatorOnly,
    [switch]$StopBeforeCoordinatorClose,
    [switch]$StopBeforeCoordinatorSend
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class RotateUi {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr hwnd);
  public static void Click(int x, int y) {
    SetCursorPos(x, y);
    System.Threading.Thread.Sleep(80);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
    System.Threading.Thread.Sleep(40);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
  public static void Key(byte vk, bool up) {
    keybd_event(vk, 0, up ? 2u : 0u, UIntPtr.Zero);
  }
  public static void Chord(params byte[] keys) {
    foreach (byte k in keys) { Key(k, false); System.Threading.Thread.Sleep(25); }
    for (int i = keys.Length - 1; i >= 0; i--) { Key(keys[i], true); System.Threading.Thread.Sleep(25); }
  }
  public static void AllowForeground(IntPtr hwnd) {
    Key(0x12, false);
    Key(0x12, true);
    System.Threading.Thread.Sleep(40);
    SetForegroundWindow(hwnd);
    System.Threading.Thread.Sleep(180);
  }
}
"@
[void][RotateUi]::SetProcessDpiAwarenessContext([IntPtr](-4))
[void][RotateUi]::SetThreadDpiAwarenessContext([IntPtr](-4))

$WorkerProcess = 'OpenCode'
$CoordinatorProcess = 'OpenCode Dev'
$repoRoot = Split-Path $PSScriptRoot -Parent
$promptRel = 'maps/vector_ownership/team3_next_prompt.txt'
$MinMinutesBetween = 3

function Get-Scale([IntPtr]$hwnd) {
    $dpi = [RotateUi]::GetDpiForWindow($hwnd)
    if ($dpi -lt 96) { $dpi = 96 }
    return $dpi / 96.0
}

function Set-Clip([string]$text) {
    $ok = $false
    foreach ($try in 1..8) {
        try {
            [System.Windows.Forms.Clipboard]::SetText($text)
            $ok = $true
            break
        } catch {
            Start-Sleep -Milliseconds 150
        }
    }
    if (-not $ok) { throw 'clipboard set failed' }
}

function Get-AppWindow([string]$processName) {
    $proc = Get-Process -Name $processName -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $proc) { throw "$processName window not found" }
    return $proc.MainWindowHandle
}

function Get-UiAll([IntPtr]$hwnd) {
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    return $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
}

function Test-RendererAccessibility([IntPtr]$hwnd, [string]$label) {
    $legacyOnly = $false
    $doc = $false
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            $name = $el.Current.Name
            $type = $el.Current.ControlType.ProgrammaticName
        } catch { continue }
        if ($type -eq 'ControlType.Document') { $doc = $true }
        if ($name -eq 'Chrome Legacy Window') { $legacyOnly = $true }
    }
    if ($doc) { return }
    if ($legacyOnly) {
        throw @"
$label has no Chromium accessibility tree (UI Automation only sees Chrome Legacy Window). Close OpenCode Dev and start it with --force-renderer-accessibility:
  powershell -NoProfile -ExecutionPolicy Bypass -File handoff_oc/start_opencode_dev.ps1
"@
    }
}

function Get-SessionTabs([IntPtr]$hwnd) {
    $maxY = 46 * (Get-Scale $hwnd)
    $closes = @()
    $links = @()
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            $r = $el.Current.BoundingRectangle
            $name = $el.Current.Name
            $type = $el.Current.ControlType.ProgrammaticName
        } catch { continue }
        if ($r.Width -lt 2 -or $r.Y -lt 0 -or $r.Y -gt $maxY) { continue }
        if (-not $name) { continue }
        if ($name -eq 'Close tab' -and $type -eq 'ControlType.Button') {
            $closes += $el
        } elseif ($type -eq 'ControlType.Hyperlink' -and $name -notlike '*Close tab*') {
            $links += $el
        }
    }
    $tabs = @()
    foreach ($link in $links) {
        $hr = $link.Current.BoundingRectangle
        foreach ($c in $closes) {
            $cr = $c.Current.BoundingRectangle
            $mx = $cr.X + $cr.Width / 2
            $my = $cr.Y + $cr.Height / 2
            if ($mx -ge $hr.X -and $mx -le ($hr.X + $hr.Width) -and $my -ge $hr.Y -and $my -le ($hr.Y + $hr.Height)) {
                $tabs += [pscustomobject]@{
                    Name = $link.Current.Name
                    CloseX = [int]$mx
                    CloseY = [int]$my
                    CloseEl = $c
                    LinkId = ($link.GetRuntimeId() -join '.')
                }
                break
            }
        }
    }
    $unique = @()
    $seenClose = @{}
    foreach ($tab in $tabs) {
        $key = '{0},{1}' -f $tab.CloseX, $tab.CloseY
        if ($seenClose.ContainsKey($key)) { continue }
        $seenClose[$key] = $true
        $unique += $tab
    }
    return $unique
}

function Find-Button([IntPtr]$hwnd, [string]$name) {
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            if ($el.Current.Name -eq $name -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Button') { return $el }
        } catch { continue }
    }
    return $null
}

# Invoke by accessibility pattern when the control supports it. A click
# that lands a few pixels off can hit New session and spawn an empty one.
function Invoke-Element($el) {
    $pat = $null
    try { $pat = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern) } catch {}
    if ($pat) { $pat.Invoke(); return }
    $r = $el.Current.BoundingRectangle
    [RotateUi]::Click([int]($r.X + $r.Width / 2), [int]($r.Y + $r.Height / 2))
}

function Find-PromptEdit([IntPtr]$hwnd) {
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            if ($el.Current.Name -eq 'Prompt' -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Edit') { return $el }
        } catch { continue }
    }
    throw 'prompt box not found'
}

function Get-PromptValue([IntPtr]$hwnd) {
    $prompt = Find-PromptEdit $hwnd
    try {
        $vp = $prompt.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        if ($vp) { return [string]$vp.Current.Value }
    } catch {}
    return ''
}

# New session, wait for its tab. Returns the LinkIds of the tabs that were
# open before, so the caller can close exactly those.
function Open-FreshSession([IntPtr]$hwnd, [string]$label) {
    [RotateUi]::AllowForeground($hwnd)
    $beforeTabs = @(Get-SessionTabs $hwnd)
    if ($beforeTabs.Count -lt 1) { throw "no $label session tab to rotate" }
    $before = @($beforeTabs | ForEach-Object { $_.LinkId })
    Write-Host "$label before: $($beforeTabs.Name -join ' | ')"
    $newBtn = Find-Button $hwnd 'New session'
    if (-not $newBtn) { throw "$label New session button not found" }
    Invoke-Element $newBtn
    $fresh = @()
    foreach ($wait in 1..12) {
        Start-Sleep -Milliseconds 300
        $now = @(Get-SessionTabs $hwnd)
        $fresh = @($now | Where-Object { $before -notcontains $_.LinkId })
        if ($fresh.Count -ge 1) { break }
    }
    if ($fresh.Count -lt 1) { throw "new $label session did not appear; old session left open" }
    Write-Host "$label fresh: $($fresh.Name -join ' | ')"
    return , $before
}

function Close-OldSessions([IntPtr]$hwnd, [string]$label, [string[]]$before) {
    foreach ($pass in 1..8) {
        $now = @(Get-SessionTabs $hwnd)
        $old = @($now | Where-Object { $before -contains $_.LinkId } | Sort-Object CloseX -Descending)
        if ($old.Count -lt 1) { break }
        $tab = $old[0]
        "closing old $label session '$($tab.Name)' at $($tab.CloseX),$($tab.CloseY)"
        Invoke-Element $tab.CloseEl
        Start-Sleep -Milliseconds 450
    }
    $left = @(Get-SessionTabs $hwnd)
    $still = @($left | Where-Object { $before -contains $_.LinkId })
    if ($still.Count -gt 0) { throw "old $label session still open: $($still.Name -join ' | ')" }
    if ($left.Count -lt 1) { throw "$label session tab disappeared" }
    "$label remaining: $($left.Name -join ' | ')"
}

# Ctrl+A, Delete, paste. Click the first text line: the card center sits below
# it and does not focus the editor.
function Paste-IntoPrompt([IntPtr]$hwnd, [string]$text) {
    $prompt = Find-PromptEdit $hwnd
    # Tab changes drop keyboard focus. Take it back right before the click.
    [RotateUi]::AllowForeground($hwnd)
    try { $prompt.SetFocus() } catch {}
    $s = Get-Scale $hwnd
    $pr = $prompt.Current.BoundingRectangle
    [RotateUi]::Click([int]($pr.X + 48 * $s), [int]($pr.Y + [Math]::Min($pr.Height / 2, 21 * $s)))
    Start-Sleep -Milliseconds 200
    [RotateUi]::Chord(0x11, 0x41) # Ctrl+A
    Start-Sleep -Milliseconds 60
    [RotateUi]::Key(0x2E, $false); [RotateUi]::Key(0x2E, $true) # Delete
    Start-Sleep -Milliseconds 60
    Set-Clip $text
    Start-Sleep -Milliseconds 60
    [RotateUi]::Chord(0x11, 0x56) # Ctrl+V
    Start-Sleep -Milliseconds 350
}

# Enter, then prove the send by Stop appearing. If Stop does not show, press
# Send once. A prompt that still holds text after that is a failure.
function Send-Prompt([IntPtr]$hwnd, [string]$label) {
    [RotateUi]::Key(0x0D, $false); [RotateUi]::Key(0x0D, $true) # Enter
    foreach ($wait in 1..10) {
        Start-Sleep -Milliseconds 300
        if (Find-Button $hwnd 'Stop') { "$label prompt sent"; return }
    }
    $value = (Get-PromptValue $hwnd).Trim()
    if ($value.Length -gt 0 -and $value -ne '?') {
        $send = Find-Button $hwnd 'Send'
        if (-not $send) { throw "$label prompt still holds text and Send was not found" }
        Invoke-Element $send
        foreach ($wait in 1..10) {
            Start-Sleep -Milliseconds 300
            if (Find-Button $hwnd 'Stop') { "$label prompt sent"; return }
        }
        $value = (Get-PromptValue $hwnd).Trim()
    }
    if ($value.Length -eq 0) { "$label prompt sent (box is empty; Stop not seen)"; return }
    if ($value -eq '?') { throw "$label prompt did not take the text; the empty box reports its value as ?" }
    throw "$label prompt still holds unexpected text: $value"
}

# One rotation at a time, and one rotation per pass id. The mutex name is the
# same as handoff/rotate_threads.ps1, so the Cursor flow and this flow cannot
# rotate at once. Remove a line from handoff_oc/.rotated to re-run it.
$rotateLock = New-Object System.Threading.Mutex($false, 'Local\team3a_rotate_threads')
try { $locked = $rotateLock.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $locked = $true }
if (-not $locked) { 'another rotation is running; not rotating'; exit 1 }

$promptPath = Join-Path $repoRoot $promptRel
$rotatedPath = Join-Path $PSScriptRoot '.rotated'
# The Cursor flow's ledger. Read only: an id rotated by either flow is spent.
$cursorRotatedPath = Join-Path $repoRoot 'handoff\.rotated'
$passId = $null
if (Test-Path -LiteralPath $promptPath) {
    foreach ($line in @(Get-Content -LiteralPath $promptPath -TotalCount 8)) {
        if ($line -match '^Pass id: (\S+)\s*$') {
            $passId = $Matches[1]
            break
        }
    }
}
if (-not $CoordinatorOnly) {
    if (-not $passId) { "$promptRel has no Pass id line; not rotating"; exit 1 }
    foreach ($ledger in @($rotatedPath, $cursorRotatedPath)) {
        if ((Test-Path -LiteralPath $ledger) -and (Get-Content -LiteralPath $ledger -ErrorAction SilentlyContinue) -contains $passId) {
            "pass $passId already rotated (listed in $ledger); not rotating"
            exit 1
        }
    }
    # A held Ghidra lock makes every new session stop at the same place.
    # That is what ran the 6 Oct loop away. Report it; do not delete it.
    $lockDir = Join-Path $repoRoot 'v3d_files_uncomp_copy'
    $locks = @(Get-ChildItem -LiteralPath $lockDir -Filter 'V3D_SKIP.lock*' -Force -ErrorAction SilentlyContinue)
    if ($locks.Count -gt 0) {
        "lock present: $(($locks | ForEach-Object { '{0} ({1} bytes, {2})' -f $_.Name, $_.Length, $_.LastWriteTime }) -join '; '). Not rotating."
        exit 1
    }
    foreach ($ledger in @($rotatedPath, $cursorRotatedPath)) {
        if (Test-Path -LiteralPath $ledger) {
            $age = (Get-Date) - (Get-Item -LiteralPath $ledger).LastWriteTime
            if ($age.TotalMinutes -lt $MinMinutesBetween) {
                "last rotation was $([int]$age.TotalSeconds)s ago ($ledger); wait $MinMinutesBetween minutes between rotations. Not rotating."
                exit 1
            }
        }
    }
    if (Find-Button (Get-AppWindow $WorkerProcess) 'Stop') {
        'OpenCode shows Stop; Team 3 is mid-run. Not rotating.'
        exit 1
    }
    # Both windows must be found before the id is spent or anything is clicked.
    $coordHwnd = Get-AppWindow $CoordinatorProcess
    Test-RendererAccessibility (Get-AppWindow $WorkerProcess) 'OpenCode (Team 3)'
    Test-RendererAccessibility $coordHwnd 'OpenCode Dev (coordinator)'
    Add-Content -LiteralPath $rotatedPath -Value $passId
}

if (-not $CoordinatorOnly) {
    $hwnd = Get-AppWindow $WorkerProcess
    $before = Open-FreshSession $hwnd 'open code'
    Close-OldSessions $hwnd 'open code' $before
    $notice = "Pass $passId. Read $promptRel and answer only pass $passId."
    "open code notice: $notice"
    Paste-IntoPrompt $hwnd $notice
    Send-Prompt $hwnd 'open code'
}

if ($WorkerOnly) { return }

# Coordinator. The old tab is closed last: it is the session running this
# script, and the new one must be sent before it goes.
$dh = Get-AppWindow $CoordinatorProcess
$devBefore = Open-FreshSession $dh 'open code dev'
$boot = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'opencode_bootstrap.md')).Trim()
Paste-IntoPrompt $dh $boot
$pr = (Find-PromptEdit $dh).Current.BoundingRectangle
$shotPath = Join-Path $env:TEMP 'opencode_dev_before_send.png'
$shot = New-Object System.Drawing.Bitmap ([int]$pr.Width), ([int]$pr.Height)
$sg = [System.Drawing.Graphics]::FromImage($shot)
$sg.CopyFromScreen([int]$pr.X, [int]$pr.Y, 0, 0, (New-Object System.Drawing.Size ([int]$pr.Width), ([int]$pr.Height)))
$shot.Save($shotPath, [System.Drawing.Imaging.ImageFormat]::Png)
$sg.Dispose(); $shot.Dispose()
if ($StopBeforeCoordinatorSend) { "open code dev bootstrap pasted, not sent (screenshot $shotPath)"; return }
Send-Prompt $dh 'open code dev'
if ($StopBeforeCoordinatorClose) { return }
Close-OldSessions $dh 'open code dev' $devBefore
