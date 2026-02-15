#pragma once

#include <opencv2/opencv.hpp>
#include <windows.h>
#include <string>

/// <summary>
/// Calibration utility for defining the Tetris board region
/// </summary>
class Calibrator {
public:
    Calibrator();
    ~Calibrator();

    /// <summary>
    /// Run the calibration process
    /// </summary>
    /// <returns>true on successful calibration, false on failure</returns>
    bool run();

    /// <summary>
    /// Load calibration from file
    /// </summary>
    /// <param name="filename">Path to calibration JSON file</param>
    /// <returns>true on success, false on failure</returns>
    bool loadFromFile(const std::string& filename);

    /// <summary>
    /// Save calibration to file
    /// </summary>
    /// <param name="filename">Path to calibration JSON file</param>
    /// <returns>true on success, false on failure</returns>
    bool saveToFile(const std::string& filename);

    /// <summary>
    /// Get the calibrated region of interest
    /// </summary>
    /// <returns>ROI rectangle</returns>
    cv::Rect getROI() const { return m_roi; }

private:
    /// <summary>
    /// Create calibration window
    /// </summary>
    /// <returns>true on success, false on failure</returns>
    bool createWindow();

    /// <summary>
    /// Window procedure for calibration window
    /// </summary>
    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

    /// <summary>
    /// Handle mouse clicks for calibration
    /// </summary>
    /// <param name="x">Mouse X coordinate</param>
    /// <param name="y">Mouse Y coordinate</param>
    void handleMouseClick(int x, int y);

    /// <summary>
    /// Draw calibration overlay on window
    /// </summary>
    void drawOverlay();

    /// <summary>
    /// Capture current screen and display in window
    /// </summary>
    void captureAndDisplay();

    HWND m_hwnd;                    ///< Calibration window handle
    cv::Mat m_screenCapture;        ///< Current screen capture
    cv::Rect m_roi;                 ///< Region of interest
    int m_clickCount;               ///< Number of clicks recorded
    POINT m_clickPoints[2];        ///< Click coordinates (TL and BR)
    
    static Calibrator* s_instance; ///< Static instance for window proc
};
