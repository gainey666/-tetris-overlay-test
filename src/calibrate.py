import json, cv2, sys
from pathlib import Path

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


CFG = Path("config.json")


def calibrate():
@trace_calls('calibrate', 'calibrate.py', 23)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("camera")
    pts = []

    def cb(ev, x, y, fl, pr):
    @trace_calls('cb', 'calibrate.py', 29)
        if ev == cv2.EVENT_LBUTTONDOWN:
            pts.append((x, y))
            if len(pts) == 2:
                cv2.destroyAllWindows()

    cv2.namedWindow("Cal")
    cv2.setMouseCallback("Cal", cb)
    while True:
        ret, frm = cap.read()
        if not ret:
            break
        cv2.imshow("Cal", frm)
        if cv2.waitKey(1) == 27:
            break
        if len(pts) == 2:
            break
    cap.release()
    cv2.destroyAllWindows()
    if len(pts) != 2:
        return
    CFG.write_text(json.dumps({"roi": {"tl": pts[0], "br": pts[1]}}, indent=2))
    print("ROI saved")


if __name__ == "__main__":
    calibrate()
