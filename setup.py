#!/usr/bin/env python3
"""
Setup script for Tetris Overlay.
"""

from setuptools import setup, find_packages

setup(
    name="tetris-overlay",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tetris-overlay=run_overlay_core:main",
        ],
    },
    author="Tetris Overlay Team",
    description="Real-time Tetris overlay with ghost pieces",
    long_description="A production-ready Tetris overlay that shows ghost pieces and provides real-time assistance.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.11",
)
