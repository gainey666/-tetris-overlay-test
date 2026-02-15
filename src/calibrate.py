import json, cv2, sys
from pathlib import Path
CFG = Path("config.json")

def calibrate():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): raise RuntimeError("camera")
    pts = []
    def cb(ev,x,y,fl,pr):
        if ev==cv2.EVENT_LBUTTONDOWN:
            pts.append((x,y))
            if len(pts)==2: cv2.destroyAllWindows()
    cv2.namedWindow("Cal")
    cv2.setMouseCallback("Cal",cb)
    while True:
        ret,frm=cap.read()
        if not ret: break
        cv2.imshow("Cal",frm)
        if cv2.waitKey(1)==27: break
        if len(pts)==2: break
    cap.release(); cv2.destroyAllWindows()
    if len(pts)!=2: return
    CFG.write_text(json.dumps({"roi":{"tl":pts[0],"br":pts[1]}},indent=2))
    print("ROI saved")
if __name__=="__main__": calibrate()
