# -------------------------------------------------
# task4_unittest_suite.ps1
# -------------------------------------------------
function Set-Status {
    param([int]$Id, [string]$State, [string]$Note=$null)
    .\update_task.ps1 -id $Id -newStatus $State $(if($Note){ "-note `"$Note`"" })
}

Set-Status -Id 4 -State in_progress -Note "Generating & running unit tests"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$testsDir = Join-Path $repoRoot "tests"
if (-not (Test-Path $testsDir)) {
    $null = New-Item -ItemType Directory -Force -Path $testsDir
}

$artifactsDir = Join-Path $repoRoot "artifacts"
if (-not (Test-Path $artifactsDir)) {
    $null = New-Item -ItemType Directory -Force -Path $artifactsDir
}

$testFile = @"
import unittest
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parents[1] / 'src'))

class SmokeTest(unittest.TestCase):
    def test_imports(self):
        from src.agents.synthetic_capture_agent import SyntheticCaptureAgent
        from src.agents.board_extractor_agent import BoardExtractorAgent
        from src.agents.prediction_agent_mock_perfect import PredictionAgent

if __name__ == '__main__':
    unittest.main()
"@

Set-Content -Path (Join-Path $testsDir "test_smoke.py") -Value $testFile -Encoding UTF8

$results = Join-Path $artifactsDir "test_results.txt"
python -m unittest discover -s $testsDir -v > $results 2>&1
$exit = $LASTEXITCODE

if ($exit -eq 0) {
    Set-Status -Id 4 -State done -Note "All unit tests passed."
    Write-Host "Unit tests succeeded."
} else {
    Set-Status -Id 4 -State blocked -Note "Unit tests failed - see artifacts\test_results.txt."
    Write-Host "Unit tests failed."
}
