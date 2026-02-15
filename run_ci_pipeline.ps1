# run_ci_pipeline.ps1 – autonomous CI pipeline execution (10+ min AFK-ready)
# ---------------------------------------------------------------------
# 0️⃣ Helper to update task status (calls update_task.ps1)
function Set-TaskStatus {
 param(
 [int]$Id,
 [ValidateSet('todo','in_progress','done','blocked')]
 [string]$Status,
 [string]$Note = $null,
 [bool]$Fatal = $false
 )
 $cmd = ".\update_task.ps1 -id $Id -newStatus $Status"
 if ($Note) { $cmd += " -note '$Note'" }
 if ($Fatal) { $cmd += " -fatal" }
 Write-Host "[TASK $Id] -> $Status" -ForegroundColor Cyan
 Invoke-Expression $cmd
}

# ---------------------------------------------------------------------
# 1️⃣ Mark Task 2 as IN_PROGRESS
Set-TaskStatus -Id 2 -Status in_progress

# ---------------------------------------------------------------------
# 2️⃣ Generate the GitHub-Actions workflow file (if not present)
if (-not (Test-Path '.github\workflows\ci.yml')) {
 Write-Host "Generating CI workflow..." -ForegroundColor Yellow
 .\ci_pipeline_setup.ps1
}

# ---------------------------------------------------------------------
# 3️⃣ Run the workflow locally with act (if installed)
$actPath = Get-Command act -ErrorAction SilentlyContinue
if ($actPath) {
 Write-Host "Running CI locally with act..." -ForegroundColor Green
 # --verbose for more output, --job build to run only the build job
 act --job build --verbose
 $exitCode = $LASTEXITCODE
} else {
 Write-Warning "'act' not found - falling back to direct local build."
 # ---- Direct local build ----
 cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE="$(Resolve-Path .\vcpkg\scripts\buildsystems\vcpkg.cmake)"
 if ($LASTEXITCODE -ne 0) { $exitCode = 1 } else {
 cmake --build build --config Release -- /m
 $exitCode = $LASTEXITCODE
 }
 if ($exitCode -eq 0) {
 # Run benchmark for ~200ms and capture output
 Push-Location "build\Release"
 ./tetris_overlay.exe > benchmark.txt
 Pop-Location
 # Collect artifacts (same layout as the workflow)
 New-Item -ItemType Directory -Force -Path artifacts
 Copy-Item "build\Release\tetris_overlay.exe" artifacts\
 Copy-Item "build\Release\benchmark.txt" artifacts\
 Copy-Item "calibration.json" artifacts\ -ErrorAction SilentlyContinue
 Compress-Archive -Path artifacts\* -DestinationPath tetris_artifacts.zip
 }
}

# ---------------------------------------------------------------------
# 4️⃣ Update task status based on result
if ($exitCode -eq 0) {
 Set-TaskStatus -Id 2 -Status done -Note "CI pipeline completed successfully"
 Write-Host "CI pipeline completed! Check tetris_artifacts.zip" -ForegroundColor Green
} else {
 Set-TaskStatus -Id 2 -Status blocked -Note "CI failed with exit code $exitCode"
 Write-Host "CI pipeline failed. Check logs above." -ForegroundColor Red
}
