# Places OpenCode on the left half of the primary work area and Cursor on
# the right, then drags the editor/agent split so the clicks in
# rotate_threads.ps1 land on the empty editor, the left agent tab, and the
# chat pane. Run this before a new handoff loop. It does not message
# OpenCode and it does not start watch_response.ps1.
#
# OpenCode's session tabs are found only when their top edge is within 46
# logical pixels of the screen top, so this script keeps that window at the
# top of the primary monitor. The primary side bar stays closed: the
# sidebar click is 30 logical pixels in from the Cursor window's left edge.
#
# Per-monitor DPI aware, like rotate_threads.ps1. Every rect here is
# physical pixels; logical offsets and sizes are multiplied by $S.

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms

# Same logical offsets as handoff/rotate_threads.ps1.
$SidebarDx = 30;  $SidebarDy = 180
$TabDx = 249;     $TabDy = 58
$ComposerDx = 420; $ComposerDy = 115
$CursorTitle = '*vision_3d_skips - team 3a*'

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PrepWin {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmd);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] inputs, int cb);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int n);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr hwnd);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [StructLayout(LayoutKind.Sequential)]
  public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  [StructLayout(LayoutKind.Explicit)]
  public struct INPUT {
    [FieldOffset(0)] public uint type;
    [FieldOffset(8)] public MOUSEINPUT mi;
  }
  public static RECT Outer(IntPtr hwnd) {
    RECT r; GetWindowRect(hwnd, out r); return r;
  }
  public static void Place(IntPtr hwnd, int x, int y, int w, int h) {
    SetWindowPos(hwnd, IntPtr.Zero, x, y, w, h, 0x0014); // NOZORDER | NOACTIVATE
  }
  public static void AllowForeground(IntPtr hwnd) {
    keybd_event(0x12, 0, 0, UIntPtr.Zero);
    keybd_event(0x12, 0, 2, UIntPtr.Zero);
    System.Threading.Thread.Sleep(40);
    SetForegroundWindow(hwnd);
    System.Threading.Thread.Sleep(180);
  }
  public static void Abs(int x, int y, uint flags) {
    int vx = GetSystemMetrics(76);
    int vy = GetSystemMetrics(77);
    int vw = GetSystemMetrics(78);
    int vh = GetSystemMetrics(79);
    INPUT inp = new INPUT();
    inp.type = 0;
    inp.mi.dx = (int)((x - vx) * 65535.0 / (vw - 1));
    inp.mi.dy = (int)((y - vy) * 65535.0 / (vh - 1));
    inp.mi.dwFlags = flags | 0x8000 | 0x4000; // ABSOLUTE | VIRTUALDESK
    SendInput(1, new INPUT[] { inp }, Marshal.SizeOf(typeof(INPUT)));
  }
}
"@
[void][PrepWin]::SetProcessDpiAwarenessContext([IntPtr](-4))
[void][PrepWin]::SetThreadDpiAwarenessContext([IntPtr](-4))

function Get-UiRoot([IntPtr]$hwnd) {
    return [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
}

function Get-UiAll([IntPtr]$hwnd) {
    $root = Get-UiRoot $hwnd
    return $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
}

function Get-ContentRect([IntPtr]$hwnd) {
    $best = $null
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            if ($el.Current.ControlType.ProgrammaticName -ne 'ControlType.Document') { continue }
            $r = $el.Current.BoundingRectangle
        } catch { continue }
        if ($r.Width -lt 100) { continue }
        if (-not $best -or $r.Width -gt $best.Width) { $best = $r }
    }
    if (-not $best) { throw 'window content rect not found' }
    return $best
}

function Set-ContentRect([IntPtr]$hwnd, [int]$x, [int]$y, [int]$w, [int]$h) {
    if ([PrepWin]::IsZoomed($hwnd)) {
        [PrepWin]::ShowWindow($hwnd, 9) | Out-Null
        Start-Sleep -Milliseconds 250
    }
    $outer = [PrepWin]::Outer($hwnd)
    $content = Get-ContentRect $hwnd
    $padL = [int]($content.X - $outer.Left)
    $padT = [int]($content.Y - $outer.Top)
    $padR = [int]($outer.Right - ($content.X + $content.Width))
    $padB = [int]($outer.Bottom - ($content.Y + $content.Height))
    [PrepWin]::Place($hwnd, ($x - $padL), ($y - $padT), ($w + $padL + $padR), ($h + $padT + $padB))
    Start-Sleep -Milliseconds 300
    $content = Get-ContentRect $hwnd
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

function Get-LeftAgentTab([IntPtr]$hwnd) {
    $best = $null
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            if ($el.Current.ControlType.ProgrammaticName -ne 'ControlType.TabItem') { continue }
            $r = $el.Current.BoundingRectangle
        } catch { continue }
        if ($r.Width -lt (40 * $S) -or $r.Height -lt (12 * $S) -or $r.Height -gt (40 * $S)) { continue }
        if ($r.Y -lt (20 * $S) -or $r.Y -gt (90 * $S)) { continue }
        if (-not $best -or $r.X -lt $best.X) { $best = $r }
    }
    if (-not $best) { throw 'no agent tab found; open the agent chat beside the editor and run again' }
    return $best
}

function Get-EditorRect([IntPtr]$hwnd) {
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            $name = $el.Current.Name
            $r = $el.Current.BoundingRectangle
        } catch { continue }
        if ($name -like 'Editor Group*' -and $r.Width -gt (40 * $S) -and $r.Height -gt (200 * $S)) { return $r }
    }
    return $null
}

function Get-SplitSash([IntPtr]$hwnd, [double]$tabX) {
    $best = $null
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            $className = $el.Current.ClassName
            if ($className -notlike 'monaco-sash vertical*') { continue }
            if ($className -like '*disabled*') { continue }
            $r = $el.Current.BoundingRectangle
        } catch { continue }
        if ($r.Height -lt (200 * $S) -or $r.Width -gt (16 * $S)) { continue }
        if ($r.X -ge $tabX) { continue }
        if (-not $best -or $r.X -gt $best.X) { $best = $r }
    }
    if (-not $best) { throw 'agent split sash not found; dock the agent chat to the right of the editor and run again' }
    return $best
}

function Move-SplitSash([IntPtr]$hwnd, [int]$delta, [double]$tabX) {
    if ([Math]::Abs($delta) -lt (4 * $S)) { return }
    $sash = Get-SplitSash $hwnd $tabX
    $sx = [int]($sash.X + $sash.Width / 2)
    $sy = [int]($sash.Y + [Math]::Min(400 * $S, $sash.Height / 2))
    $target = $sx + $delta
    [PrepWin]::AllowForeground($hwnd)
    [PrepWin]::Abs($sx, $sy, 0x0001)
    Start-Sleep -Milliseconds 100
    [PrepWin]::Abs($sx, $sy, 0x0002)
    Start-Sleep -Milliseconds 120
    foreach ($i in 1..20) {
        $x = [int]($sx + ($target - $sx) * $i / 20)
        [PrepWin]::Abs($x, $sy, 0x0001)
        Start-Sleep -Milliseconds 25
    }
    Start-Sleep -Milliseconds 80
    [PrepWin]::Abs($target, $sy, 0x0004)
    Start-Sleep -Milliseconds 400
}

function Test-TabClick([double]$tabX, [double]$tabW, [double]$tabY, [double]$tabH, [int]$clickX, [int]$clickY) {
    $m = 12 * $S
    return ($clickX -ge ($tabX + $m) -and $clickX -le ($tabX + $tabW - $m) -and $clickY -ge $tabY -and $clickY -le ($tabY + $tabH))
}

function Get-NamesAt([IntPtr]$hwnd, [int]$x, [int]$y) {
    $names = @()
    foreach ($el in (Get-UiAll $hwnd)) {
        try {
            $r = $el.Current.BoundingRectangle
            $name = $el.Current.Name
        } catch { continue }
        if (-not $name -or $r.Width -lt 2) { continue }
        if ($x -ge $r.X -and $x -le ($r.X + $r.Width) -and $y -ge $r.Y -and $y -le ($r.Y + $r.Height)) {
            $names += $name
        }
    }
    return @($names | Select-Object -Unique)
}

$oc = Get-Process | Where-Object { $_.ProcessName -like 'OpenCode*' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $oc) { throw 'OpenCode window not found' }
$cursor = Get-Process | Where-Object { $_.ProcessName -eq 'Cursor' -and $_.MainWindowTitle -like $CursorTitle } | Select-Object -First 1
if (-not $cursor) { throw 'Cursor window not found' }

$work = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$leftW = [int]($work.Width / 2)
$rightW = $work.Width - $leftW

Set-ContentRect $oc.MainWindowHandle $work.X $work.Y $leftW $work.Height
Set-ContentRect $cursor.MainWindowHandle ($work.X + $leftW) $work.Y $rightW $work.Height

$ch = $cursor.MainWindowHandle
$dpi = [PrepWin]::GetDpiForWindow($ch)
if ($dpi -lt 96) { $dpi = 96 }
$S = $dpi / 96.0
$tabRowMax = [int](46 * $S)
if ($work.Y -gt (8 * $S)) {
    Write-Warning "Primary work area starts at Y=$($work.Y). OpenCode tabs are found only when their screen Y is between 0 and $tabRowMax."
}

$outer = [PrepWin]::Outer($ch)
$tabClickX = $outer.Left + [int]($TabDx * $S)
$tabClickY = $outer.Top + [int]($TabDy * $S)
$tab = Get-LeftAgentTab $ch
if (-not (Test-TabClick $tab.X $tab.Width $tab.Y $tab.Height $tabClickX $tabClickY)) {
    $desiredLeft = $tabClickX - [int]($tab.Width / 2)
    Move-SplitSash $ch ([int]($desiredLeft - $tab.X)) $tab.X
    $outer = [PrepWin]::Outer($ch)
    $tabClickX = $outer.Left + [int]($TabDx * $S)
    $tabClickY = $outer.Top + [int]($TabDy * $S)
    $tab = Get-LeftAgentTab $ch
    if (-not (Test-TabClick $tab.X $tab.Width $tab.Y $tab.Height $tabClickX $tabClickY)) {
        $padLeft = $tabClickX - [int](16 * $S)
        Move-SplitSash $ch ([int]($padLeft - $tab.X)) $tab.X
        $tab = Get-LeftAgentTab $ch
    }
}

$outer = [PrepWin]::Outer($ch)
$tab = Get-LeftAgentTab $ch
$editor = Get-EditorRect $ch
$sash = Get-SplitSash $ch $tab.X
$sideX = $outer.Left + [int]($SidebarDx * $S)
$sideY = $outer.Top + [int]($SidebarDy * $S)
$tabX = $outer.Left + [int]($TabDx * $S)
$tabY = $outer.Top + [int]($TabDy * $S)
$compX = $outer.Left + [int]($ComposerDx * $S)
$compY = $outer.Top + [int]($ComposerDy * $S)

$ocContent = Get-ContentRect $oc.MainWindowHandle
$cuContent = Get-ContentRect $ch
"display scale $([int]($S * 100))% (dpi $dpi); all coordinates below are physical pixels"
"OpenCode content $([int]$ocContent.X),$([int]$ocContent.Y) $([int]$ocContent.Width)x$([int]$ocContent.Height)"
"Cursor content $([int]$cuContent.X),$([int]$cuContent.Y) $([int]$cuContent.Width)x$([int]$cuContent.Height)"

$sideNames = Get-NamesAt $ch $sideX $sideY
$tabNames = Get-NamesAt $ch $tabX $tabY
"sidebar click @$sideX,$sideY hits: $($sideNames -join ' | ')"
"tab click @$tabX,$tabY hits: $($tabNames -join ' | ')"
"composer click @$compX,$compY is right of the split: $($compX -gt ($sash.X + $sash.Width))"

$closeTop = $null
$promptBottom = $null
foreach ($el in (Get-UiAll $oc.MainWindowHandle)) {
    try {
        $name = $el.Current.Name
        $r = $el.Current.BoundingRectangle
    } catch { continue }
    if ($name -eq 'Close tab' -and $r.Width -gt 2) { $closeTop = [int]$r.Y }
    if ($name -eq 'Prompt' -and $r.Height -gt (20 * $S)) { $promptBottom = [int]($r.Y + $r.Height) }
}
$promptText = if ($null -eq $promptBottom) { 'hidden' } else { "$promptBottom" }
"OpenCode close-tab Y=$closeTop prompt bottom=$promptText work bottom=$($work.Bottom)"

$problems = @()
if ([Math]::Abs([int]$ocContent.X - $work.X) -gt 1 -or [Math]::Abs([int]$ocContent.Width - $leftW) -gt 1) { $problems += 'OpenCode is not the left half' }
if ([Math]::Abs([int]$cuContent.X - ($work.X + $leftW)) -gt 1 -or [Math]::Abs([int]$cuContent.Width - $rightW) -gt 1) { $problems += 'Cursor is not the right half' }
if (-not ($sideNames | Where-Object { $_ -like 'Editor Group*' })) { $problems += 'sidebar click missed the editor group; close the primary side bar and run again' }
if (-not (Test-TabClick $tab.X $tab.Width $tab.Y $tab.Height $tabX $tabY)) { $problems += 'tab click missed the left agent tab' }
if ($compX -le ($sash.X + $sash.Width)) { $problems += 'composer click is left of the agent split' }
if ($null -eq $editor) { $problems += 'editor group not found' }
if ($null -eq $closeTop -or $closeTop -lt 0 -or $closeTop -gt $tabRowMax) { $problems += "OpenCode tab row is outside screen Y 0..$tabRowMax" }
if (([int]($ocContent.Y + $ocContent.Height)) -gt $work.Bottom) { $problems += 'OpenCode extends under the taskbar' }
if ($null -ne $promptBottom -and $promptBottom -gt $work.Bottom) { $problems += 'OpenCode prompt is under the taskbar' }
if ($problems.Count -gt 0) { throw ($problems -join '; ') }
'windows ready for handoff/rotate_threads.ps1'
