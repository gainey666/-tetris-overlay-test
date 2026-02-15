# ci_pipeline_setup_python.ps1
# -------------------------------------------------
# Creates .github/workflows/ci_python.yml
# -------------------------------------------------
$ciPath = Join-Path -Path $PSScriptRoot -ChildPath '.github\workflows'
New-Item -ItemType Directory -Force -Path $ciPath | Out-Null

$yaml = @'
name: Python CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    defaults:
      run:
        shell: pwsh

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run unit-tests (if any)
        run: |
          if (Test-Path .\tests) {
            python -m unittest discover -s tests
          } else {
            Write-Host "No tests folder - skipping."
          }

      - name: Run benchmark (200ms)
        run: |
          python src/main.py --benchmark 200 > benchmark.txt
          type benchmark.txt

      - name: Collect artifacts
        run: |
          mkdir artifacts
          copy /Y src\tetris_overlay.exe artifacts\ 2>$null
          copy /Y benchmark.txt artifacts\ 2>$null
          copy /Y calibration.json artifacts\ 2>$null
        shell: cmd

      - name: Archive artifacts
        uses: actions/upload-artifact@v3
        with:
          name: tetris-artifacts
          path: artifacts\
'@

$workflowFile = Join-Path $ciPath 'ci_python.yml'
Set-Content -Path $workflowFile -Value $yaml -Encoding UTF8
Write-Host "`n✅ Created .github\workflows\ci_python.yml`n"
