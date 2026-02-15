# -------------------------------------------------
# task7_doc_purge.ps1
# -------------------------------------------------
function Set-Status {
    param([int]$Id, [string]$State, [string]$Note=$null)
    .\update_task.ps1 -id $Id -newStatus $State $(if($Note){ "-note `"$Note`"" })
}

Set-Status -Id 7 -State in_progress -Note "Updating documentation"

$repoRoot   = Split-Path $PSScriptRoot -Parent
$readmePath = Join-Path $repoRoot 'README.md'
$logPath    = Join-Path $repoRoot 'progress_log.json'

if (-not (Test-Path $readmePath)) {
    Set-Status -Id 7 -State blocked -Note "README.md not found."
    Write-Error "README.md not found at $readmePath"
    return
}

if (-not (Test-Path $logPath)) {
    Set-Status -Id 7 -State blocked -Note "progress_log.json missing."
    Write-Error "progress_log.json not found at $logPath"
    return
}

$progress = Get-Content $logPath -Raw | ConvertFrom-Json

# Build badge block
$badgeLines = @('# 📊 Project Status', '', '| Task | Status | Note |', '|------|--------|------|')
foreach ($entry in $progress.tasks) {
    $noteValue = if ($null -ne $entry.note) { $entry.note } else { '' }
    $note = $noteValue -replace '\|','&#124;'
    $badgeLines += "| $($entry.task_id) | $($entry.status) | $note |"
}
$badgeSection = @"
<!--- STATUS-BADGES-START --->
$($badgeLines -join "`n")
<!--- STATUS-BADGES-END   --->
"@

# Build tasks overview
$descMap = @{
    1 = 'Log & tracker cleanup'
    2 = 'CI pipeline verification'
    3 = 'Cross-platform packaging'
    4 = 'Unit-test suite'
    5 = 'CNN verification'
    6 = 'ImGui UI configuration'
    7 = 'Documentation refresh'
    8 = 'Verification & backup'
}

$overviewLines = @('## 📋 Tasks Overview', '', '| ID | Description | Current Status |', '|----|-------------|----------------|')
foreach ($entry in $progress.tasks) {
    $overviewLines += "| $($entry.task_id) | $($descMap[$entry.task_id]) | $($entry.status) |"
}
$overviewSection = @"
<!--- TASKS-OVERVIEW-START --->
$($overviewLines -join "`n")
<!--- TASKS-OVERVIEW-END   --->
"@

$readmeContent = Get-Content $readmePath -Raw

if ($readmeContent -match '<!--- STATUS-BADGES-START --->') {
    $readmeContent = $readmeContent -replace '(?s)<!--- STATUS-BADGES-START --->.*?<!--- STATUS-BADGES-END   --->', $badgeSection
} else {
    $readmeContent = "$badgeSection`n`n$readmeContent"
}

if ($readmeContent -match '<!--- TASKS-OVERVIEW-START --->') {
    $readmeContent = $readmeContent -replace '(?s)<!--- TASKS-OVERVIEW-START --->.*?<!--- TASKS-OVERVIEW-END   --->', $overviewSection
} else {
    $readmeContent = "$readmeContent`n`n$overviewSection"
}

Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8

Set-Status -Id 7 -State done -Note "README markers refreshed."
Write-Host "README refreshed with status badges and overview."
