"""Configuration and calibration data-classes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CONFIG_FILE = Path("config.json")
CALIB_FILE = Path("calibration.json")


@dataclass
class AppConfig:
    """High-level runtime configuration."""

    video_source: int = 0
    target_fps: int = 30
    board_width: int = 20
    board_height: int = 10
    # ---- NEW DXGI SETTINGS -------------------------------------------------
    use_dxgi: bool = True  # auto‑detect, can be forced off
    dxgi_target_fps: int = 60  # desired capture FPS
    dxgi_pool_size: int = 3  # number of pre‑allocated frames
    use_overlay: bool = False  # console by default
    roi: dict | None = None  # {"tl":[0,0],"br":[w,h]} – full frame by default
    # -------------------------------------------------------------------------

    @classmethod
    def load(cls) -> "AppConfig":
        if not CONFIG_FILE.is_file():
            return cls()
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Filter out unknown fields that aren't part of AppConfig
        import inspect

        app_config_fields = {
            name for name, _ in inspect.signature(cls).parameters.items()
        }
        filtered_data = {k: v for k, v in data.items() if k in app_config_fields}

        return cls(**filtered_data)

    def save(self) -> None:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)


@dataclass
class CalibrationConfig:
    """Camera calibration parameters."""

    camera_matrix: list[list[float]] | None = None
    distortion_coeffs: list[float] | None = None

    @classmethod
    def load(cls) -> "CalibrationConfig":
        if not CALIB_FILE.is_file():
            return cls()
        with CALIB_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def save(self) -> None:
        with CALIB_FILE.open("w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
