# Opens a new OpenCode session, closes the previous one, and sends a short
# notice. Then opens a new Cursor agent, pastes cursor_bootstrap.md, and
# closes the Cursor chat that launched this script.
# Requires powershell -STA. The two windows stay where they are.

param(
    [switch]$OpenCodeOnly,
    [switch]$CursorOnly,
    [switch]$StopBeforeCursorClose,
    [switch]$StopBeforeCursorSend
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class RotateUi {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
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
    $proc = Get-Process | Where-Object { $_.ProcessName -eq 'OpenCode' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $proc) { throw 'OpenCode window not found' }
    return $proc
}

function Get-OpenCodeSessionTabs([IntPtr]$hwnd) {
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    $closes = @()
    $links = @()
    foreach ($el in $all) {
        $r = $el.Current.BoundingRectangle
        if ($r.Width -lt 2 -or $r.Y -lt 0 -or $r.Y -gt 46) { continue }
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
                }
                break
            }
        }
    }
    return $tabs
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

if (-not $CursorOnly) {
    $oc = Get-OpenCodeProcess
    $hwnd = $oc.MainWindowHandle
    [RotateUi]::AllowForeground($hwnd)
    $before = @(Get-OpenCodeSessionTabs $hwnd | ForEach-Object { $_.Name })
    if ($before.Count -lt 1) { throw 'no OpenCode session tab to rotate' }
    "open code before: $($before -join ' | ')"
    $newBtn = Find-OpenCodeButton $hwnd 'New session'
    if (-not $newBtn) { throw 'New session button not found' }
    $nr = $newBtn.Current.BoundingRectangle
    [RotateUi]::Click([int]($nr.X + $nr.Width / 2), [int]($nr.Y + $nr.Height / 2))
    $fresh = @()
    foreach ($wait in 1..12) {
        Start-Sleep -Milliseconds 300
        $now = @(Get-OpenCodeSessionTabs $hwnd)
        $fresh = @($now | Where-Object { $before -notcontains $_.Name })
        if ($fresh.Count -ge 1) { break }
    }
    if ($fresh.Count -lt 1) { throw 'new OpenCode session did not appear; old session left open' }
    "open code fresh: $($fresh.Name -join ' | ')"
    $now = @(Get-OpenCodeSessionTabs $hwnd)
    foreach ($tab in $now) {
        if ($before -contains $tab.Name) {
            "closing old session '$($tab.Name)' at $($tab.CloseX),$($tab.CloseY)"
            [RotateUi]::Click($tab.CloseX, $tab.CloseY)
            Start-Sleep -Milliseconds 450
        }
    }
    $left = @(Get-OpenCodeSessionTabs $hwnd)
    $still = @($left | Where-Object { $before -contains $_.Name })
    if ($still.Count -gt 0) { throw "old OpenCode session still open: $($still.Name -join ' | ')" }
    if ($left.Count -lt 1) { throw 'OpenCode session tab disappeared' }
    "open code remaining: $($left.Name -join ' | ')"

    $notice = 'Continue from maps/vector_ownership/team3_next_prompt.txt'
    $prompt = Find-PromptEdit $hwnd
    $pr = $prompt.Current.BoundingRectangle
    [RotateUi]::Click([int]($pr.X + 48), [int]($pr.Y + $pr.Height / 2))
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
            $sr = $send.Current.BoundingRectangle
            [RotateUi]::Click([int]($sr.X + $sr.Width / 2), [int]($sr.Y + $sr.Height / 2))
            Start-Sleep -Milliseconds 400
            'open code notice sent'
        } elseif ($value.Trim().Length -eq 0) {
            'open code notice sent'
        } else {
            throw "OpenCode prompt still holds unexpected text: $value"
        }
    }
}

if ($OpenCodeOnly) { return }

$cursor = Get-Process | Where-Object { $_.ProcessName -eq 'Cursor' -and $_.MainWindowTitle -like '*vision_3d_skips*' } | Select-Object -First 1
if (-not $cursor) { throw 'Cursor window not found' }
$ch = $cursor.MainWindowHandle
$wr = New-Object RotateUi+RECT
[RotateUi]::GetWindowRect($ch, [ref]$wr) | Out-Null
[RotateUi]::AllowForeground($ch)
# Empty sidebar, above the New Agent label, so the shortcut is not swallowed by the composer.
[RotateUi]::Click(($wr.Left + 30), ($wr.Top + 180))
Start-Sleep -Milliseconds 180
[RotateUi]::Chord(0x11, 0x10, 0x4C) # Ctrl+Shift+L, New Agent
Start-Sleep -Milliseconds 700
# Fresh agent composer sits under the tab row. Window-relative, so the window can sit on either monitor.
[RotateUi]::Click(($wr.Left + 420), ($wr.Top + 115))
Start-Sleep -Milliseconds 200
$bootPath = Join-Path $PSScriptRoot 'cursor_bootstrap.md'
$boot = [System.IO.File]::ReadAllText($bootPath).Trim()
Set-Clip $boot
Start-Sleep -Milliseconds 80
[RotateUi]::Chord(0x11, 0x41)
Start-Sleep -Milliseconds 40
[RotateUi]::Chord(0x11, 0x56)
Start-Sleep -Milliseconds 350
Add-Type -AssemblyName System.Drawing
$shot = New-Object System.Drawing.Bitmap 700, 220
$sg = [System.Drawing.Graphics]::FromImage($shot)
$sg.CopyFromScreen(($wr.Left + 200), ($wr.Top + 70), 0, 0, (New-Object System.Drawing.Size 700, 220))
$shot.Save('C:\Users\s_sme\AppData\Local\Temp\cursor_before_send.png', [System.Drawing.Imaging.ImageFormat]::Png)
$sg.Dispose(); $shot.Dispose()
if ($StopBeforeCursorSend) { 'cursor bootstrap pasted, not sent'; return }
[RotateUi]::Chord(0x11, 0x0D) # Ctrl+Enter, force send
Start-Sleep -Milliseconds 500
'cursor bootstrap sent'
if ($StopBeforeCursorClose) { return }
# Ctrl+[ does not switch chats in this Agents window. The new agent opens to
# the right, so the chat that launched the script is the left tab.
[RotateUi]::Click(($wr.Left + 249), ($wr.Top + 58))
Start-Sleep -Milliseconds 300
[RotateUi]::Chord(0x11, 0x57) # Ctrl+W
Start-Sleep -Milliseconds 400
[RotateUi]::Key(0x0D, $false) # Enter confirms "Close Running Tab?"
[RotateUi]::Key(0x0D, $true)
'cursor previous chat closed'
