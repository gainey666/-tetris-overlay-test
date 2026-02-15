#include "overlay_renderer.h"
#include <iostream>
#include <dwmapi.h>

OverlayRenderer* OverlayRenderer::s_instance = nullptr;

OverlayRenderer::OverlayRenderer(int width, int height, int cellSize)
    : m_hwnd(nullptr), m_width(width), m_height(height), m_cellSize(cellSize),
      m_posX(0), m_posY(0), m_hasPrediction(false) {
    s_instance = this;
}

OverlayRenderer::~OverlayRenderer() {
    if (s_instance == this) {
        s_instance = nullptr;
    }
}

bool OverlayRenderer::initialize() {
    if (!createWindow()) {
        std::cerr << "Failed to create overlay window" << std::endl;
        return false;
    }

    if (!initializeDirect2D()) {
        std::cerr << "Failed to initialize Direct2D" << std::endl;
        return false;
    }

    return true;
}

bool OverlayRenderer::createWindow() {
    // Register window class
    WNDCLASSEX wc = {};
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
    wc.lpszClassName = L"TetrisOverlay";

    if (!RegisterClassEx(&wc)) {
        std::cerr << "Failed to register window class" << std::endl;
        return false;
    }

    // Create layered window for transparency
    m_hwnd = CreateWindowEx(
        WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
        L"TetrisOverlay",
        L"Tetris Overlay",
        WS_POPUP,
        m_posX, m_posY, m_width, m_height,
        nullptr, nullptr, GetModuleHandle(nullptr), nullptr
    );

    if (!m_hwnd) {
        std::cerr << "Failed to create window" << std::endl;
        return false;
    }

    // Set window to be click-through and transparent
    SetLayeredWindowAttributes(m_hwnd, RGB(0, 0, 0), 200, LWA_COLORKEY);
    
    // Show window
    ShowWindow(m_hwnd, SW_SHOW);
    UpdateWindow(m_hwnd);

    return true;
}

bool OverlayRenderer::initializeDirect2D() {
    HRESULT hr;

    // Create Direct2D factory
    hr = D2D1CreateFactory(
        D2D1_FACTORY_TYPE_SINGLE_THREADED,
        &m_factory
    );
    if (FAILED(hr)) {
        std::cerr << "Failed to create Direct2D factory: " << std::hex << hr << std::endl;
        return false;
    }

    // Create render target
    D2D1_RENDER_TARGET_PROPERTIES props = D2D1::RenderTargetProperties(
        D2D1::RenderTargetType::Default,
        D2D1::PixelFormat(DXGI_FORMAT_B8G8R8A8_UNORM, D2D1_ALPHA_MODE_PREMULTIPLIED),
        0.0f, 0.0f
    );

    D2D1_SIZE_U size = D2D1::SizeU(m_width, m_height);
    hr = m_factory->CreateHwndRenderTarget(
        props,
        D2D1::HwndRenderTargetProperties(m_hwnd, size),
        &m_renderTarget
    );
    if (FAILED(hr)) {
        std::cerr << "Failed to create render target: " << std::hex << hr << std::endl;
        return false;
    }

    // Create brush for drawing
    hr = m_renderTarget->CreateSolidColorBrush(
        D2D1::ColorF(D2D1::ColorF::Yellow, 0.8f),
        &m_brush
    );
    if (FAILED(hr)) {
        std::cerr << "Failed to create brush: " << std::hex << hr << std::endl;
        return false;
    }

    return true;
}

void OverlayRenderer::drawGhost(const Prediction& pred) {
    m_currentPrediction = pred;
    m_hasPrediction = true;

    if (m_renderTarget) {
        // Clear and redraw
        m_renderTarget->BeginDraw();
        m_renderTarget->Clear(D2D1::ColorF(D2D1::ColorF::Black, 0.0f));

        if (m_hasPrediction) {
            // Get piece shape
            cv::Mat pieceShape = getPieceShape(m_currentPrediction.piece_type, m_currentPrediction.rotation);
            
            // Draw each block of the piece
            for (int y = 0; y < pieceShape.rows; ++y) {
                for (int x = 0; x < pieceShape.cols; ++x) {
                    if (pieceShape.at<uint8_t>(y, x)) {
                        int blockX = (m_currentPrediction.column + x) * m_cellSize;
                        int blockY = y * m_cellSize;
                        drawBlock(blockX, blockY);
                    }
                }
            }
        }

        m_renderTarget->EndDraw();
    }
}

void OverlayRenderer::drawBlock(int x, int y) {
    if (!m_renderTarget || !m_brush) return;

    // Draw rectangle outline for ghost piece
    D2D1_RECT_F rect = D2D1::RectF(
        static_cast<float>(x + 1),
        static_cast<float>(y + 1),
        static_cast<float>(x + m_cellSize - 1),
        static_cast<float>(y + m_cellSize - 1)
    );

    m_brush->SetColor(D2D1::ColorF(D2D1::ColorF::Yellow, 0.8f));
    m_renderTarget->DrawRectangle(rect, m_brush.Get(), 2.0f);
}

cv::Mat OverlayRenderer::getPieceShape(const std::string& pieceType, int rotation) const {
    // Same piece definitions as in HeuristicEngine
    if (pieceType == "I") {
        cv::Mat h = (cv::Mat_<uint8_t>(1, 4) << 1, 1, 1, 1);
        cv::Mat v = (cv::Mat_<uint8_t>(4, 1) << 1, 1, 1, 1);
        return rotation % 2 == 0 ? h : v;
    } else if (pieceType == "O") {
        cv::Mat o = (cv::Mat_<uint8_t>(2, 2) << 1, 1, 1, 1);
        return o;
    } else if (pieceType == "T") {
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 0, 1, 0, 1, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 0, 1, 1, 1, 0);
        cv::Mat r2 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 1, 0, 1, 0);
        cv::Mat r3 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 1, 1, 0, 1);
        cv::Mat shapes[] = {r0, r1, r2, r3};
        return shapes[rotation % 4];
    } else if (pieceType == "S") {
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 0, 1, 1, 1, 1, 0);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 0, 1, 1, 0, 1);
        return rotation % 2 == 0 ? r0 : r1;
    } else if (pieceType == "Z") {
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 0, 0, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 1, 1, 1, 0);
        return rotation % 2 == 0 ? r0 : r1;
    } else if (pieceType == "J") {
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 1, 0, 0, 1, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 1, 1, 0, 1, 0);
        cv::Mat r2 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 1, 0, 0, 1);
        cv::Mat r3 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 0, 1, 1, 1);
        cv::Mat shapes[] = {r0, r1, r2, r3};
        return shapes[rotation % 4];
    } else if (pieceType == "L") {
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 0, 0, 1, 1, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 1, 0, 1, 0, 1);
        cv::Mat r2 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 1, 1, 0, 0);
        cv::Mat r3 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 1, 1, 1, 0);
        cv::Mat shapes[] = {r0, r1, r2, r3};
        return shapes[rotation % 4];
    }
    
    // Default: return empty matrix
    return cv::Mat();
}

void OverlayRenderer::setPosition(int x, int y) {
    m_posX = x;
    m_posY = y;
    if (m_hwnd) {
        SetWindowPos(m_hwnd, HWND_TOPMOST, x, y, m_width, m_height, SWP_NOACTIVATE);
    }
}

void OverlayRenderer::start() {
    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

LRESULT CALLBACK OverlayRenderer::WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;

    case WM_PAINT:
        if (s_instance && s_instance->m_hasPrediction) {
            s_instance->drawGhost(s_instance->m_currentPrediction);
        }
        ValidateRect(hwnd, nullptr);
        return 0;

    case WM_KEYDOWN:
        if (wParam == VK_ESCAPE) {
            DestroyWindow(hwnd);
        }
        return 0;

    case WM_ERASEBKGND:
        // Prevent background erasing to avoid flicker
        return 1;

    default:
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
}
