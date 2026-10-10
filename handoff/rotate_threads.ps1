# Opens a new OpenCode session, closes the previous one, and sends a short
# notice. Then opens a new Cursor agent, pastes cursor_bootstrap.md, and
# closes the Cursor chat that launched this script.
# Requires powershell -STA. The two windows stay where they are.
#
# This process is per-monitor DPI aware, so UI Automation rects, window
# rects, clicks, and screenshots are all physical pixels. The Cursor offsets
# below are logical (100%) pixels and are scaled by the window's DPI. This
# laptop runs at 125%, so an unaware process would click 1.25x off target.

param(
    [switch]$OpenCodeOnly,
    [switch]$CursorOnly,
    [switch]$StopBeforeCursorClose,
    [switch]$StopBeforeCursorSend
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
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr hwnd);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
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

$CursorTitle = '*vision_3d_skips - team 3a*'
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

function Get-OpenCodeProcess {
    $proc = Get-Process | Where-Object { $_.ProcessName -like 'OpenCode*' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $proc) { throw 'OpenCode window not found' }
    return $proc
}

function Get-OpenCodeSessionTabs([IntPtr]$hwnd) {
    $maxY = 46 * (Get-Scale $hwnd)
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    $closes = @()
    $links = @()
    foreach ($el in $all) {
        $r = $el.Current.BoundingRectangle
        if ($r.Width -lt 2 -or $r.Y -lt 0 -or $r.Y -gt $maxY) { continue }
        $name = $el.Current.Name
        if (-not $name) { continue }
        if ($name -eq 'Close tab' -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Button') {
            $closes += $el
        } elseif ($el.Current.ControlType.ProgrammaticName -eq 'ControlType.Hyperlink' -and $name -notlike '*Close tab*') {
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

function Find-OpenCodeButton([IntPtr]$hwnd, [string]$name) {
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all) {
        if ($el.Current.Name -eq $name -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Button') {
            return $el
        }
    }
    return $null
}

# Invoke by accessibility pattern when the control supports it. A click
# that lands a few pixels off can hit New session and spawn an empty one.
function Invoke-OpenCodeElement($el) {
    $pat = $null
    try { $pat = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern) } catch {}
    if ($pat) { $pat.Invoke(); return }
    $r = $el.Current.BoundingRectangle
    [RotateUi]::Click([int]($r.X + $r.Width / 2), [int]($r.Y + $r.Height / 2))
}

function Find-PromptEdit([IntPtr]$hwnd) {
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all) {
        if ($el.Current.Name -eq 'Prompt' -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Edit') {
            return $el
        }
    }
    throw 'OpenCode prompt box not found'
}

# One rotation at a time, and one rotation per pass id. The mutex is freed
# when this process exits. Remove a line from handoff/.rotated to re-run it.
$rotateLock = New-Object System.Threading.Mutex($false, 'Local\team3a_rotate_threads')
try { $locked = $rotateLock.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $locked = $true }
if (-not $locked) { 'another rotation is running; not rotating'; exit 1 }

$promptPath = Join-Path $repoRoot $promptRel
$rotatedPath = Join-Path $PSScriptRoot '.rotated'
$passId = $null
if (Test-Path -LiteralPath $promptPath) {
    foreach ($line in @(Get-Content -LiteralPath $promptPath -TotalCount 8)) {
        if ($line -match '^Pass id: (\S+)\s*$') {
            $passId = $Matches[1]
            break
        }
    }
}
if (-not $CursorOnly) {
    if (-not $passId) { "$promptRel has no Pass id line; not rotating"; exit 1 }
    if ((Test-Path -LiteralPath $rotatedPath) -and (Get-Content -LiteralPath $rotatedPath -ErrorAction SilentlyContinue) -contains $passId) {
        "pass $passId already rotated; not rotating"
        exit 1
    }
    # A held Ghidra lock makes every new session stop at the same place.
    # That is what ran the 6 Oct loop away. Report it; do not delete it.
    $lockDir = Join-Path $repoRoot 'v3d_files_uncomp_copy'
    $locks = @(Get-ChildItem -LiteralPath $lockDir -Filter 'V3D_SKIP.lock*' -Force -ErrorAction SilentlyContinue)
    if ($locks.Count -gt 0) {
        "lock present: $(($locks | ForEach-Object { '{0} ({1} bytes, {2})' -f $_.Name, $_.Length, $_.LastWriteTime }) -join '; '). Not rotating."
        exit 1
    }
    if (Test-Path -LiteralPath $rotatedPath) {
        $age = (Get-Date) - (Get-Item -LiteralPath $rotatedPath).LastWriteTime
        if ($age.TotalMinutes -lt $MinMinutesBetween) {
            "last rotation was $([int]$age.TotalSeconds)s ago; wait $MinMinutesBetween minutes between rotations. Not rotating."
            exit 1
        }
    }
    if (Find-OpenCodeButton (Get-OpenCodeProcess).MainWindowHandle 'Stop') {
        'OpenCode shows Stop; Team 3 is mid-run. Not rotating.'
        exit 1
    }
    Add-Content -LiteralPath $rotatedPath -Value $passId
}

if (-not $CursorOnly) {
    $oc = Get-OpenCodeProcess
    $hwnd = $oc.MainWindowHandle
    [RotateUi]::AllowForeground($hwnd)
    $beforeTabs = @(Get-OpenCodeSessionTabs $hwnd)
    if ($beforeTabs.Count -lt 1) { throw 'no OpenCode session tab to rotate' }
    $before = @($beforeTabs | ForEach-Object { $_.LinkId })
    "open code before: $($beforeTabs.Name -join ' | ')"
    $newBtn = Find-OpenCodeButton $hwnd 'New session'
    if (-not $newBtn) { throw 'New session button not found' }
    Invoke-OpenCodeElement $newBtn
    $fresh = @()
    foreach ($wait in 1..12) {
        Start-Sleep -Milliseconds 300
        $now = @(Get-OpenCodeSessionTabs $hwnd)
        $fresh = @($now | Where-Object { $before -notcontains $_.LinkId })
        if ($fresh.Count -ge 1) { break }
    }
    if ($fresh.Count -lt 1) { throw 'new OpenCode session did not appear; old session left open' }
    "open code fresh: $($fresh.Name -join ' | ')"
    foreach ($pass in 1..8) {
        $now = @(Get-OpenCodeSessionTabs $hwnd)
        $old = @($now | Where-Object { $before -contains $_.LinkId } | Sort-Object CloseX -Descending)
        if ($old.Count -lt 1) { break }
        $tab = $old[0]
        "closing old session '$($tab.Name)' at $($tab.CloseX),$($tab.CloseY)"
        Invoke-OpenCodeElement $tab.CloseEl
        Start-Sleep -Milliseconds 450
    }
    $left = @(Get-OpenCodeSessionTabs $hwnd)
    $still = @($left | Where-Object { $before -contains $_.LinkId })
    if ($still.Count -gt 0) { throw "old OpenCode session still open: $($still.Name -join ' | ')" }
    if ($left.Count -lt 1) { throw 'OpenCode session tab disappeared' }
    "open code remaining: $($left.Name -join ' | ')"

    $notice = "Pass $passId. Read $promptRel and answer only pass $passId."
    "open code notice: $notice"
    $prompt = Find-PromptEdit $hwnd
    # Tab changes drop keyboard focus. Take it back right before the click.
    [RotateUi]::AllowForeground($hwnd)
    try { $prompt.SetFocus() } catch {}
    # Click the first text line. The card center sits below it and does not focus the editor.
    $s = Get-Scale $hwnd
    $pr = $prompt.Current.BoundingRectangle
    [RotateUi]::Click([int]($pr.X + 48 * $s), [int]($pr.Y + [Math]::Min($pr.Height / 2, 21 * $s)))
    Start-Sleep -Milliseconds 200
    [RotateUi]::Chord(0x11, 0x41) # Ctrl+A
    Start-Sleep -Milliseconds 60
    [RotateUi]::Key(0x2E, $false); [RotateUi]::Key(0x2E, $true) # Delete
    Start-Sleep -Milliseconds 60
    Set-Clip $notice
    Start-Sleep -Milliseconds 60
    [RotateUi]::Chord(0x11, 0x56) # Ctrl+V
    Start-Sleep -Milliseconds 250
    [RotateUi]::Key(0x0D, $false); [RotateUi]::Key(0x0D, $true) # Enter
    Start-Sleep -Milliseconds 500
    $stop = Find-OpenCodeButton $hwnd 'Stop'
    if ($stop) {
        'open code notice sent'
    } else {
        $prompt = Find-PromptEdit $hwnd
        $value = ''
        try {
            $vp = $prompt.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($vp) { $value = [string]$vp.Current.Value }
        } catch {}
        if ($value.Trim() -eq $notice) {
            $send = Find-OpenCodeButton $hwnd 'Send'
            if (-not $send) { throw 'notice still in the prompt box and Send was not found' }
            Invoke-OpenCodeElement $send
            Start-Sleep -Milliseconds 400
            'open code notice sent'
        } elseif ($value.Trim().Length -eq 0) {
            'open code notice sent'
        } elseif ($value.Trim() -eq '?') {
            throw 'OpenCode prompt did not take the notice; the empty box reports its value as ?'
        } else {
            throw "OpenCode prompt still holds unexpected text: $value"
        }
    }
}

if ($OpenCodeOnly) { return }

$cursor = Get-Process | Where-Object { $_.ProcessName -eq 'Cursor' -and $_.MainWindowTitle -like $CursorTitle } | Select-Object -First 1
if (-not $cursor) { throw 'Cursor window not found' }
$ch = $cursor.MainWindowHandle
$wr = New-Object RotateUi+RECT
[RotateUi]::GetWindowRect($ch, [ref]$wr) | Out-Null
$s = Get-Scale $ch
function At([int]$dx, [int]$dy) { [RotateUi]::Click([int]($wr.Left + $dx * $s), [int]($wr.Top + $dy * $s)) }
[RotateUi]::AllowForeground($ch)
# Empty sidebar, above the New Agent label, so the shortcut is not swallowed by the composer.
At 30 180
Start-Sleep -Milliseconds 180
[RotateUi]::Chord(0x11, 0x10, 0x4C) # Ctrl+Shift+L, New Agent
Start-Sleep -Milliseconds 700
# Fresh agent composer sits under the tab row. Window-relative, so the window can sit on either monitor.
At 420 115
Start-Sleep -Milliseconds 200
$bootPath = Join-Path $PSScriptRoot 'cursor_bootstrap.md'
$boot = [System.IO.File]::ReadAllText($bootPath).Trim()
Set-Clip $boot
Start-Sleep -Milliseconds 80
[RotateUi]::Chord(0x11, 0x41)
Start-Sleep -Milliseconds 40
[RotateUi]::Chord(0x11, 0x56)
Start-Sleep -Milliseconds 350
$shotW = [int](700 * $s); $shotH = [int](220 * $s)
$shot = New-Object System.Drawing.Bitmap $shotW, $shotH
$sg = [System.Drawing.Graphics]::FromImage($shot)
$sg.CopyFromScreen([int]($wr.Left + 200 * $s), [int]($wr.Top + 70 * $s), 0, 0, (New-Object System.Drawing.Size $shotW, $shotH))
$shot.Save((Join-Path $env:TEMP 'cursor_before_send.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$sg.Dispose(); $shot.Dispose()
if ($StopBeforeCursorSend) { 'cursor bootstrap pasted, not sent'; return }
[RotateUi]::Chord(0x11, 0x0D) # Ctrl+Enter, force send
Start-Sleep -Milliseconds 500
'cursor bootstrap sent'
if ($StopBeforeCursorClose) { return }
# Ctrl+[ does not switch chats in this Agents window. The new agent opens to
# the right, so the chat that launched the script is the left tab.
At 249 58
Start-Sleep -Milliseconds 300
[RotateUi]::Chord(0x11, 0x57) # Ctrl+W
Start-Sleep -Milliseconds 400
[RotateUi]::Key(0x0D, $false) # Enter confirms "Close Running Tab?"
[RotateUi]::Key(0x0D, $true)
'cursor previous chat closed'
