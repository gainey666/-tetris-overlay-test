from capture import ScreenCapture
from dual_roi_manager import get_roi_pair
import logging

class DualScreenCapture:
    def __init__(self):
        rois = get_roi_pair()
        if len(rois) != 2:
            raise ValueError("Dual ROI required – exactly 2 regions expected")
        self.capturers = [ScreenCapture(r) for r in rois]

    def grab(self):
        left_img = self.capturers[0].grab()
        right_img = self.capturers[1].grab()
        logging.debug("Captured both boards")
        return left_img, right_img
