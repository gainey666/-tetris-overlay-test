from ultralytics import YOLO
import numpy as np
from PIL import Image
import logging

model = YOLO("runs/detect/train/weights/best.pt")

def infer_board_boxes(frame: Image):
    arr = np.array(frame.convert("RGB"))[:, :, ::-1]
    results = model(arr, verbose=False)[0]
    left_box, right_box = None, None
    for box in results.boxes:
        cls = int(box.cls)
        if cls == 0:
            left_box = box.xyxy[0].tolist()
        elif cls == 1:
            right_box = box.xyxy[0].tolist()
    logging.debug(f"Inference results – left:{left_box} right:{right_box}")
    return left_box, right_box
