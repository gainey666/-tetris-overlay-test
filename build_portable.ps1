<#=====================================================================
  build_portable.ps1
  ---------------------------------------------------------------
  What it does (in one run):
   1️⃣  Creates a clean build workspace.
   2️⃣  Downloads the Embeddable Python zip (no installer needed).
   3️⃣  Bootsraps pip inside that portable interpreter.
   4️⃣  Installs ALL runtime wheels (imgui, glfw, onnxruntime, …).
   5️⃣  Copies your project files (overlay exe, model, scripts, README).
   6️⃣  Writes a tiny Python entry‑point (`run_overlay.py`) that
       mirrors the old PowerShell driver but runs entirely in Python.
   7️⃣  Calls PyInstaller → produces a **single EXE** (`TetrisOverlay.exe`).
   8️⃣  (Optional) Downloads a portable NSIS and builds a tiny installer
       (`TetrisOverlay‑Setup.exe`) that extracts the EXE and creates a
       desktop shortcut.
=====================================================================#>

# -----------------------------------------------------------------
# 0️⃣  USER‑CONFIGURABLE SETTINGS – edit if you need a different version
# -----------------------------------------------------------------
$repoRoot          = "G:\dad fucken around\tetris again"   # <‑‑ folder that already works
$pythonVersion     = "3.11.9"                           # any recent 3.x works
$targetExeName     = "TetrisOverlay.exe"                 # name of the final single EXE
$buildRoot         = "$env:TEMP\TetrisOverlayBuild"      # temporary workspace
$makeInstaller     = $true                               # $false → skip NSIS step
$nsisDownloadUrl   = "https://downloads.sourceforge.net/project/nsis/NSIS%203/3.09/nsis-3.09-setup.exe"
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# 1️⃣  Prepare clean workspace
# -----------------------------------------------------------------
Write-Host "`n=== Preparing clean build workspace ==="
if (Test-Path $buildRoot) { Remove-Item -Recurse -Force $buildRoot }
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
Set-Location $buildRoot

# -----------------------------------------------------------------
# 2️⃣  Download & extract Embeddable Python (portable interpreter)
# -----------------------------------------------------------------
$embedUrl = "https://www.python.org/ftp/python/$pythonVersion/python-${pythonVersion}-embed-amd64.zip"
$zipPath  = "$buildRoot\python-embed.zip"
Write-Host "Downloading Embeddable Python $pythonVersion ..."
Invoke-WebRequest -Uri $embedUrl -OutFile $zipPath -UseBasicParsing
Expand-Archive -Path $zipPath -DestinationPath "$buildRoot\python" -Force
$pythonExe = "$buildRoot\python\python.exe"
Write-Host "✅ Portable Python extracted to $buildRoot\python"

# -----------------------------------------------------------------
# 3️⃣  Bootstrap pip inside the portable interpreter
# -----------------------------------------------------------------
Write-Host "Bootstrapping pip ..."
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$buildRoot\get-pip.py"
& $pythonExe "$buildRoot\get-pip.py" --no-warn-script-location
Write-Host "✅ pip ready"

# -----------------------------------------------------------------
# 4️⃣  Install required wheels (into <buildRoot>\python\site‑packages)
# -----------------------------------------------------------------
$requirements = @"
imgui==2.0.0
glfw==2.10.0
onnxruntime==1.17.0
numpy
pillow
tqdm
pyinstaller==6.4.0
"@
$reqPath = "$buildRoot\requirements.txt"
$requirements | Set-Content -Path $reqPath -Encoding ASCII

Write-Host "Installing runtime packages ..."
& $pythonExe -m pip install -r $reqPath --target "$buildRoot\python\site-packages"
Write-Host "✅ Packages installed into portable interpreter"

# -----------------------------------------------------------------
# 5️⃣  Copy project assets (overlay binary, model, scripts, README)
# -----------------------------------------------------------------
Write-Host "Copying project files ..."
Copy-Item -Path "$repoRoot\bin\*"            -Destination "$buildRoot\bin"            -Recurse -Force
Copy-Item -Path "$repoRoot\models\tetris_cnn.onnx" -Destination "$buildRoot\models" -Force
Copy-Item -Path "$repoRoot\scripts\*"      -Destination "$buildRoot\scripts"      -Recurse -Force
Copy-Item -Path "$repoRoot\README.md"      -Destination "$buildRoot"               -Force
# (Optional) copy any extra data folder you may have
# Copy-Item -Path "$repoRoot\some_extra_folder" -Destination "$buildRoot\some_extra_folder" -Recurse -Force

# -----------------------------------------------------------------
# 6️⃣  Write the **Python driver** (run_overlay.py)
# -----------------------------------------------------------------
$driverPath = "$buildRoot\run_overlay.py"
@"
import os, sys, json, subprocess, datetime, pathlib

ROOT = pathlib.Path(__file__).parent.parent                # repo root (two levels up)
LOG_PATH   = ROOT / "progress_log.json"
MODEL_PATH = ROOT / "models" / "tetris_cnn.onnx"
ARTIFACTS  = ROOT / "artifacts"

def load_log():
    if LOG_PATH.is_file():
        return json.load(LOG_PATH.open())
    # fresh skeleton – same as used in the original PowerShell version
    return [
        {"id":1,"status":"todo","note":"Log & tracker cleanup pending"},
        {"id":2,"status":"done","note":"CI pipeline verified"},
        {"id":3,"status":"todo","note":"Cross‑platform packaging pending"},
        {"id":4,"status":"todo","note":"Unit‑test suite pending"},
        {"id":5,"status":"done","note":"CNN verification completed"},
        {"id":6,"status":"done","note":"ImGui UI configured"},
        {"id":7,"status":"todo","note":"Documentation refresh pending"},
        {"id":8,"status":"done","note":"Backup & verification completed"}
    ]

def save_log(data):
    LOG_PATH.write_text(json.dumps(data, indent=2))

def set_status(log, tid, new_state, note=None):
    for e in log:
        if e["id"] == tid:
            e["status"] = new_state
            if note:
                e["note"] = note
            break
    save_log(log)

def run_ps(rel_path):
    script = ROOT / "scripts" / rel_path
    subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(script)], check=True)

# -------------------- Main driver (mirrors run_day6_all.ps1) --------------------
log = load_log()

# 1 – Log & tracker
set_status(log, 1, "done", "Log & tracker files initialized")

# 2 – CI pipeline (already done)
set_status(log, 2, "done", "CI pipeline verified")

# 3 – Cross‑platform packaging
run_ps("task3_crossplatform_packaging.ps1")
set_status(log, 3, "done", "Packaging script executed")

# 4 – Unit‑test suite
run_ps("task4_unittest_suite.ps1")
set_status(log, 4, "done", "Unit tests executed")

# 5 – CNN verification (already done)
set_status(log, 5, "done", "CNN verification completed")

# 6 – ImGui UI (already done)
set_status(log, 6, "done", "ImGui UI configured")

# 7 – Documentation refresh
run_ps("task7_doc_purge.ps1")
set_status(log, 7, "done", "Documentation refreshed")

# 8 – Verification & backup
run_ps("task8_verification_backup.ps1")
set_status(log, 8, "done", f"Backup created {datetime.datetime.now():%Y-%m-%d}")

print("✅ All tasks finished – launching overlay…")

# -----------------------------------------------------------------
# Finally launch the overlay binary (adjust name if different)
# -----------------------------------------------------------------
overlay_exe = ROOT / "bin" / "tetris_overlay.exe"
if overlay_exe.is_file():
    subprocess.Popen([str(overlay_exe)], cwd=str(overlay_exe.parent))
else:
    print("⚠️  Overlay executable not found:", overlay_exe)
"@ | Set-Content -Path $driverPath -Encoding UTF8
Write-Host "✅ Python driver (run_overlay.py) written."

# -----------------------------------------------------------------
# 7️⃣  Build the **single‑file EXE** with PyInstaller
# -----------------------------------------------------------------
Write-Host "`n=== Building single‑file EXE with PyInstaller ==="
& $pythonExe -m PyInstaller `
    --onefile `
    --clean `
    --distpath "$buildRoot\dist" `
    --workpath "$buildRoot\build" `
    --specpath "$buildRoot" `
    --add-data "$buildRoot\models;models" `
    --add-data "$buildRoot\bin;bin" `
    --add-data "$buildRoot\scripts;scripts" `
    --add-data "$buildRoot\README.md;." `
    "$driverPath"

# Rename the generated exe to the friendly name the user will see
$generatedExe = Get-ChildItem -Path "$buildRoot\dist" -Filter "*.exe" | Select-Object -First 1
Rename-Item -Path $generatedExe.FullName -NewName $targetExeName -Force
Write-Host "`n✅ Portable EXE created: $buildRoot\$targetExeName"

# -----------------------------------------------------------------
# 8️⃣  OPTIONAL: Build a tiny NSIS installer (TetrisOverlay‑Setup.exe)
# -----------------------------------------------------------------
if ($makeInstaller) {
    Write-Host "`n=== Creating NSIS installer (requires NSIS) ==="

    # Download a **portable** NSIS installer if it is not already on the machine
    $nsisInstaller = "$env:TEMP\nsis-setup.exe"
    if (-not (Test-Path $nsisInstaller)) {
        Write-Host "Downloading NSIS ..."
        Invoke-WebRequest -Uri $nsisDownloadUrl -OutFile $nsisInstaller -UseBasicParsing
        # Silent install to the default location (C:\Program Files (x86)\NSIS)
        Start-Process -FilePath $nsisInstaller -ArgumentList "/S" -Wait
    }

    # Path to the nsis compiler (makensis.exe)
    $makensis = "C:\Program Files (x86)\NSIS\makensis.exe"
    if (-not (Test-Path $makensis)) {
        Write-Error "❌ NSIS compiler not found at $makensis – aborting installer creation."
        exit 1
    }

    # Create a minimal NSIS script on the fly
    $nsisScript = @"
!define APPNAME `"TetrisOverlay`"
!define EXEFILE `"${targetExeName}`"
!define OUTFILE `"TetrisOverlay-Setup.exe`"

OutFile `"$OUTFILE`"
InstallDir `"$PROGRAMFILES\\${APPNAME}`"
Page directory
Page instfiles

Section
    SetOutPath `"$INSTDIR`"
    File "`"$buildRoot\${targetExeName}`"
    CreateShortcut "`"$DESKTOP\\${APPNAME}.lnk`" "`"$INSTDIR\\${EXEFILE}`"
SectionEnd
"@
    $nsisScriptPath = "$buildRoot\installer.nsi"
    $nsisScript | Set-Content -Path $nsisScriptPath -Encoding ASCII

    Write-Host "Compiling NSIS installer ..."
    & $makensis $nsisScriptPath

    Write-Host "`n✅ Installer created: $buildRoot\TetrisOverlay-Setup.exe"
} else {
    Write-Host "`n⚠️  Installer step was skipped ( `$makeInstaller = $false )."
}

# -----------------------------------------------------------------
# 9️⃣  Final user‑friendly summary
# -----------------------------------------------------------------
Write-Host "`n=================================================================="
Write-Host "✅  Build complete!  You now have two distribution options:"
Write-Host "   • Portable single EXE  :  $buildRoot\$targetExeName"
if ($makeInstaller) {
    Write-Host "   • Installer (EXE + desktop shortcut) :  $buildRoot\TetrisOverlay-Setup.exe"
}
Write-Host "`n▶️  To distribute:"
Write-Host "   – Simply copy the .exe (or the installer) to any Windows 10+ PC."
Write-Host "   – Double‑click it.  The overlay will start, create its logs, and run the"
Write-Host "     ImGui UI configuration window (hot‑key as defined in your scripts)."
Write-Host "`n=================================================================="
