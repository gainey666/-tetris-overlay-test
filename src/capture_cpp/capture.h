#pragma once
#include <windows.h>
#include <d3d11.h>
#include <dxgi1_2.h>
#include <wrl/client.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <winrt/Windows.Graphics.DirectX.h>
#include <winrt/Windows.Graphics.DirectX.Direct3D11.h>

using namespace Microsoft::WRL;
using namespace winrt;
using namespace Windows::Graphics::Capture;
using namespace Windows::Graphics::DirectX;
using namespace Windows::Graphics::DirectX::Direct3D11;

class FrameGrabber {
public:
    FrameGrabber(HWND gameHwnd);
    ~FrameGrabber();

    // Returns true if a new frame was copied into outTexture
    bool TryGetFrame(ID3D11Texture2D* outTexture);
    
    // Get frame dimensions
    void GetFrameSize(UINT* width, UINT* height);
    
    // Check if capture is active
    bool IsCapturing() const { return m_isCapturing; }

private:
    void InitializeD3D();
    void InitializeCapture();
    
    HWND m_hwnd;
    bool m_isCapturing = false;
    
    // D3D11 objects
    ComPtr<ID3D11Device> m_device;
    ComPtr<ID3D11DeviceContext> m_context;
    ComPtr<ID3D11Texture2D> m_stagingTexture;
    
    // Windows Graphics Capture objects
    GraphicsCaptureItem m_captureItem{ nullptr };
    Direct3D11CaptureFramePool m_framePool{ nullptr };
    GraphicsCaptureSession m_captureSession{ nullptr };
    
    // Frame data
    ComPtr<ID3D11Texture2D> m_latestFrame;
    UINT m_frameWidth = 0;
    UINT m_frameHeight = 0;
    
    // Thread safety
    CRITICAL_SECTION m_frameLock;
};
