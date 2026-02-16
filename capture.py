import logging

import mss  # type: ignore
from PIL import Image  # type: ignore

__all__ = ["ScreenCapture"]


class ScreenCapture:
    """Capture a rectangle (left, top, width, height) using mss only."""

    def __init__(self, rect):
        if len(rect) != 4:
            raise ValueError("rect must be (left, top, width, height)")
        left, top, width, height = rect
        self.region = {"left": left, "top": top, "width": width, "height": height}
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        right = left + width
        bottom = top + height
        mon_left = monitor["left"]
        mon_top = monitor["top"]
        mon_right = mon_left + monitor["width"]
        mon_bottom = mon_top + monitor["height"]
        if (
            right <= mon_left
            or bottom <= mon_top
            or left >= mon_right
            or top >= mon_bottom
        ):
            raise ValueError("Capture region lies completely off-screen")
        logging.info("ScreenCapture initialized with region %s", self.region)

    def grab(self):
        shot = self.sct.grab(self.region)
        return Image.frombytes("RGB", shot.size, shot.rgb)
