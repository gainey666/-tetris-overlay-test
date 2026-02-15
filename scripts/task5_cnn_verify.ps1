# -------------------------------------------------
# task5_cnn_verify.ps1
# -------------------------------------------------
function Set-Status {
    param([int]$Id, [string]$State, [string]$Note=$null)
    .\update_task.ps1 -id $Id -newStatus $State $(if($Note){ "-note `"$Note`"" })
}

Set-Status -Id 5 -State in_progress -Note "CNN verification started"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$artifactsDir = Join-Path $repoRoot "artifacts"
if (-not (Test-Path $artifactsDir)) {
    $null = New-Item -ItemType Directory -Force -Path $artifactsDir
}

$candidatePaths = @(
    (Join-Path $PSScriptRoot "..\tetris_cnn.onnx"),
    (Join-Path $PSScriptRoot "..\models\tetris_cnn.onnx")
)

$onnxPath = $null
foreach ($path in $candidatePaths) {
    if (Test-Path $path) {
        $onnxPath = Resolve-Path $path
        break
    }
}

if (-not $onnxPath) {
    Set-Status -Id 5 -State blocked -Note "tetris_cnn.onnx not found in repo root or models/."
    Write-Host "CNN model missing - task blocked."
    return
}

$py = @"
import onnxruntime as ort, numpy as np, time, json, pathlib
model = pathlib.Path(r'$onnxPath')
sess = ort.InferenceSession(str(model))
input_meta = sess.get_inputs()[0]
shape = []
for dim in input_meta.shape:
    if isinstance(dim, int) and dim > 0:
        shape.append(dim)
    else:
        shape.append(1)
dummy = np.zeros(tuple(shape), dtype=np.float32)
inp = {input_meta.name: dummy}
t0 = time.time()
_ = sess.run(None, inp)
lat = (time.time() - t0) * 1000.0
print(f'Inference latency: {lat:.2f} ms')
with open('cnn_latency.json','w') as f:
    json.dump({'latency_ms': lat, 'input_shape': shape}, f)
"@

$scriptPath = Join-Path $PSScriptRoot "cnn_verify.py"
Set-Content -Path $scriptPath -Value $py -Encoding UTF8

python $scriptPath
if ($LASTEXITCODE -ne 0) {
    Set-Status -Id 5 -State blocked -Note "CNN inference script failed."
    return
}

Copy-Item "cnn_latency.json" (Join-Path $artifactsDir "cnn_latency.json") -Force
Set-Status -Id 5 -State done -Note "CNN latency recorded."
Write-Host "CNN verification succeeded."
