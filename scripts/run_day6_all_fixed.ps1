# -------------------------------------------------
# run_day6_all_fixed.ps1
# -------------------------------------------------
$taskMap = @{
    3 = ".\scripts\task3_crossplatform_packaging.ps1"
    4 = ".\scripts\task4_unittest_suite.ps1"
    5 = ".\scripts\task5_cnn_verify.ps1"
    6 = ".\scripts\task6_user_config_ui.ps1"
    7 = ".\scripts\task7_doc_purge.ps1"
    8 = ".\scripts\task8_verification_backup.ps1"
}

foreach ($id in $taskMap.Keys) {
    Write-Host "`n=== Running Task $id ===" -ForegroundColor Cyan
    $script = $taskMap[$id]

    if (-not (Test-Path $script)) {
        Write-Warning "Script $script not found - skipping Task $id."
        continue
    }

    & $script
    $code = $LASTEXITCODE

    if ($code -eq 0) {
        Write-Host "Task $id finished successfully." -ForegroundColor Green
    } else {
        Write-Warning "Task $id exited with code $code"
    }
}

Write-Host "`nAll Day 6 tasks attempted. Check progress_log.json for final statuses." -ForegroundColor Magenta
