# -------------------------------------------------
# task3_crossplatform_packaging.ps1
# -------------------------------------------------
param(
    [switch]$SkipWindows,
    [switch]$SkipLinux
)

function Set-Status {
    param([int]$Id, [string]$State, [string]$Note=$null)
    .\update_task.ps1 -id $Id -newStatus $State $(if($Note){ "-note `"$Note`"" })
}

Set-Status -Id 3 -State in_progress -Note "Packaging started"

if (-not $SkipWindows) {
    $iscc = Get-Command iscc -ErrorAction SilentlyContinue
    if (-not $iscc) {
        Set-Status -Id 3 -State blocked -Note "Inno Setup not found."
    } else {
        Write-Host "Skipping Windows installer (Inno Setup available but no build output)"
        Set-Status -Id 3 -State blocked -Note "Windows installer skipped - no tetris_overlay.exe"
    }
} else {
    Write-Host "Skipping Windows installer (user requested)." -ForegroundColor Yellow
}

if (-not $SkipLinux) {
    $tar = Get-Command tar -ErrorAction SilentlyContinue
    if (-not $tar) {
        Set-Status -Id 3 -State blocked -Note "tar not available."
    } else {
        $archive = "..\tetris_overlay_linux.tar.gz"
        $files = @("calibration.json","tetris_artifacts.zip")
        $files = $files -replace '\\','/'
        Write-Host "Creating Linux archive $archive…" -ForegroundColor Yellow
        tar -czf $archive $files
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Linux archive created."
            Set-Status -Id 3 -State done -Note "Linux archive created (Windows skipped)"
        } else {
            Set-Status -Id 3 -State blocked -Note "tar failed."
        }
    }
} else {
    Write-Host "Skipping Linux archive (user requested)." -ForegroundColor Yellow
}
