@echo off
echo ========================================
echo       Tetris Overlay Launcher
echo ========================================
echo.
echo Starting Tetris Overlay...
echo.
echo Controls:
echo   F9        - Toggle overlay visibility
echo   F1        - Open settings dialog
echo   Ctrl+Alt+S - Open statistics dashboard
echo   Ctrl+Alt+C - Open ROI calibrator
echo   F2        - Toggle debug logging
echo   Esc       - Quit application
echo.
echo Make sure your Tetris game is running!
echo.
echo ========================================
echo.

TetrisOverlay.exe

if errorlevel 1 (
    echo.
    echo Error: TetrisOverlay.exe failed to start
    echo Press any key to exit...
    pause > nul
) else (
    echo.
    echo Tetris Overlay closed successfully
)
