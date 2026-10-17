# OpenCode Dev coordinator flow. Places OpenCode (Team 3) on the left half of
# the primary work area and OpenCode Dev (coordinator) on the right, then
# checks that rotate_threads.ps1 can find what it drives in each window: the
# session tab row, New session, and the Prompt box. Run this before a new
# handoff loop. It does not message either window and it does not start
# watch_response.ps1.
#
# Session tabs are found only when their top edge is within 46 logical
# pixels of the screen top, so both windows sit at the top of the primary
# monitor. Both apps are titled "OpenCode"; they are told apart by exact
# process name ('OpenCode' and 'OpenCode Dev'), never by 'OpenCode*'.
#
# Per-monitor DPI aware, like rotate_threads.ps1. Every rect here is
# physical pixels; logical sizes are multiplied by the window's DPI scale.

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms

$WorkerProcess = 'OpenCode'
$CoordinatorProcess = 'OpenCode Dev'

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PrepWin {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmd);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr hwnd);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  public static RECT Outer(IntPtr hwnd) {
    RECT r; GetWindowRect(hwnd, out r); return r;
  }
  public static void Place(IntPtr hwnd, int x, int y, int w, int h) {
    SetWindowPos(hwnd, IntPtr.Zero, x, y, w, h, 0x0014); // NOZORDER | NOACTIVATE
  }
}
"@
[void][PrepWin]::SetProcessDpiAwarenessContext([IntPtr](-4))
[void][PrepWin]::SetThreadDpiAwarenessContext([IntPtr](-4))

function Get-AppWindow([string]$processName) {
    $proc = Get-Process -Name $processName -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $proc) { throw "$processName window not found" }
    return $proc.MainWindowHandle
}

function Get-Scale([IntPtr]$hwnd) {
    $dpi = [PrepWin]::GetDpiForWindow($hwnd)
    if ($dpi -lt 96) { $dpi = 96 }
    return $dpi / 96.0
}

function Get-UiAll([IntPtr]$hwnd) {
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    return $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
}

function Test-RendererAccessibility([IntPtr]$hwnd, [string]$label) {
    # Electron/Chromium keeps the a11y tree off until a screen reader is
    # detected or --force-renderer-accessibility is set. With it off, UIA
    # only sees "Chrome Legacy Window" and Document / Prompt never appear.
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
Stable OpenCode (Team 3) already exposes its tree; this usually only affects OpenCode Dev.
"@
    }
}

function Get-ContentRect([IntPtr]$hwnd, [string]$label = 'window') {
    # Chromium exposes the document a moment after the window is first touched.
    foreach ($try in 1..5) {
        $best = $null
        foreach ($el in (Get-UiAll $hwnd)) {
            try {
                if ($el.Current.ControlType.ProgrammaticName -ne 'ControlType.Document') { continue }
                $r = $el.Current.BoundingRectangle
            } catch { continue }
            if ($r.Width -lt 100) { continue }
            if (-not $best -or $r.Width -gt $best.Width) { $best = $r }
        }
        if ($best) { return $best }
        Start-Sleep -Milliseconds 400
    }
    Test-RendererAccessibility $hwnd $label
    throw "$label content rect not found (no ControlType.Document). Open a session tab and keep the window visible."
}

function Set-ContentRect([IntPtr]$hwnd, [string]$label, [int]$x, [int]$y, [int]$w, [int]$h) {
    if ([PrepWin]::IsZoomed($hwnd) -or [PrepWin]::IsIconic($hwnd)) {
        [PrepWin]::ShowWindow($hwnd, 9) | Out-Null
        Start-Sleep -Milliseconds 250
    }
    $outer = [PrepWin]::Outer($hwnd)
    $content = Get-ContentRect $hwnd $label
    $padL = [int]($content.X - $outer.Left)
    $padT = [int]($content.Y - $outer.Top)
    $padR = [int]($outer.Right - ($content.X + $content.Width))
    $padB = [int]($outer.Bottom - ($content.Y + $content.Height))
    [PrepWin]::Place($hwnd, ($x - $padL), ($y - $padT), ($w + $padL + $padR), ($h + $padT + $padB))
    Start-Sleep -Milliseconds 300
    $content = Get-ContentRect $hwnd $label
    $dx = $x - [int]$content.X
    $dy = $y - [int]$content.Y
    $dw = $w - [int]$content.Width
    $dh = $h - [int]$content.Height
    if ($dx -or $dy -or $dw -or $dh) {
        $outer = [PrepWin]::Outer($hwnd)
        $ow = $outer.Right - $outer.Left
        $oh = $outer.Bottom - $outer.Top
        [PrepWin]::Place($hwnd, ($outer.Left + $dx), ($outer.Top + $dy), ($ow + $dw), ($oh + $dh))
        Start-Sleep -Milliseconds 300
    }
}

# What rotate_threads.ps1 needs from one window. Returns a list of problems.
function Test-Window([IntPtr]$hwnd, [string]$label, $work) {
    $tabRowMax = [int](46 * (Get-Scale $hwnd))
    $content = Get-ContentRect $hwnd $label
    $closeTop = $null
    $promptBottom = $null
    $newSession = $false
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            $name = $el.Current.Name
            $type = $el.Current.ControlType.ProgrammaticName
            $r = $el.Current.BoundingRectangle
        } catch { continue }
        if ($name -eq 'Close tab' -and $type -eq 'ControlType.Button' -and $r.Width -gt 2) {
            if ($null -eq $closeTop -or $r.Y -lt $closeTop) { $closeTop = [int]$r.Y }
        }
        if ($name -eq 'New session' -and $type -eq 'ControlType.Button') { $newSession = $true }
        if ($name -eq 'Prompt' -and $type -eq 'ControlType.Edit' -and $r.Height -gt 20) { $promptBottom = [int]($r.Y + $r.Height) }
    }
    $promptText = if ($null -eq $promptBottom) { 'hidden' } else { "$promptBottom" }
    Write-Host "$label content $([int]$content.X),$([int]$content.Y) $([int]$content.Width)x$([int]$content.Height); close-tab Y=$closeTop prompt bottom=$promptText New session button=$newSession"
    $problems = @()
    if ($null -eq $closeTop -or $closeTop -lt 0 -or $closeTop -gt $tabRowMax) { $problems += "$label session tab row is outside screen Y 0..$tabRowMax (open one session tab and keep the window at the screen top)" }
    if (-not $newSession) { $problems += "$label New session button not found" }
    if ($null -eq $promptBottom) { $problems += "$label Prompt box not found; open a session" }
    if (([int]($content.Y + $content.Height)) -gt $work.Bottom) { $problems += "$label extends under the taskbar" }
    if ($null -ne $promptBottom -and $promptBottom -gt $work.Bottom) { $problems += "$label prompt is under the taskbar" }
    return , $problems
}

$wh = Get-AppWindow $WorkerProcess
$ch = Get-AppWindow $CoordinatorProcess

# Fail fast with a clear fix if OpenCode Dev's renderer a11y is off.
Test-RendererAccessibility $wh 'OpenCode (Team 3)'
Test-RendererAccessibility $ch 'OpenCode Dev (coordinator)'

$work = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$leftW = [int]($work.Width / 2)
$rightW = $work.Width - $leftW

Set-ContentRect $wh 'OpenCode (Team 3)' $work.X $work.Y $leftW $work.Height
Set-ContentRect $ch 'OpenCode Dev (coordinator)' ($work.X + $leftW) $work.Y $rightW $work.Height

$S = Get-Scale $wh
"display scale $([int]($S * 100))% (dpi $([int]($S * 96))); all coordinates below are physical pixels"
if ($work.Y -gt (8 * $S)) {
    Write-Warning "Primary work area starts at Y=$($work.Y). Session tabs are found only when their screen Y is between 0 and $([int](46 * $S))."
}

$problems = @()
$wc = Get-ContentRect $wh 'OpenCode (Team 3)'
$cc = Get-ContentRect $ch 'OpenCode Dev (coordinator)'
if ([Math]::Abs([int]$wc.X - $work.X) -gt 1 -or [Math]::Abs([int]$wc.Width - $leftW) -gt 1) { $problems += 'OpenCode is not the left half' }
if ([Math]::Abs([int]$cc.X - ($work.X + $leftW)) -gt 1 -or [Math]::Abs([int]$cc.Width - $rightW) -gt 1) { $problems += 'OpenCode Dev is not the right half' }
$problems += Test-Window $wh 'OpenCode (Team 3)' $work
$problems += Test-Window $ch 'OpenCode Dev (coordinator)' $work
if ($problems.Count -gt 0) { throw ($problems -join '; ') }
'windows ready for handoff_oc/rotate_threads.ps1'
