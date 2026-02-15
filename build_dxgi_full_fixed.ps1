Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------- Paths ----------
$repoRoot   = "g:\dad fucken around\tetris again"
$dxgiSrc    = Join-Path $repoRoot "cpp_binding\dxgi_capture"
$dxgiBuild  = Join-Path $dxgiSrc "build"
$agentsDir  = Join-Path $repoRoot "src\agents"
$vcpkgRoot  = Join-Path $repoRoot "vcpkg"
$vcpkgExe   = Join-Path $vcpkgRoot "vcpkg.exe"
# -------------------------------------------------------------
# Locate the VS Dev Cmd automatically (works for VS 2022, VS 2026, etc.)
# -------------------------------------------------------------
$vsInstallerPaths = @()
if ($env:ProgramFiles) {
    $vsInstallerPaths += (Join-Path $env:ProgramFiles "Microsoft Visual Studio\Installer\vswhere.exe")
}
if (${env:ProgramFiles(x86)}) {
    $vsInstallerPaths += (Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe")
}
$vswhere = $vsInstallerPaths | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $vswhere) {
    Throw "vswhere.exe not found - please install the Visual Studio Installer."
}

$vsInstall = & $vswhere -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
                         -property installationPath -format value
if ([string]::IsNullOrWhiteSpace($vsInstall)) {
    Throw "No Visual Studio instance with the C++ tools was found."
}

$vsDevCmd = Join-Path $vsInstall "Common7\Tools\VsDevCmd.bat"
if (-not (Test-Path $vsDevCmd)) {
    Throw "VsDevCmd.bat not found at $vsDevCmd"
}
Write-Host "Using VS Dev Cmd: $vsDevCmd"
$toolchain  = Join-Path $vcpkgRoot "scripts\buildsystems\vcpkg.cmake"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

# ---------- Install protobuf ----------
Write-Host "`n=== Installing protobuf via vcpkg ==="
if (-not (Test-Path $vcpkgExe)) { Throw "vcpkg not found at $vcpkgExe" }
& $vcpkgExe install protobuf --triplet x64-windows

# ---------- Clean previous build ----------
if (Test-Path $dxgiBuild) { Remove-Item $dxgiBuild -Recurse -Force }
New-Item -ItemType Directory -Path $dxgiBuild | Out-Null

# ---------- Build DXGI module in a single cmd block ----------
$batch = @"
@echo off
call `"$vsDevCmd`" -arch=x64
cd /d `"$dxgiSrc`"
cd build
cmake .. -G `"NMake Makefiles`" -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=`"$toolchain`" -DOpenCV_DIR=`"$repoRoot\vcpkg\installed\x64-windows\share\opencv`"
nmake
if exist *.pyd copy *.pyd `"$agentsDir\`"
"@
$tmpBat = [IO.Path]::GetTempFileName() + ".bat"
Set-Content -Path $tmpBat -Value $batch -Encoding ASCII
Write-Host "`n=== Building DXGI capture module ==="
cmd.exe /c $tmpBat
Remove-Item $tmpBat -Force

# ---------- Verify with the repo venv ----------
if (-not (Test-Path $venvPython)) { Throw "Venv python not found at $venvPython" }

$nativeBin    = Join-Path $repoRoot "vcpkg\installed\x64-windows\bin"
$debugBin     = Join-Path $repoRoot "vcpkg\installed\x64-windows\debug\bin"
$systemRoot   = $env:SystemRoot
$vsBuildTools = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
$vsDebugCRTBase = Join-Path $vsBuildTools "VC\Redist\MSVC"
$vsDebugCRTPath = $null
if (Test-Path $vsDebugCRTBase) {
    $vsDebugCRTVersion = Get-ChildItem -Path $vsDebugCRTBase -Directory |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if ($vsDebugCRTVersion) {
        $candidate = Join-Path $vsDebugCRTVersion.FullName "debug"
        if (Test-Path $candidate) { $vsDebugCRTPath = $candidate }
    }
}

$extraPaths = @()
if ($vsDebugCRTPath) { $extraPaths += $vsDebugCRTPath }
if (Test-Path $debugBin) { $extraPaths += $debugBin }
if (Test-Path $nativeBin) { $extraPaths += $nativeBin }
if ($systemRoot) { $extraPaths += (Join-Path $systemRoot "System32") }

foreach ($p in $extraPaths) {
    $env:PATH = "$p;$env:PATH"
}

Write-Host "Added required DLL dirs to PATH:"
foreach ($p in $extraPaths) { Write-Host "  $p" }

Write-Host "`n=== Verifying DXGI module with repo venv python ==="
& $venvPython -c @"
import os, sys
sys.path.insert(0, r'$repoRoot\src\agents')
os.add_dll_directory(r'$nativeBin')
import dxgi_capture
print('✅ Imported dxgi_capture')
g = dxgi_capture.FrameGrabber()
print('Init:', g.initialize())
"@
