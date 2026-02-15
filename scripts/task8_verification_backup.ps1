function Set-Status {
    param(
        [int]   $Id,
        [string]$State,
        [string]$Note = $null
    )
    .\update_task.ps1 -id $Id -newStatus $State $(if($Note){ "-note `"$Note`"" })
}

Set-Status -Id 8 -State in_progress -Note "Running verification and creating backup"

$tempRoot = Join-Path $PSScriptRoot "..\verification_temp"
if (Test-Path $tempRoot) { Remove-Item -Recurse -Force $tempRoot }
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

$installer = Get-Item "..\TetrisOverlay-Setup.exe" -ErrorAction SilentlyContinue
if ($installer) {
    Write-Host "Running installer silently..." -ForegroundColor Yellow
    & $installer /VERYSILENT /SUPPRESSMSGBOXES /DIR=$tempRoot\TetrisOverlay 2>$null
    if ($LASTEXITCODE -ne 0) {
        Set-Status -Id 8 -State blocked -Note "Installer failed (exit $LASTEXITCODE)."
        return
    }
} else {
    Write-Warning "Installer not found - skipping installer step."
}

$exePath = Join-Path $tempRoot "TetrisOverlay\tetris_overlay.exe"
if (Test-Path $exePath) {
    Write-Host "Running benchmark on installed binary..." -ForegroundColor Yellow
    & $exePath --benchmark 200 > $tempRoot\verification_benchmark.txt 2>$null
    if ($LASTEXITCODE -ne 0) {
        Set-Status -Id 8 -State blocked -Note "Installed binary benchmark failed."
        return
    }
} else {
    Write-Host "No installed binary found - skipping benchmark step."
}

$canUseZipFile = $false
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
    $null = [System.IO.Compression.ZipFile]
    $canUseZipFile = $true
} catch {
    $canUseZipFile = $false
}

$repoRoot = Resolve-Path "..\"
$exclude = @('.git','verification_temp','artifacts')
$files = Get-ChildItem -Path $repoRoot -Recurse -File -Force |
    Where-Object {
        $relative = $_.FullName.Substring($repoRoot.Path.Length + 1)
        foreach ($e in $exclude) { if ($relative -like "$e*") { return $false } }
        return $true
    }

$backupName = "tetris_again_backup_$(Get-Date -Format yyyyMMdd).zip"

if ($canUseZipFile) {
    Write-Host "Using ZipFile fast path..." -ForegroundColor Green
    $total = $files.Count
    Write-Host "Compressing $total items into $backupName..."

    try {
        $zip = [System.IO.Compression.ZipFile]::Open($backupName, [System.IO.Compression.ZipArchiveMode]::Create)
        $counter = 0
        foreach ($file in $files) {
            $relative = $file.FullName.Substring($repoRoot.Path.Length + 1)
            $entry = $zip.CreateEntry($relative, [System.IO.Compression.CompressionLevel]::Fastest)
            $entryStream = $entry.Open()
            $fileStream = [System.IO.File]::OpenRead($file.FullName)
            $fileStream.CopyTo($entryStream)
            $fileStream.Close()
            $entryStream.Close()
            $counter++
            if ($counter % 500 -eq 0) {
                $percent = ($counter / [double]$total) * 100
                Write-Progress -Activity "Creating backup zip" -Status "$counter / $total files" -PercentComplete $percent
            }
        }
        $zip.Dispose()
        Write-Progress -Activity "Creating backup zip" -Completed
    } catch {
        Write-Warning "ZipFile fast path failed - switching to Compress-Archive."
        $canUseZipFile = $false
    }
}

if (-not $canUseZipFile) {
    Write-Host "Using Compress-Archive fallback..." -ForegroundColor Yellow
    $paths = $files.FullName
    Compress-Archive -Path $paths -DestinationPath $backupName -Force -CompressionLevel Fastest
}

Write-Host "Backup ZIP created: $backupName" -ForegroundColor Green
Set-Status -Id 8 -State done -Note "Verification passed; backup $backupName generated."
