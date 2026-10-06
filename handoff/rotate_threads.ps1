# Opens a new OpenCode session, closes the previous one, and sends a short
# notice. Then opens a new Cursor agent, pastes cursor_bootstrap.md, and
# closes the Cursor chat that launched this script.
# Requires powershell -STA. Each run places OpenCode on the left and
# Cursor on the right when either window has drifted.

param(
    [switch]$OpenCodeOnly,
    [switch]$CursorOnly,
    [switch]$StopBeforeCursorClose,
    [switch]$StopBeforeCursorSend,
    [switch]$MeasureCursorTabs,
    [switch]$ClickLeftTitle,
    [switch]$StopAfterNewAgent,
    [switch]$ShowComposerClick,
    [switch]$LayoutOnly
)

$ErrorActionPreference = 'Stop'
if ($PSCommandPath -like '*.disabled') {
    Write-Output 'rotate_threads is disabled. Rename it back to rotate_threads.ps1 only when the loop guard status in handoff/state.md is running.'
    exit 2
}
. (Join-Path $PSScriptRoot 'loop_guard.ps1')
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
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr value);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  public struct POINT { public int X; public int Y; }
  public static void Click(int x, int y) {
    SetCursorPos(x, y);
    System.Threading.Thread.Sleep(80);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
    System.Threading.Thread.Sleep(40);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
  public static void ClickPhysical(int x, int y) {
    IntPtr old = SetThreadDpiAwarenessContext(new IntPtr(-4));
    try {
      SetCursorPos(x, y);
      System.Threading.Thread.Sleep(120);
      mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
      System.Threading.Thread.Sleep(50);
      mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
    } finally {
      SetThreadDpiAwarenessContext(old);
    }
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
                    CloseEl = $c
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

function Invoke-UiElement($el) {
    # Prefer the accessibility Invoke pattern over a synthesized mouse click:
    # it is immune to the physical-vs-scaled coordinate mismatch that moves a
    # click off the intended control (and onto "New session", spawning empty
    # OpenCode sessions).
    $pat = $null
    try { $pat = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern) } catch {}
    if (-not $pat) { throw "element '$($el.Current.Name)' does not support Invoke" }
    $pat.Invoke()
}

function Get-OpenCodeRects([IntPtr]$hwnd) {
    # The unaware rect is the 1536x864 space SetCursorPos clicks in; the aware
    # rect is the physical space UIAutomation reports BoundingRectangle in.
    $un = New-Object RotateUi+RECT
    [RotateUi]::GetWindowRect($hwnd, [ref]$un) | Out-Null
    $old = [RotateUi]::SetThreadDpiAwarenessContext([IntPtr](-4))
    $aw = New-Object RotateUi+RECT
    try { [RotateUi]::GetWindowRect($hwnd, [ref]$aw) | Out-Null }
    finally { [void][RotateUi]::SetThreadDpiAwarenessContext($old) }
    return [pscustomobject]@{ Un = $un; Aw = $aw }
}

function Click-OpenCodeElement($el, $rects, [double]$fracX = 0.5, [double]$fracY = 0.5, [int]$offsetX = -1, [int]$offsetY = -1) {
    # UIAutomation BoundingRectangle is physical. Offset from the top-left so
    # the click sits on the first text line. Click from a DPI-aware thread so
    # the cursor is not scaled a second time. $rects is unused; callers still
    # pass the window rects.
    $r = $el.Current.BoundingRectangle
    if ($offsetX -ge 0) { $px = $r.X + $offsetX } else { $px = $r.X + $r.Width * $fracX }
    if ($offsetY -ge 0) { $py = $r.Y + $offsetY } else { $py = $r.Y + $r.Height * $fracY }
    [RotateUi]::ClickPhysical([int][Math]::Round($px), [int][Math]::Round($py))
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

function Measure-CursorChatTabs([System.Drawing.Bitmap]$bmp) {
    # Light tab strip: dark glyphs on a pale row. y=48..84 sits under the menu
    # and on the chat-tab titles. A close glyph is a short cluster with a wide
    # gap on both sides; letters sit closer together.
    $y0 = 48
    $y1 = 84
    $cols = New-Object int[] $bmp.Width
    for ($x = 0; $x -lt $bmp.Width; $x++) {
        for ($y = $y0; $y -le $y1; $y++) {
            $c = $bmp.GetPixel($x, $y)
            if (($c.R + $c.G + $c.B) -lt 420) { $cols[$x]++ }
        }
    }
    $raw = New-Object System.Collections.Generic.List[object]
    $in = $false
    $start = 0
    for ($x = 0; $x -lt $bmp.Width; $x++) {
        if ($cols[$x] -ge 2) {
            if (-not $in) { $in = $true; $start = $x }
        } elseif ($in) {
            $raw.Add([pscustomobject]@{ A = $start; B = ($x - 1) })
            $in = $false
        }
    }
    if ($in) { $raw.Add([pscustomobject]@{ A = $start; B = ($bmp.Width - 1) }) }
    # A close glyph can have a one-pixel hole. Join those holes, and leave the
    # wider gaps between letters alone.
    $merged = New-Object System.Collections.Generic.List[object]
    foreach ($cluster in $raw) {
        if ($merged.Count -gt 0) {
            $prev = $merged[$merged.Count - 1]
            if (($cluster.A - $prev.B - 1) -le 1) {
                $prev.B = $cluster.B
                continue
            }
        }
        $merged.Add([pscustomobject]@{ A = $cluster.A; B = $cluster.B })
    }
    $marks = New-Object System.Collections.Generic.List[object]
    for ($i = 0; $i -lt $merged.Count; $i++) {
        $width = $merged[$i].B - $merged[$i].A + 1
        if ($width -lt 7 -or $width -gt 16) { continue }
        $gapBefore = 999
        if ($i -gt 0) { $gapBefore = $merged[$i].A - $merged[$i - 1].B - 1 }
        $gapAfter = 999
        if (($i + 1) -lt $merged.Count) { $gapAfter = $merged[$i + 1].A - $merged[$i].B - 1 }
        if ($gapBefore -ge 16 -and $gapAfter -ge 12) { $marks.Add($merged[$i]) }
    }
    # The chat-panel icon sits just past the only tab's close glyph and has no
    # title of its own. A real second tab has label ink between the two glyphs.
    $kept = New-Object System.Collections.Generic.List[object]
    $prevEnd = -1
    foreach ($mark in $marks) {
        $hasLabel = $false
        foreach ($cluster in $merged) {
            if ($cluster.A -gt $prevEnd -and $cluster.B -le ($mark.A - 18) -and ($cluster.B - $cluster.A + 1) -ge 8) {
                $hasLabel = $true
                break
            }
        }
        if ($hasLabel) {
            $kept.Add($mark)
            $prevEnd = $mark.B
        }
    }
    # The active tab often hides its close glyph. A wide title right after the
    # last glyph is that second tab. The toolbar at the right end of the row
    # (+, history, ..., panel) is far from the glyph and is not a tab.
    if ($kept.Count -ge 1) {
        $after = $kept[$kept.Count - 1].B
        $first = $null
        foreach ($cluster in $merged) {
            if ($cluster.A -le $after) { continue }
            if (($cluster.B - $cluster.A + 1) -lt 4) { continue }
            if ($null -eq $first) {
                $first = [pscustomobject]@{ A = $cluster.A; B = $cluster.B }
                continue
            }
            if (($cluster.A - $first.B - 1) -ge 24) { break }
            $first.B = $cluster.B
        }
        if ($null -ne $first -and ($first.A - $after) -le 120 -and ($first.B - $first.A) -ge 24) {
            $kept.Add($first)
        }
    }
    # Same hidden glyph, on the left tab. Letter gaps inside one title are
    # smaller than the gap between two titles. The group nearest the glyph
    # belongs to that glyph. An earlier wide group is a tab with no X.
    if ($kept.Count -ge 1) {
        $glyphA = $kept[0].A
        $groups = New-Object System.Collections.Generic.List[object]
        foreach ($cluster in $merged) {
            $width = $cluster.B - $cluster.A + 1
            if ($width -lt 4) { continue }
            if ($cluster.B -gt ($glyphA - 18)) { continue }
            if ($cluster.A -lt ($glyphA - 420)) { continue }
            if ($groups.Count -gt 0) {
                $prev = $groups[$groups.Count - 1]
                if (($cluster.A - $prev.B - 1) -lt 24) {
                    if ($cluster.B -gt $prev.B) { $prev.B = $cluster.B }
                    continue
                }
            }
            $groups.Add([pscustomobject]@{ A = $cluster.A; B = $cluster.B })
        }
        if ($groups.Count -ge 2) {
            $insertAt = 0
            for ($g = 0; $g -lt ($groups.Count - 1); $g++) {
                $span = $groups[$g].B - $groups[$g].A + 1
                if ($span -lt 24) { continue }
                $kept.Insert($insertAt, [pscustomobject]@{ A = $groups[$g].A; B = $groups[$g].B })
                $insertAt++
            }
        }
    }
    return [pscustomobject]@{ Cols = $cols; Raw = $merged; Marks = $kept; Y0 = $y0; Y1 = $y1 }
}

function Get-LeftChatTabClick([System.Drawing.Bitmap]$bmp) {
    $found = Measure-CursorChatTabs $bmp
    $markText = (($found.Marks | ForEach-Object { "$($_.A)-$($_.B)" }) -join ' ')
    if ($found.Marks.Count -lt 2) {
        return [pscustomobject]@{ Ok = $false; Reason = "need two chat tabs, saw $($found.Marks.Count) ($markText)" }
    }
    $left = $found.Marks[0]
    $leftWidth = $left.B - $left.A + 1
    if ($leftWidth -gt 16) {
        $prefer = [int](($left.A + $left.B) / 2)
        $best = $null
        $bestDist = 999
        for ($x = $left.A; $x -le $left.B; $x++) {
            if ($found.Cols[$x] -ge 2) {
                $dist = [Math]::Abs($x - $prefer)
                if ($dist -lt $bestDist) { $bestDist = $dist; $best = $x }
            }
        }
        if ($null -eq $best) {
            return [pscustomobject]@{ Ok = $false; Reason = "left chat title $($left.A)-$($left.B) has no ink" }
        }
        $ySum = 0
        $yN = 0
        for ($y = $found.Y0; $y -le $found.Y1; $y++) {
            $c = $bmp.GetPixel($best, $y)
            if (($c.R + $c.G + $c.B) -lt 420) { $ySum += $y; $yN++ }
        }
        if ($yN -lt 1) {
            return [pscustomobject]@{ Ok = $false; Reason = 'left chat label row is empty' }
        }
        return [pscustomobject]@{ Ok = $true; X = $best; Y = [int]($ySum / $yN); Marks = $markText }
    }
    $labelEnd = $left.A - 18
    $labelA = $null
    $labelB = $null
    foreach ($cluster in $found.Raw) {
        if ($cluster.B -le $labelEnd -and $cluster.A -ge ($left.A - 220)) {
            if ($null -eq $labelA -or $cluster.A -lt $labelA) { $labelA = $cluster.A }
            if ($null -eq $labelB -or $cluster.B -gt $labelB) { $labelB = $cluster.B }
        }
    }
    if ($null -eq $labelA) {
        return [pscustomobject]@{ Ok = $false; Reason = "left chat tab has a close mark at $($left.A) but no label" }
    }
    $prefer = [int](($labelA + $labelB) / 2)
    $best = $null
    $bestDist = 999
    for ($x = $labelA; $x -le $labelEnd; $x++) {
        if ($found.Cols[$x] -ge 2) {
            $dist = [Math]::Abs($x - $prefer)
            if ($dist -lt $bestDist) { $bestDist = $dist; $best = $x }
        }
    }
    if ($null -eq $best -or $best -gt ($left.A - 18)) {
        return [pscustomobject]@{ Ok = $false; Reason = "left chat label is not clear of the close mark at $($left.A)-$($left.B)" }
    }
    $ySum = 0
    $yN = 0
    for ($y = $found.Y0; $y -le $found.Y1; $y++) {
        $c = $bmp.GetPixel($best, $y)
        if (($c.R + $c.G + $c.B) -lt 420) { $ySum += $y; $yN++ }
    }
    if ($yN -lt 1) {
        return [pscustomobject]@{ Ok = $false; Reason = 'left chat label row is empty' }
    }
    return [pscustomobject]@{ Ok = $true; X = $best; Y = [int]($ySum / $yN); Marks = $markText }
}

function Test-HandoffRect($rect, $x, $y, $w, $h) {
    $dw = [Math]::Abs($rect.Left - $x)
    $dy = [Math]::Abs($rect.Top - $y)
    $dW = [Math]::Abs(($rect.Right - $rect.Left) - $w)
    $dH = [Math]::Abs(($rect.Bottom - $rect.Top) - $h)
    return ($dw -le 2 -and $dy -le 2 -and $dW -le 2 -and $dH -le 2)
}

function Place-HandoffWindow($hwnd, $x, $y, $w, $h, $name) {
    $rect = New-Object RotateUi+RECT
    [RotateUi]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    if (Test-HandoffRect $rect $x $y $w $h) { return $false }
    if ([RotateUi]::IsZoomed($hwnd)) {
        [RotateUi]::ShowWindow($hwnd, 9) | Out-Null
        Start-Sleep -Milliseconds 200
    }
    [RotateUi]::SetWindowPos($hwnd, [IntPtr]::Zero, $x, $y, $w, $h, 0x0014) | Out-Null
    Start-Sleep -Milliseconds 200
    [RotateUi]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    if (-not (Test-HandoffRect $rect $x $y $w $h)) {
        [RotateUi]::ShowWindow($hwnd, 9) | Out-Null
        Start-Sleep -Milliseconds 200
        [RotateUi]::SetWindowPos($hwnd, [IntPtr]::Zero, $x, $y, $w, $h, 0x0004) | Out-Null
        Start-Sleep -Milliseconds 200
        [RotateUi]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    }
    if (-not (Test-HandoffRect $rect $x $y $w $h)) {
        $gotW = $rect.Right - $rect.Left
        $gotH = $rect.Bottom - $rect.Top
        throw "$name stayed at $($rect.Left),$($rect.Top) ${gotW}x${gotH}; wanted $x,$y ${w}x${h}"
    }
    return $true
}

# Clicks are offsets from Cursor's top-left in the coordinate space this
# process sees. On the 1920x1080 display at 125%, that space is 1536x864.
# OpenCode's right edge is Cursor's left edge, so the windows do not overlap.
function Ensure-HandoffLayout {
    $screenW = [RotateUi]::GetSystemMetrics(0)
    $screenH = [RotateUi]::GetSystemMetrics(1)
    if ($screenW -ne 1536 -or $screenH -ne 864) {
        throw "handoff layout is calibrated for a 1536 by 864 view. This process sees $screenW by $screenH."
    }
    $oc = Get-Process | Where-Object { $_.ProcessName -eq 'OpenCode' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    $cursor = Get-Process | Where-Object { $_.ProcessName -eq 'Cursor' -and $_.MainWindowTitle -like '*vision_3d_skips*' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ((-not $CursorOnly) -and -not $oc) { throw 'OpenCode window not found' }
    if ((-not $OpenCodeOnly) -and -not $cursor) { throw 'Cursor window not found' }
    $moved = @()
    if ($oc -and (Place-HandoffWindow $oc.MainWindowHandle -2 0 807 870 'OpenCode')) { $moved += 'OpenCode' }
    if ($cursor -and (Place-HandoffWindow $cursor.MainWindowHandle 805 0 731 864 'Cursor')) { $moved += 'Cursor' }
    if ($moved.Count -eq 0) { return 'layout already OpenCode -2,0 807x870; Cursor 805,0 731x864' }
    return "layout placed $($moved -join ', ')"
}

# CopyFromScreen reads physical pixels, but GetWindowRect and SetCursorPos
# in this DPI-unaware process use the scaled 1536x864 view. Capture by the
# physical rect, then divide by the window's scale before clicking.
function Get-CursorPhysicalRect([IntPtr]$hwnd) {
    $old = [RotateUi]::SetThreadDpiAwarenessContext([IntPtr](-4))
    $pr = New-Object RotateUi+RECT
    try {
        [RotateUi]::GetWindowRect($hwnd, [ref]$pr) | Out-Null
    } finally {
        [void][RotateUi]::SetThreadDpiAwarenessContext($old)
    }
    return $pr
}

function Copy-CursorWindow([IntPtr]$hwnd, [int]$height) {
    $pr = Get-CursorPhysicalRect $hwnd
    $width = $pr.Right - $pr.Left
    $old = [RotateUi]::SetThreadDpiAwarenessContext([IntPtr](-4))
    try {
        $bmp = New-Object System.Drawing.Bitmap $width, $height
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($pr.Left, $pr.Top, 0, 0, (New-Object System.Drawing.Size $width, $height))
        $g.Dispose()
    } finally {
        [void][RotateUi]::SetThreadDpiAwarenessContext($old)
    }
    return $bmp
}

function Copy-CursorTabRow([IntPtr]$hwnd) {
    return Copy-CursorWindow $hwnd 100
}

function Save-CursorShot([IntPtr]$hwnd, [string]$name) {
    $shot = Copy-CursorWindow $hwnd 350
    $shot.Save((Join-Path 'C:\Users\s_sme\AppData\Local\Temp' $name), [System.Drawing.Imaging.ImageFormat]::Png)
    $shot.Dispose()
}

function Get-CursorScreenPoint([IntPtr]$hwnd, $wr, [int]$imageX, [int]$imageY) {
    $pr = Get-CursorPhysicalRect $hwnd
    $scale = ($pr.Right - $pr.Left) / [double]($wr.Right - $wr.Left)
    return [pscustomobject]@{
        X = $wr.Left + [int][Math]::Round($imageX / $scale)
        Y = $wr.Top + [int][Math]::Round($imageY / $scale)
    }
}

function Get-CursorChatCount([IntPtr]$hwnd) {
    $band = Copy-CursorTabRow $hwnd
    try {
        $found = Measure-CursorChatTabs $band
        if ($null -eq $found.Marks) { return -1 }
        return [int]$found.Marks.Count
    } finally {
        $band.Dispose()
    }
}

function Get-CursorNamedChatCount([IntPtr]$hwnd) {
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    $count = 0
    foreach ($el in $all) {
        $name = [string]$el.Current.Name
        if ($name -like 'Team 3 response*') { $count++ }
    }
    return $count
}

function Close-LeftCursorChat([IntPtr]$hwnd) {
    $before = Get-CursorChatCount $hwnd
    if ($before -lt 2) { return $false }
    $wr = New-Object RotateUi+RECT
    [RotateUi]::GetWindowRect($hwnd, [ref]$wr) | Out-Null
    $hit = $null
    $band = $null
    foreach ($try in 1..8) {
        if ($band) { $band.Dispose() }
        $band = Copy-CursorTabRow $hwnd
        $hit = Get-LeftChatTabClick $band
        if ($hit.Ok) { break }
        Start-Sleep -Milliseconds 250
    }
    if ($band) {
        $band.Save((Join-Path $env:TEMP 'cursor_tab_close.png'), [System.Drawing.Imaging.ImageFormat]::Png)
        $band.Dispose()
    }
    if (-not $hit -or -not $hit.Ok) { return $false }
    $pt = Get-CursorScreenPoint $hwnd $wr $hit.X $hit.Y
    "cursor left tab label at image $($hit.X),$($hit.Y) ; click $($pt.X),$($pt.Y) ; close marks $($hit.Marks)"
    [RotateUi]::AllowForeground($hwnd)
    [RotateUi]::Click($pt.X, $pt.Y)
    Start-Sleep -Milliseconds 300
    [RotateUi]::Chord(0x11, 0x57) # Ctrl+W
    Start-Sleep -Milliseconds 400
    [RotateUi]::Key(0x0D, $false) # Enter confirms "Close Running Tab?"
    [RotateUi]::Key(0x0D, $true)
    Start-Sleep -Milliseconds 400
    $after = Get-CursorChatCount $hwnd
    return ($after -ge 0 -and $after -lt $before)
}

function Assert-OneCursorChatBeforeOpen {
    $cursor = Get-Process | Where-Object { $_.ProcessName -eq 'Cursor' -and $_.MainWindowTitle -like '*vision_3d_skips*' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $cursor) { throw 'abort: Cursor window not found. Not opening a chat.' }
    $hwnd = [IntPtr]$cursor.MainWindowHandle
    $named = 0
    try { $named = Get-CursorNamedChatCount $hwnd } catch { $named = 0 }
    if ($named -gt 2) {
        $reason = "abort: UI Automation sees $named Team 3 chats. Not opening another."
        Update-LoopGuardFields -Fields @{ status = 'stopped'; pause_reason = $reason; tracked_open_chats = "$named" }
        Write-LoopAlert -Reason $reason
        throw $reason
    }
    $count = Get-CursorChatCount $hwnd
    if ($count -gt 2) {
        $reason = "abort: $count Cursor chats are open. Not opening another."
        Update-LoopGuardFields -Fields @{ status = 'stopped'; pause_reason = $reason; tracked_open_chats = "$count" }
        Write-LoopAlert -Reason $reason
        throw $reason
    }
    if ($count -eq 2) {
        if (-not (Close-LeftCursorChat $hwnd)) {
            $reason = 'abort: could not close the old Cursor chat. Not opening another.'
            Update-LoopGuardFields -Fields @{ status = 'stopped'; pause_reason = $reason; tracked_open_chats = '2' }
            Write-LoopAlert -Reason $reason
            throw $reason
        }
        $count = Get-CursorChatCount $hwnd
    }
    if ($count -ne 1) {
        $reason = "abort: need exactly one Cursor chat before opening another, saw $count."
        Update-LoopGuardFields -Fields @{ status = 'stopped'; pause_reason = $reason }
        Write-LoopAlert -Reason $reason
        throw $reason
    }
}

if ($MeasureCursorTabs -or $ClickLeftTitle -or $StopAfterNewAgent -or $ShowComposerClick) { $CursorOnly = $true }

Ensure-HandoffLayout
if ($LayoutOnly) { return }

$calibrateOnly = $MeasureCursorTabs -or $ClickLeftTitle -or $ShowComposerClick
if (-not $calibrateOnly) {
    $decision = Test-LoopGuardRotation -ForRotate -Alert
    if ($decision.Result -ne 'allow') {
        throw "rotation refused: $($decision.Reason)"
    }
    # Consume the rate limit as soon as a rotation is allowed, so a failed
    # UI step cannot be retried in a tight loop.
    Update-LoopGuardFields -Fields @{ last_rotation_utc = [datetime]::UtcNow.ToString('o') }
}
if (-not $calibrateOnly -and -not $OpenCodeOnly) {
    Assert-OneCursorChatBeforeOpen
}

if (-not $CursorOnly) {
    $oc = Get-OpenCodeProcess
    $hwnd = $oc.MainWindowHandle
    [RotateUi]::AllowForeground($hwnd)
    $ocRects = Get-OpenCodeRects $hwnd
    $beforeTabs = @(Get-OpenCodeSessionTabs $hwnd)
    if ($beforeTabs.Count -lt 1) { throw 'no OpenCode session tab to rotate' }
    $before = @($beforeTabs | ForEach-Object { $_.Name })
    "open code before: $($before -join ' | ')"
    $newBtn = Find-OpenCodeButton $hwnd 'New session'
    if (-not $newBtn) { throw 'New session button not found' }
    Invoke-UiElement $newBtn
    $now = @()
    foreach ($wait in 1..12) {
        Start-Sleep -Milliseconds 300
        $now = @(Get-OpenCodeSessionTabs $hwnd)
        if ($now.Count -gt $beforeTabs.Count) { break }
    }
    if ($now.Count -le $beforeTabs.Count) { throw 'new OpenCode session did not appear; old session left open' }
    $keep = $now | Sort-Object CloseX | Select-Object -Last 1
    "open code fresh: $($keep.Name) at $($keep.CloseX),$($keep.CloseY)"
    $old = @($now | Where-Object { -not ($_.CloseX -eq $keep.CloseX -and $_.CloseY -eq $keep.CloseY) } | Sort-Object CloseX -Descending)
    foreach ($tab in $old) {
        "closing old session '$($tab.Name)' at $($tab.CloseX),$($tab.CloseY)"
        Invoke-UiElement $tab.CloseEl
        Start-Sleep -Milliseconds 450
    }
    $left = @(Get-OpenCodeSessionTabs $hwnd)
    if ($left.Count -lt 1) { throw 'OpenCode session tab disappeared' }
    if ($left.Count -ne 1) { throw "old OpenCode session still open: $($left.Name -join ' | ')" }
    "open code remaining: $($left.Name -join ' | ')"

    $notice = 'Continue from maps/vector_ownership/team3_next_prompt.txt'
    $prompt = Find-PromptEdit $hwnd
    # Tab changes drop keyboard focus. Take it back immediately before the click,
    # or the paste lands in whatever window is still active.
    [RotateUi]::AllowForeground($hwnd)
    try { $prompt.SetFocus() } catch {}
    # First line of the prompt: 16px padding plus the middle of the 20px line.
    # The card center sits below that line and does not focus the editor.
    Click-OpenCodeElement $prompt $ocRects -offsetX 80 -offsetY 26
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
            Invoke-UiElement $send
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

if ($OpenCodeOnly) {
    Register-LoopRotation
    return
}

$cursor = Get-Process | Where-Object { $_.ProcessName -eq 'Cursor' -and $_.MainWindowTitle -like '*vision_3d_skips*' } | Select-Object -First 1
if (-not $cursor) { throw 'Cursor window not found' }
$ch = $cursor.MainWindowHandle
$wr = New-Object RotateUi+RECT
[RotateUi]::GetWindowRect($ch, [ref]$wr) | Out-Null
if ($ShowComposerClick) {
    [RotateUi]::AllowForeground($ch)
    $sx = $wr.Left + 420
    $sy = $wr.Top + 115
    [RotateUi]::Click($sx, $sy)
    Start-Sleep -Milliseconds 350
    $cursorAt = New-Object RotateUi+POINT
    [RotateUi]::GetCursorPos([ref]$cursorAt) | Out-Null
    "composer clicked at $sx,$sy ; pointer $($cursorAt.X),$($cursorAt.Y) ; not pasted"
    Save-CursorShot $ch 'cursor_composer_click.png'
    return
}
if ($MeasureCursorTabs -or $ClickLeftTitle) {
    $band = Copy-CursorTabRow $ch
    $hit = Get-LeftChatTabClick $band
    $found = Measure-CursorChatTabs $band
    $markText = (($found.Marks | ForEach-Object { "$($_.A)-$($_.B)" }) -join ' ')
    "cursor tab close marks: $markText"
    if ($hit.Ok) {
        $pt = Get-CursorScreenPoint $ch $wr $hit.X $hit.Y
        "cursor left tab label: image $($hit.X),$($hit.Y) ; click $($pt.X),$($pt.Y)"
    } else {
        "cursor left tab not closed: $($hit.Reason)"
    }
    $band.Save('C:\Users\s_sme\AppData\Local\Temp\cursor_tab_measure.png', [System.Drawing.Imaging.ImageFormat]::Png)
    $band.Dispose()
    if ($ClickLeftTitle) {
        if (-not $hit.Ok) { throw "cursor left title not clicked: $($hit.Reason)" }
        [RotateUi]::AllowForeground($ch)
        [RotateUi]::Click($pt.X, $pt.Y)
        Start-Sleep -Milliseconds 350
        $cursorAt = New-Object RotateUi+POINT
        [RotateUi]::GetCursorPos([ref]$cursorAt) | Out-Null
        "cursor left tab clicked at $($pt.X),$($pt.Y) ; pointer $($cursorAt.X),$($cursorAt.Y) ; not closed"
        Save-CursorShot $ch 'cursor_after_left_click.png'
    }
    return
}
if ($StopAfterNewAgent) {
    $before = Copy-CursorTabRow $ch
    $foundBefore = Measure-CursorChatTabs $before
    $before.Dispose()
    $beforeText = (($foundBefore.Marks | ForEach-Object { "$($_.A)-$($_.B)" }) -join ' ')
    "tabs before new agent: $beforeText"
}
[RotateUi]::AllowForeground($ch)
# Empty sidebar, above the New Agent label, so the shortcut is not swallowed by the composer.
[RotateUi]::Click(($wr.Left + 30), ($wr.Top + 180))
Start-Sleep -Milliseconds 180
Update-LoopGuardFields -Fields @{ tracked_open_chats = '2' }
[RotateUi]::Chord(0x11, 0x10, 0x4C) # Ctrl+Shift+L, New Agent
Start-Sleep -Milliseconds 700
if ($StopAfterNewAgent) {
    $band = Copy-CursorTabRow $ch
    $found = Measure-CursorChatTabs $band
    $band.Dispose()
    $markText = (($found.Marks | ForEach-Object { "$($_.A)-$($_.B)" }) -join ' ')
    "tabs after new agent: $markText"
    Save-CursorShot $ch 'cursor_after_new_agent.png'
    'new agent shortcut sent, not pasted'
    return
}
# Fresh agent composer sits under the tab row.
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
Save-CursorShot $ch 'cursor_before_send.png'
if ($StopBeforeCursorSend) { 'cursor bootstrap pasted, not sent'; return }
[RotateUi]::Chord(0x11, 0x0D) # Ctrl+Enter, force send
Start-Sleep -Milliseconds 500
'cursor bootstrap sent'
if ($StopBeforeCursorClose) { return }
# The new agent is already open. Close the chat that launched this script.
# If that close cannot be proved, stop the loop instead of leaving a third chat.
if (-not (Close-LeftCursorChat $ch)) {
    $reason = 'Opened a Cursor chat but could not close the old one. Loop stopped.'
    Update-LoopGuardFields -Fields @{ status = 'stopped'; pause_reason = $reason; tracked_open_chats = '2' }
    Write-LoopAlert -Reason $reason
    throw $reason
}
$leftOpen = Get-CursorChatCount $ch
if ($leftOpen -ne 1) {
    $reason = "After close, $leftOpen Cursor chats are still open. Loop stopped."
    Update-LoopGuardFields -Fields @{ status = 'stopped'; pause_reason = $reason; tracked_open_chats = "$leftOpen" }
    Write-LoopAlert -Reason $reason
    throw $reason
}
Register-LoopRotation
'cursor previous chat closed'
