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
