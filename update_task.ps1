# PowerShell helper to update task status
param(
    [int]$id,
    [ValidateSet('todo','in_progress','done','blocked')]
    [string]$newStatus,
    [string]$note = $null
)

$logPath = "progress_log.json"
$log = Get-Content $logPath -Raw | ConvertFrom-Json
$task = $log.tasks | Where-Object { $_.task_id -eq $id }

if ($newStatus -eq 'in_progress') {
    $task.started_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} elseif ($newStatus -eq 'done') {
    $task.finished_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}
$task.status = $newStatus
if ($note) {
    $task.note = $note
}
$log | ConvertTo-Json -Depth 5 | Set-Content $logPath -Encoding UTF8
Write-Host "Task $id updated to $newStatus"
