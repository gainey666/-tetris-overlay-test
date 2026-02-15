# ci_pipeline_setup.ps1 – create .github/workflows/ci.yml
$ciPath = Join-Path -Path $PSScriptRoot -ChildPath '.github\workflows'
New-Item -ItemType Directory -Force -Path $ciPath | Out-Null

$ciYml = @"
name: CI Build and Benchmark

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-2022
    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Setup vcpkg
      uses: lukka/run-vcpkg@v10
      with:
        vcpkgGitCommitId: 'latest'
        vcpkgTriplet: 'x64-windows'

    - name: Configure CMake
      run: |
        cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"

    - name: Build
      run: |
        cmake --build build --config Release -- /m

    - name: Run Benchmark
      run: |
        cd build/Release
        ./tetris_overlay.exe > benchmark.txt 2>&1 || true

    - name: Package Artifacts
      run: |
        mkdir artifacts
        copy build/Release/tetris_overlay.exe artifacts/
        copy build/Release/benchmark.txt artifacts/
        copy calibration.json artifacts/ || echo "No calibration.json found"
        Compress-Archive -Path artifacts/* -DestinationPath tetris_artifacts.zip

    - name: Upload Artifacts
      uses: actions/upload-artifact@v4
      with:
        name: tetris-artifacts
        path: tetris_artifacts.zip
"@

$ciYml | Out-File -FilePath (Join-Path $ciPath "ci.yml") -Encoding UTF8
Write-Host "CI workflow created at .github/workflows/ci.yml" -ForegroundColor Green
