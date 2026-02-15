# run_ci_pipeline_python.ps1
# -------------------------------------------------
# 1️⃣ Mark Task 2 as IN_PROGRESS
# -------------------------------------------------
.\update_task.ps1 -id 2 -newStatus in_progress

# -------------------------------------------------
# 2️⃣ Ensure the Python workflow exists (generate if missing)
# -------------------------------------------------
$workflow = Join-Path $PSScriptRoot '.github\workflows\ci_python.yml'
if (-not (Test-Path $workflow)) {
    Write-Host "Python CI workflow not found - generating…" -ForegroundColor Yellow
    .\ci_pipeline_setup_python.ps1
}

# -------------------------------------------------
# 3️⃣ Run the workflow locally with `act` (if installed)
# -------------------------------------------------
$act = Get-Command act -ErrorAction SilentlyContinue
if ($act) {
    Write-Host "Running CI locally via act…" -ForegroundColor Green
    act --workflow ci_python.yml --verbose
    $exitCode = $LASTEXITCODE
} else {
    Write-Warning "'act' not installed - falling back to direct python execution."
    # -------- Direct execution fallback ----------
    python -m src.main --benchmark 200 > benchmark.txt
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        # Collect artifacts (same layout as the GH workflow)
        New-Item -ItemType Directory -Force -Path artifacts | Out-Null
        if (Test-Path src\tetris_overlay.exe) { Copy-Item src\tetris_overlay.exe artifacts\ }
        Copy-Item benchmark.txt artifacts\
        if (Test-Path calibration.json) { Copy-Item calibration.json artifacts\ }
        Compress-Archive -Path artifacts\* -DestinationPath tetris_artifacts.zip -Force
    }
}

# -------------------------------------------------
# 4️⃣ Update progress tracker based on result
# -------------------------------------------------
if ($exitCode -eq 0) {
    .\update_task.ps1 -id 2 -newStatus done -note "Python CI succeeded - artifacts in tetris_artifacts.zip"
    Write-Host "`n✅ Task 2 completed successfully`n" -ForegroundColor Green
} else {
    $msg = "Python CI failed (exit code $exitCode). Check the console log."
    .\update_task.ps1 -id 2 -newStatus blocked -note $msg -fatal $true
    Write-Error "`n❌ $msg`n"
    exit $exitCode
}
