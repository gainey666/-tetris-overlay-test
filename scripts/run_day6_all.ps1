# =========================================================
# run_day6_all.ps1 â€“ Master driver for Day-6 tasks
# ---------------------------------------------------------
# This script runs Tasks 1-8 sequentially, updates
# progress_log.json after each step, and prints a short
# summary at the end.
# =========================================================
$scriptRoot = Split-Path $MyInvocation.MyCommand.Path -Parent
$repoRoot   = Split-Path $scriptRoot -Parent
$logPath    = Join-Path $repoRoot 'progress_log.json'

if (-not (Test-Path $logPath)) {
    Write-Error "âŒ progress_log.json not found â€“ aborting."
    exit 1
}

$global:ProgressLog = Get-Content $logPath -Raw | ConvertFrom-Json

function Set-TaskStatus {
    param(
        [int]   $Id,
        [string]$State,
        [string]$Note = $null
    )

    foreach ($task in $global:ProgressLog.tasks) {
        if ($task.task_id -eq $Id) {
            $task.status = $State
            if ($Note) { $task.note = $Note }
            break
        }
    }

    $json = $global:ProgressLog | ConvertTo-Json -Depth 5
    Set-Content -Path $logPath -Value $json -Encoding UTF8
}

function Run-TaskScript {
    param(
        [int]   $Id,
        [string]$Name,
        [string]$RelativeScript,
        [string]$SuccessNote,
        [switch]$Optional
    )

    Write-Host "
--- Task $Id: $Name ---" -ForegroundColor Yellow

    $scriptPath = Join-Path $scriptRoot $RelativeScript
    Set-TaskStatus -Id $Id -State in_progress -Note "Running via master driver"

    if (-not (Test-Path $scriptPath)) {
        $msg = "Script missing: $scriptPath"
        if ($Optional) {
            Set-TaskStatus -Id $Id -State skipped -Note $msg
            Write-Warning "Skipping task $Id â€“ $msg"
            return
        }
        Set-TaskStatus -Id $Id -State blocked -Note $msg
        throw $msg
    }

    & $scriptPath
    if ($LASTEXITCODE -ne 0) {
        Set-TaskStatus -Id $Id -State blocked -Note "Exit code $LASTEXITCODE"
        throw "Task $Id failed (exit $LASTEXITCODE)."
    }

    Set-TaskStatus -Id $Id -State done -Note $SuccessNote
    Write-Host "Task $Id complete." -ForegroundColor Green
}

Write-Host "
=== Starting Day-6 batch ===" -ForegroundColor Cyan

Run-TaskScript -Id 1 -Name 'Log & tracker files'       -RelativeScript 'task1_log_tracker_cleanup.ps1'   -SuccessNote 'Log & tracker files initialized.'
Run-TaskScript -Id 2 -Name 'CI pipeline'               -RelativeScript '..\run_ci_pipeline_python.ps1'  -SuccessNote 'CI pipeline verified.'
Run-TaskScript -Id 3 -Name 'Cross-platform packaging'  -RelativeScript 'task3_crossplatform_packaging.ps1' -SuccessNote 'Packaging script executed.'
Run-TaskScript -Id 4 -Name 'Unit-test suite'           -RelativeScript 'task4_unittest_suite.ps1' -SuccessNote 'Unit tests executed.'
Run-TaskScript -Id 5 -Name 'CNN verification'          -RelativeScript 'task5_cnn_verify.ps1' -SuccessNote 'CNN verification completed.'
Run-TaskScript -Id 6 -Name 'ImGui UI configuration'    -RelativeScript 'task6_user_config_ui.ps1' -SuccessNote 'ImGui UI configured.'
Run-TaskScript -Id 7 -Name 'Documentation refresh'     -RelativeScript 'task7_doc_purge.ps1' -SuccessNote 'Documentation refreshed.'
Run-TaskScript -Id 8 -Name 'Verification & backup'     -RelativeScript 'task8_verification_backup.ps1' -SuccessNote 'Backup & verification completed.'

Write-Host "
=== Day-6 batch finished ===" -ForegroundColor Cyan
