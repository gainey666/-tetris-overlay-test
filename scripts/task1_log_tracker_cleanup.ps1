# -------------------------------------------------
# task1_log_tracker_cleanup.ps1
# -------------------------------------------------
<#!
.SYNOPSIS
    Initializes and cleans the Day 6 tracking assets (Task 1).
    - Guarantees progress_log.json exists with full task entries.
    - Marks Task 1 as done with a descriptive note.
    - (Re)creates the Day-6 master driver script with a clean header.
    - Removes stale temporary folders (verification_temp, temp, artifacts).
#>

$repoRoot   = Split-Path $PSScriptRoot -Parent
$logPath    = Join-Path $repoRoot 'progress_log.json'
$driverPath = Join-Path $repoRoot 'scripts\run_day6_all.ps1'

function Initialize-ProgressLog {
    if (-not (Test-Path $logPath)) {
        Write-Host "🔧 progress_log.json not found – creating default structure."
        $defaultTasks = @(
            [pscustomobject]@{ task_id=1; name='Log & tracker files';       status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=2; name='CI pipeline';              status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=3; name='Cross-platform packaging'; status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=4; name='Unit-test suite';          status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=5; name='Optional CNN backend';     status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=6; name='User-config UI';           status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=7; name='Documentation polish';     status='todo'; started_at=$null; finished_at=$null; note=$null },
            [pscustomobject]@{ task_id=8; name='Verification & backup';    status='todo'; started_at=$null; finished_at=$null; note=$null }
        )

        $logObject = [pscustomobject]@{
            date = (Get-Date).ToString('yyyy-MM-dd')
            total_estimated_hours = 10
            tasks = $defaultTasks
        }

        $logObject | ConvertTo-Json -Depth 5 | Set-Content -Path $logPath -Encoding UTF8
        Write-Host "✅ Created new progress_log.json"
    } else {
        Write-Host "✅ progress_log.json already exists."
    }
}

function Ensure-TaskOneDone {
    $logObject = Get-Content $logPath -Raw | ConvertFrom-Json
    if ($null -eq $logObject.tasks) {
        throw "progress_log.json is missing the 'tasks' array."
    }

    $taskOne = $logObject.tasks | Where-Object { $_.task_id -eq 1 }
    if (-not $taskOne) {
        $taskOne = [pscustomobject]@{
            task_id     = 1
            name        = 'Log & tracker files'
            status      = 'done'
            started_at  = (Get-Date).ToString('o')
            finished_at = (Get-Date).ToString('o')
            note        = 'Log & tracker files initialized'
        }
        $logObject.tasks += $taskOne
        Write-Host "➕ Added Task 1 entry."
    } else {
        $taskOne.status = 'done'
        if (-not $taskOne.started_at) { $taskOne.started_at = (Get-Date).ToString('o') }
        $taskOne.finished_at = (Get-Date).ToString('o')
        $taskOne.note = 'Log & tracker files initialized'
        Write-Host "🔄 Updated Task 1 entry to status=done."
    }

    $logObject | ConvertTo-Json -Depth 5 | Set-Content -Path $logPath -Encoding UTF8
}

function Write-DriverScript {
    $driverHeader = @"
# =========================================================
# run_day6_all.ps1 – Master driver for Day-6 tasks
# ---------------------------------------------------------
# This script runs Tasks 1-8 sequentially, updates
# progress_log.json after each step, and prints a short
# summary at the end.
# =========================================================
"@

    $driverBody = @"

`$scriptRoot = Split-Path `$MyInvocation.MyCommand.Path -Parent
`$repoRoot   = Split-Path `$scriptRoot -Parent
`$logPath    = Join-Path `$repoRoot 'progress_log.json'

if (-not (Test-Path `$logPath)) {
    Write-Error "❌ progress_log.json not found – aborting."
    exit 1
}

`$global:ProgressLog = Get-Content `$logPath -Raw | ConvertFrom-Json

function Set-TaskStatus {
    param(
        [int]   `$Id,
        [string]`$State,
        [string]`$Note = `$null
    )

    foreach (`$task in `$global:ProgressLog.tasks) {
        if (`$task.task_id -eq `$Id) {
            `$task.status = `$State
            if (`$Note) { `$task.note = `$Note }
            break
        }
    }

    `$json = `$global:ProgressLog | ConvertTo-Json -Depth 5
    Set-Content -Path `$logPath -Value `$json -Encoding UTF8
}

function Run-TaskScript {
    param(
        [int]   `$Id,
        [string]`$Name,
        [string]`$RelativeScript,
        [string]`$SuccessNote,
        [switch]`$Optional
    )

    Write-Host "`n--- Task `$Id: `$Name ---" -ForegroundColor Yellow

    `$scriptPath = Join-Path `$scriptRoot `$RelativeScript
    Set-TaskStatus -Id `$Id -State in_progress -Note "Running via master driver"

    if (-not (Test-Path `$scriptPath)) {
        `$msg = "Script missing: `$scriptPath"
        if (`$Optional) {
            Set-TaskStatus -Id `$Id -State skipped -Note `$msg
            Write-Warning "Skipping task `$Id – `$msg"
            return
        }
        Set-TaskStatus -Id `$Id -State blocked -Note `$msg
        throw `$msg
    }

    & `$scriptPath
    if (`$LASTEXITCODE -ne 0) {
        Set-TaskStatus -Id `$Id -State blocked -Note "Exit code `$LASTEXITCODE"
        throw "Task `$Id failed (exit `$LASTEXITCODE)."
    }

    Set-TaskStatus -Id `$Id -State done -Note `$SuccessNote
    Write-Host "Task `$Id complete." -ForegroundColor Green
}

Write-Host "`n=== Starting Day-6 batch ===" -ForegroundColor Cyan

Run-TaskScript -Id 1 -Name 'Log & tracker files'       -RelativeScript 'task1_log_tracker_cleanup.ps1'   -SuccessNote 'Log & tracker files initialized.'
Run-TaskScript -Id 2 -Name 'CI pipeline'               -RelativeScript '..\run_ci_pipeline_python.ps1'  -SuccessNote 'CI pipeline verified.'
Run-TaskScript -Id 3 -Name 'Cross-platform packaging'  -RelativeScript 'task3_crossplatform_packaging.ps1' -SuccessNote 'Packaging script executed.'
Run-TaskScript -Id 4 -Name 'Unit-test suite'           -RelativeScript 'task4_unittest_suite.ps1' -SuccessNote 'Unit tests executed.'
Run-TaskScript -Id 5 -Name 'CNN verification'          -RelativeScript 'task5_cnn_verify.ps1' -SuccessNote 'CNN verification completed.'
Run-TaskScript -Id 6 -Name 'ImGui UI configuration'    -RelativeScript 'task6_user_config_ui.ps1' -SuccessNote 'ImGui UI configured.'
Run-TaskScript -Id 7 -Name 'Documentation refresh'     -RelativeScript 'task7_doc_purge.ps1' -SuccessNote 'Documentation refreshed.'
Run-TaskScript -Id 8 -Name 'Verification & backup'     -RelativeScript 'task8_verification_backup.ps1' -SuccessNote 'Backup & verification completed.'

Write-Host "`n=== Day-6 batch finished ===" -ForegroundColor Cyan
"@

    $driverContent = $driverHeader + $driverBody
    Set-Content -Path $driverPath -Value $driverContent -Encoding UTF8
    Write-Host "✅ run_day6_all.ps1 refreshed."
}

function Cleanup-TempFolders {
    $tempFolders = @('verification_temp','temp','artifacts')
    foreach ($folder in $tempFolders) {
        $path = Join-Path $repoRoot $folder
        if (Test-Path $path) {
            Write-Host "🗑️  Removing stale temporary folder: $path"
            Remove-Item -Recurse -Force -Path $path
        }
    }
    Write-Host "✅ Temporary folder cleanup completed."
}

Initialize-ProgressLog
Ensure-TaskOneDone
Write-DriverScript
Cleanup-TempFolders
