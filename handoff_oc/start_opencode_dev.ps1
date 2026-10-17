# Launch the OpenCode Dev coordinator with Chromium accessibility forced on.
# Without this, UI Automation only sees "Chrome Legacy Window", and
# prepare_windows.ps1 / rotate_threads.ps1 cannot find Prompt / New session.
#
# Close any running OpenCode Dev window first, then:
#   powershell -NoProfile -ExecutionPolicy Bypass -File handoff_oc/start_opencode_dev.ps1

$ErrorActionPreference = 'Stop'

$exe = Join-Path $env:LOCALAPPDATA 'OpenCode Dev\OpenCode Dev.exe'
if (-not (Test-Path -LiteralPath $exe)) {
    throw "OpenCode Dev not found at $exe"
}

$running = @(Get-Process -Name 'OpenCode Dev' -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
    throw "OpenCode Dev is already running (pids: $($running.Id -join ', ')). Close it, then run this script so --force-renderer-accessibility takes effect."
}

Start-Process -FilePath $exe -ArgumentList '--force-renderer-accessibility'
'started OpenCode Dev with --force-renderer-accessibility'
