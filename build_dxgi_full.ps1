Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------- 1️⃣ Paths & constants ----------
$repoRoot   = "g:\dad fucken around\tetris again"
$dxgiSrc    = Join-Path $repoRoot "cpp_binding\dxgi_capture"
$dxgiBuild  = Join-Path $dxgiSrc "build"
$agentsDir  = Join-Path $repoRoot "src\agents"
$vcpkgRoot  = Join-Path $repoRoot "vcpkg"
$vcpkgExe   = Join-Path $vcpkgRoot "vcpkg.exe"
$vsDevCmd   = "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat"

# ---------- 2️⃣ Install protobuf (vcpkg) ----------
Write-Host "`n=== Installing protobuf via vcpkg ==="
if (-not (Test-Path $vcpkgExe)) {
    throw "vcpkg not found at $vcpkgExe"
}
& $vcpkgExe install protobuf --triplet x64-windows

# ---------- 3️⃣ Clean previous build ----------
if (Test-Path $dxgiBuild) {
    Remove-Item $dxgiBuild -Recurse -Force
}
New-Item -ItemType Directory -Path $dxgiBuild | Out-Null

# ---------- 4️⃣ Build DXGI module ----------
$batch = @"
@echo off
call `"$vsDevCmd`" -arch=x64
cd /d `"$dxgiSrc`"
cd build
cmake .. -G `"NMake Makefiles`" -DOpenCV_DIR=`"$repoRoot\vcpkg\installed\x64-windows\share\opencv4`" -DCMAKE_TOOLCHAIN_FILE=`"$repoRoot\vcpkg\scripts\buildsystems\vcpkg.cmake`"
nmake
if exist *.pyd copy *.pyd `"$agentsDir\`"
"@
$batchFile = [IO.Path]::ChangeExtension([IO.Path]::GetTempFileName(), '.bat')
Set-Content -Path $batchFile -Value $batch -Encoding ASCII
Write-Host "`n=== Building DXGI capture module ==="
cmd.exe /c $batchFile
Remove-Item $batchFile -Force

# ---------- 5️⃣ Verify the native module ----------
$generatedPyd = Get-ChildItem -Path $agentsDir -Filter "dxgi_capture*.pyd" -ErrorAction SilentlyContinue
if ($generatedPyd) {
    Write-Host "`n✅ DXGI .pyd successfully built: $($generatedPyd.Name)"
    python -c "import dxgi_capture; print('✅ Imported dxgi_capture'); grabber = dxgi_capture.FrameGrabber(); print('Initialize:', grabber.initialize())"
} else {
    Write-Host "`n❌ DXGI build failed – .pyd not found."
    Write-Host ("Check {0}\CMakeFiles\CMakeError.log for details." -f $dxgiBuild)
    exit 1
}
