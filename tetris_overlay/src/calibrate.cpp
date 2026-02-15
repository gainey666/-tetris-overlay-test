#include "calibrate.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <wingdi.h>

Calibrator* Calibrator::s_instance = nullptr;

Calibrator::Calibrator() 
    : m_hwnd(nullptr), m_clickCount(0) {
    s_instance = this;
    m_clickPoints[0] = {0, 0};
    m_clickPoints[1] = {0, 0};
}

Calibrator::~Calibrator() {
    if (s_instance == this) {
        s_instance = nullptr;
    }
}

bool Calibrator::run() {
    std::cout << "Starting calibration..." << std::endl;
    std::cout << "Click the top-left corner of the Tetris board, then the bottom-right corner." << std::endl;

    if (!createWindow()) {
        std::cerr << "Failed to create calibration window" << std::endl;
        return false;
    }

    // Capture and display screen
    captureAndDisplay();

    // Run message loop
    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
        
        if (m_clickCount >= 2) {
            break;
        }
    }

    // Calculate ROI from click points
    if (m_clickCount == 2) {
        int x1 = std::min(m_clickPoints[0].x, m_clickPoints[1].x);
        int y1 = std::min(m_clickPoints[0].y, m_clickPoints[1].y);
        int x2 = std::max(m_clickPoints[0].x, m_clickPoints[1].x);
        int y2 = std::max(m_clickPoints[0].y, m_clickPoints[1].y);
        
        m_roi = cv::Rect(x1, y1, x2 - x1, y2 - y1);
        
        std::cout << "Calibration complete. ROI: " << m_roi.x << "," << m_roi.y 
                  << " size: " << m_roi.width << "x" << m_roi.height << std::endl;
        
        // Save to file
        if (saveToFile("calibration.json")) {
            std::cout << "Calibration saved to calibration.json" << std::endl;
        } else {
            std::cerr << "Failed to save calibration" << std::endl;
        }
        
        DestroyWindow(m_hwnd);
        return true;
    }

    DestroyWindow(m_hwnd);
    return false;
}

bool Calibrator::createWindow() {
    // Register window class
    WNDCLASSEX wc = {};
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.hCursor = LoadCursor(nullptr, IDC_CROSS);
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
    wc.lpszClassName = L"TetrisCalibrator";

    if (!RegisterClassEx(&wc)) {
        std::cerr << "Failed to register calibration window class" << std::endl;
        return false;
    }

    // Get desktop dimensions
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);

    // Create window
    m_hwnd = CreateWindowEx(
        0,
        L"TetrisCalibrator",
        L"Tetris Board Calibration",
        WS_OVERLAPPEDWINDOW,
        100, 100, screenWidth - 200, screenHeight - 200,
        nullptr, nullptr, GetModuleHandle(nullptr), nullptr
    );

    if (!m_hwnd) {
        std::cerr << "Failed to create calibration window" << std::endl;
        return false;
    }

    ShowWindow(m_hwnd, SW_SHOW);
    UpdateWindow(m_hwnd);

    return true;
}

void Calibrator::captureAndDisplay() {
    // Get desktop dimensions
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);

    // Create device context for screen
    HDC hdcScreen = GetDC(nullptr);
    HDC hdcMem = CreateCompatibleDC(hdcScreen);

    // Create bitmap
    HBITMAP hbmScreen = CreateCompatibleBitmap(hdcScreen, screenWidth, screenHeight);
    HBITMAP hbmOld = (HBITMAP)SelectObject(hdcMem, hbmScreen);

    // Copy screen
    BitBlt(hdcMem, 0, 0, screenWidth, screenHeight, hdcScreen, 0, 0, SRCCOPY);

    // Convert to OpenCV Mat
    BITMAPINFOHEADER bi = {};
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = screenWidth;
    bi.biHeight = -screenHeight; // Negative for top-down bitmap
    bi.biPlanes = 1;
    bi.biBitCount = 24;
    bi.biCompression = BI_RGB;

    m_screenCapture.create(screenHeight, screenWidth, CV_8UC3);
    GetDIBits(hdcMem, hbmScreen, 0, screenHeight, m_screenCapture.data, 
              (BITMAPINFO*)&bi, DIB_RGB_COLORS);

    // Cleanup
    SelectObject(hdcMem, hbmOld);
    DeleteObject(hbmScreen);
    DeleteDC(hdcMem);
    ReleaseDC(nullptr, hdcScreen);

    // Convert BGR to RGB for display
    cv::cvtColor(m_screenCapture, m_screenCapture, cv::COLOR_BGR2RGB);

    // Trigger window redraw
    InvalidateRect(m_hwnd, nullptr, TRUE);
}

void Calibrator::drawOverlay() {
    if (m_screenCapture.empty()) return;

    // Get window DC
    HDC hdc = GetDC(m_hwnd);
    
    // Create compatible DC and bitmap
    HDC hdcMem = CreateCompatibleDC(hdc);
    HBITMAP hBitmap = CreateCompatibleBitmap(hdc, m_screenCapture.cols, m_screenCapture.rows);
    HBITMAP hOldBitmap = (HBITMAP)SelectObject(hdcMem, hBitmap);

    // Set bitmap info
    BITMAPINFO bmi = {};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = m_screenCapture.cols;
    bmi.bmiHeader.biHeight = -m_screenCapture.rows;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 24;
    bmi.bmiHeader.biCompression = BI_RGB;

    // Copy OpenCV image to bitmap
    SetDIBits(hdcMem, hBitmap, 0, m_screenCapture.rows, m_screenCapture.data, 
              &bmi, DIB_RGB_COLORS);

    // Draw to window
    GetClientRect(m_hwnd, &bmi.bmiHeader);
    StretchBlt(hdc, 0, 0, bmi.bmiHeader.biWidth, bmi.bmiHeader.biHeight,
               hdcMem, 0, 0, m_screenCapture.cols, m_screenCapture.rows, SRCCOPY);

    // Draw click points and selection rectangle
    HPEN hPen = CreatePen(PS_SOLID, 2, RGB(255, 0, 0));
    HPEN hOldPen = (HPEN)SelectObject(hdc, hPen);

    for (int i = 0; i < m_clickCount; ++i) {
        // Draw crosshair at click point
        int x = m_clickPoints[i].x;
        int y = m_clickPoints[i].y;
        
        MoveToEx(hdc, x - 10, y, nullptr);
        LineTo(hdc, x + 10, y);
        MoveToEx(hdc, x, y - 10, nullptr);
        LineTo(hdc, x, y + 10);
    }

    // Draw selection rectangle if we have two points
    if (m_clickCount == 2) {
        int x1 = m_clickPoints[0].x;
        int y1 = m_clickPoints[0].y;
        int x2 = m_clickPoints[1].x;
        int y2 = m_clickPoints[1].y;
        
        Rectangle(hdc, x1, y1, x2, y2);
    }

    // Cleanup
    SelectObject(hdc, hOldPen);
    DeleteObject(hPen);
    SelectObject(hdcMem, hOldBitmap);
    DeleteObject(hBitmap);
    DeleteDC(hdcMem);
    ReleaseDC(m_hwnd, hdc);
}

void Calibrator::handleMouseClick(int x, int y) {
    if (m_clickCount < 2) {
        m_clickPoints[m_clickCount] = {x, y};
        m_clickCount++;
        
        std::cout << "Click " << m_clickCount << ": (" << x << ", " << y << ")" << std::endl;
        
        // Redraw to show click point
        drawOverlay();
        
        if (m_clickCount >= 2) {
            PostQuitMessage(0);
        }
    }
}

LRESULT CALLBACK Calibrator::WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;

    case WM_PAINT:
        if (s_instance) {
            s_instance->drawOverlay();
        }
        ValidateRect(hwnd, nullptr);
        return 0;

    case WM_LBUTTONDOWN:
        if (s_instance) {
            int x = LOWORD(lParam);
            int y = HIWORD(lParam);
            s_instance->handleMouseClick(x, y);
        }
        return 0;

    case WM_KEYDOWN:
        if (wParam == VK_ESCAPE) {
            DestroyWindow(hwnd);
        }
        return 0;

    default:
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
}

bool Calibrator::loadFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        return false;
    }

    try {
        std::string content((std::istreambuf_iterator<char>(file)),
                          std::istreambuf_iterator<char>());
        
        // Simple JSON parsing (for this specific format)
        size_t xPos = content.find("\"x\":");
        size_t yPos = content.find("\"y\":");
        size_t wPos = content.find("\"w\":");
        size_t hPos = content.find("\"h\":");
        
        if (xPos != std::string::npos && yPos != std::string::npos && 
            wPos != std::string::npos && hPos != std::string::npos) {
            m_roi.x = std::stoi(content.substr(xPos + 4));
            m_roi.y = std::stoi(content.substr(yPos + 4));
            m_roi.width = std::stoi(content.substr(wPos + 4));
            m_roi.height = std::stoi(content.substr(hPos + 4));
            return true;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error parsing calibration file: " << e.what() << std::endl;
    }
    
    return false;
}

bool Calibrator::saveToFile(const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }

    file << "{\"x\":" << m_roi.x << ",\"y\":" << m_roi.y 
         << ",\"w\":" << m_roi.width << ",\"h\":" << m_roi.height << "}";
    
    return file.good();
}
