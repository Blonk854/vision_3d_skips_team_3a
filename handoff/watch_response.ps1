$target = Join-Path $PSScriptRoot 'team3_response.md'
$seen = $null
if (Test-Path -LiteralPath $target) {
    $item = Get-Item -LiteralPath $target
    $seen = '{0}|{1}' -f $item.Length, $item.LastWriteTimeUtc.Ticks
}
Write-Output "watching handoff/team3_response.md baseline=$seen"
while ($true) {
    if (Test-Path -LiteralPath $target) {
        $item = Get-Item -LiteralPath $target
        $stamp = '{0}|{1}' -f $item.Length, $item.LastWriteTimeUtc.Ticks
        if ($stamp -ne $seen -and $item.Length -gt 0) {
            Start-Sleep -Milliseconds 800
            $item2 = Get-Item -LiteralPath $target
            $stamp2 = '{0}|{1}' -f $item2.Length, $item2.LastWriteTimeUtc.Ticks
            if ($stamp2 -eq $stamp) {
                $seen = $stamp2
                Write-Output 'AGENT_LOOP_WAKE_team3 {"prompt":"Team 3 wrote handoff/team3_response.md. Follow .cursor/rules/vector-ownership-director.mdc. Read handoff/state.md, maps/vector_ownership/team3_next_prompt.txt, handoff/team3_response.md, and only the last ===== section of maps/vector_ownership/anomaly_begin_store_trace.txt. Judge the reply against that heading. Write the next question into team3_next_prompt.txt and update handoff/state.md. Then run handoff/rotate_threads.ps1. Do not do their byte work. Do not change the gate status."}'
            }
        }
    }
    Start-Sleep -Seconds 3
}
