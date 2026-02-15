# -------------------------------------------------
# task6_user_config_ui.ps1
# -------------------------------------------------
function Set-Status {
    param([int]$Id, [string]$State, [string]$Note=$null)
    .\update_task.ps1 -id $Id -newStatus $State $(if($Note){ "-note `"$Note`"" })
}

Set-Status -Id 6 -State in_progress -Note "Building ImGui config UI"

$required = @('imgui','glfw')
foreach ($pkg in $required) {
    python -c "import $pkg" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing $pkg via pip..."
        python -m pip install $pkg
        if ($LASTEXITCODE -ne 0) {
            Set-Status -Id 6 -State blocked -Note "$pkg installation failed."
            return
        }
    }
}

$uiScript = @"
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw, json, pathlib, os

cfg_path = pathlib.Path('tetris_config.json')
if cfg_path.is_file():
    cfg = json.loads(cfg_path.read_text())
else:
    cfg = {'use_cnn': False, 'overlay_opacity': 200}
    cfg_path.write_text(json.dumps(cfg, indent=2))

def save_cfg():
    cfg_path.write_text(json.dumps(cfg, indent=2))

def main():
    if not glfw.init():
        print('GLFW init failed')
        return
    win = glfw.create_window(400, 200, "Overlay Config", None, None)
    glfw.make_context_current(win)
    impl = GlfwRenderer(win)

    while not glfw.window_should_close(win):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        imgui.begin("Overlay Settings", True)

        changed, cfg['use_cnn'] = imgui.checkbox('Enable CNN backend', cfg['use_cnn'])
        if changed: save_cfg()

        changed, cfg['overlay_opacity'] = imgui.slider_int('Overlay opacity', cfg['overlay_opacity'], 0, 255)
        if changed: save_cfg()

        if imgui.button('Run calibration'):
            os.system('powershell -NoProfile -ExecutionPolicy Bypass -File .\\calibrate.ps1')

        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(win)

    impl.shutdown()
    glfw.terminate()

if __name__ == '__main__':
    main()
"@

$uiPath = Join-Path $PSScriptRoot "overlay_config_ui.py"
Set-Content -Path $uiPath -Value $uiScript -Encoding UTF8

Write-Host "Launching ImGui UI - close the window when finished." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList $uiPath -WindowStyle Normal

Set-Status -Id 6 -State done -Note "ImGui UI launched."
Write-Host "UI script started."
