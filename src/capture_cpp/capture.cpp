#include "capture.h"
#include "logger.hpp"
#include <iostream>

FrameGrabber::FrameGrabber(HWND hwnd) : m_hwnd(hwnd) {
    LOG_INFO("FrameGrabber", "Constructing FrameGrabber");
    InitializeCriticalSection(&m_frameLock);
    
    try {
        InitializeD3D();
        InitializeCapture();
        m_isCapturing = true;
        LOG_SUCCESS("FrameGrabber", "Successfully initialized capture system");
    }
    catch (const std::exception& e) {
        LOG_FAIL("FrameGrabber", std::string("Failed to initialize capture: ") + e.what());
        std::cerr << "Failed to initialize capture: " << e.what() << std::endl;
        m_isCapturing = false;
    }
}

FrameGrabber::~FrameGrabber() {
    if (m_captureSession) {
        m_captureSession.Close();
    }
    if (m_framePool) {
        m_framePool.Close();
    }
    DeleteCriticalSection(&m_frameLock);
}

void FrameGrabber::InitializeD3D() {
    // Create D3D11 device
    D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_1, D3D_FEATURE_LEVEL_11_0 };
    
    HRESULT hr = D3D11CreateDevice(
        nullptr,
        D3D_DRIVER_TYPE_HARDWARE,
        nullptr,
        D3D11_CREATE_DEVICE_BGRA_SUPPORT,
        featureLevels,
        2,
        D3D11_SDK_VERSION,
        m_device.GetAddressOf(),
        nullptr,
        m_context.GetAddressOf()
    );
    
    if (FAILED(hr)) {
        LOG_FAIL("InitializeD3D", "Failed to create D3D11 device");
        throw std::runtime_error("Failed to create D3D11 device");
    }
    LOG_SUCCESS("InitializeD3D", "D3D11 device created successfully");
}

void FrameGrabber::InitializeCapture() {
    LOG_INFO("InitializeCapture", "Starting capture initialization");
    
    // Create capture item from window handle
    m_captureItem = CreateCaptureItemForWindow(reinterpret_cast<int64_t>(m_hwnd));
    if (!m_captureItem) {
        LOG_FAIL("InitializeCapture", "CreateCaptureItemForWindow returned nullptr");
        throw std::runtime_error("Failed to create capture item");
    }
    LOG_SUCCESS("InitializeCapture", "CaptureItem created successfully");
    
    // Get capture size
    auto size = m_captureItem.Size();
    m_frameWidth = size.Width;
    m_frameHeight = size.Height;
    
    // Create staging texture for CPU access
    D3D11_TEXTURE2D_DESC stagingDesc = {};
    stagingDesc.Width = m_frameWidth;
    stagingDesc.Height = m_frameHeight;
    stagingDesc.Format = DXGI_FORMAT_B8G8R8A8_UNORM;
    stagingDesc.MipLevels = 1;
    stagingDesc.ArraySize = 1;
    stagingDesc.SampleDesc.Count = 1;
    stagingDesc.Usage = D3D11_USAGE_STAGING;
    stagingDesc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
    
    HRESULT hr = m_device->CreateTexture2D(&stagingDesc, nullptr, m_stagingTexture.GetAddressOf());
    if (FAILED(hr)) {
        LOG_FAIL("InitializeCapture", "Failed to create staging texture");
        throw std::runtime_error("Failed to create staging texture");
    }
    LOG_SUCCESS("InitializeCapture", "Staging texture created successfully");
    
    // Create frame pool
    SizeInt32 frameSize{ static_cast<int32_t>(m_frameWidth), static_cast<int32_t>(m_frameHeight) };
    m_framePool = Direct3D11CaptureFramePool::Create(
        m_device.Get(),
        DirectXPixelFormat::B8G8R8A8UIntNormalized,
        2, // Buffer count
        frameSize
    );
    
    // Set up frame arrived callback
    m_framePool.FrameArrived([this](auto&&, auto&&) {
        EnterCriticalSection(&m_frameLock);
        
        auto frame = m_framePool.TryGetNextFrame();
        if (frame) {
            auto surface = frame.Surface();
            ComPtr<ID3D11Texture2D> texture;
            
            // Convert WinRT surface to D3D11 texture
            auto access = surface.as<IDirect3DDxgiInterfaceAccess>();
            if (access) {
                HRESULT hr = access->GetInterface(IID_PPV_ARGS(&texture));
                if (SUCCEEDED(hr)) {
                    m_latestFrame = texture;
                }
            }
        }
        
        LeaveCriticalSection(&m_frameLock);
    });
    
    // Start capture session
    m_captureSession = m_framePool.CreateCaptureSession(m_captureItem);
    m_captureSession.StartCapture();
    LOG_SUCCESS("InitializeCapture", "Capture session started successfully");
}

bool FrameGrabber::TryGetFrame(ID3D11Texture2D* outTexture) {
    if (!m_isCapturing || !outTexture) {
        return false;
    }
    
    EnterCriticalSection(&m_frameLock);
    
    bool success = false;
    if (m_latestFrame) {
        // Copy latest frame to staging texture
        m_context->CopyResource(m_stagingTexture.Get(), m_latestFrame.Get());
        
        // Copy from staging to output texture
        m_context->CopyResource(outTexture, m_stagingTexture.Get());
        success = true;
        LOG_SUCCESS("TryGetFrame", "Frame copied successfully");
    } else {
        LOG_WARN("TryGetFrame", "No frame available");
    }
    
    LeaveCriticalSection(&m_frameLock);
    return success;
}

void FrameGrabber::GetFrameSize(UINT* width, UINT* height) {
    if (width) *width = m_frameWidth;
    if (height) *height = m_frameHeight;
}

// C interface for Python ctypes
extern "C" {
    __declspec(dllexport) FrameGrabber* CreateFrameGrabber(HWND hwnd) {
        LOG_INFO("CreateFrameGrabber", "Creating FrameGrabber instance");
        return new FrameGrabber(hwnd);
    }
    
    __declspec(dllexport) void DestroyFrameGrabber(FrameGrabber* grabber) {
        LOG_INFO("DestroyFrameGrabber", "Destroying FrameGrabber instance");
        delete grabber;
    }
    
    __declspec(dllexport) bool TryGetFrame(FrameGrabber* grabber, ID3D11Texture2D* outTexture) {
        return grabber->TryGetFrame(outTexture);
    }
    
    __declspec(dllexport) void GetFrameSize(FrameGrabber* grabber, UINT* width, UINT* height) {
        grabber->GetFrameSize(width, height);
    }
    
    __declspec(dllexport) bool IsCapturing(FrameGrabber* grabber) {
        return grabber->IsCapturing();
    }
}
