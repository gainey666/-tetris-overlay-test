#include "frame_grabber.h"
#include <iostream>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

FrameGrabber::FrameGrabber() {
    // 1️⃣ Create DXGI factory
    if (FAILED(CreateDXGIFactory1(IID_PPV_ARGS(&m_factory)))) {
        std::cerr << "DXGI factory creation failed.\n";
        return;
    }

    // 2️⃣ Grab the first adapter & output (primary monitor)
    ComPtr<IDXGIAdapter1> adapter;
    if (FAILED(m_factory->EnumAdapters1(0, &adapter))) {
        std::cerr << "Failed to enumerate adapters.\n";
        return;
    }
    if (FAILED(adapter->EnumOutputs(0, &m_dup))) {
        std::cerr << "Failed to enumerate outputs.\n";
        return;
    }

    // 3️⃣ Get output description (size, format)
    DXGI_OUTDUPL_DESC outDesc;
    m_dup->GetDesc(&outDesc);
    m_width  = outDesc.ModeDesc.Width;
    m_height = outDesc.ModeDesc.Height;

    // 4️⃣ Create D3D11 device (needed for the duplication)
    D3D_FEATURE_LEVEL level = D3D_FEATURE_LEVEL_11_0;
    if (FAILED(D3D11CreateDevice(adapter.Get(),
                                   D3D_DRIVER_TYPE_UNKNOWN,
                                   nullptr,
                                   D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                                   &level, 1,
                                   D3D11_SDK_VERSION,
                                   &m_device,
                                   nullptr,
                                   &m_ctx))) {
        std::cerr << "Failed to create D3D11 device.\n";
        return;
    }

    // 5️⃣ Create a CPU‑readable staging texture matching the desktop format
    D3D11_TEXTURE2D_DESC texDesc = {};
    texDesc.Width            = m_width;
    texDesc.Height           = m_height;
    texDesc.MipLevels        = 1;
    texDesc.ArraySize        = 1;
    texDesc.Format           = DXGI_FORMAT_B8G8R8A8_UNORM; // BGRA (matches OpenCV default)
    texDesc.SampleDesc.Count = 1;
    texDesc.Usage            = D3D11_USAGE_STAGING;
    texDesc.CPUAccessFlags   = D3D11_CPU_ACCESS_READ;

    if (FAILED(m_device->CreateTexture2D(&texDesc, nullptr, &m_staging))) {
        std::cerr << "Failed to create staging texture.\n";
        return;
    }
}

FrameGrabber::~FrameGrabber() = default;

bool FrameGrabber::grab(cv::Mat& out) {
    IDXGIResource* dxgiRes = nullptr;
    HRESULT hr = m_dup->AcquireNextFrame(0, nullptr, &dxgiRes);
    if (FAILED(hr)) {
        // timeout = DXGI_ERROR_WAIT_TIMEOUT – not an error, just "no new frame"
        if (hr == DXGI_ERROR_WAIT_TIMEOUT) return false;
        std::cerr << "DXGI AcquireNextFrame failed: 0x" << std::hex << hr << "\n";
        return false;
    }

    // 1️⃣ Get the texture from the acquired frame
    ComPtr<ID3D11Texture2D> srcTex;
    hr = dxgiRes->QueryInterface(IID_PPV_ARGS(&srcTex));
    dxgiRes->Release();
    if (FAILED(hr)) {
        std::cerr << "Failed to get ID3D11Texture2D from frame.\n";
        m_dup->ReleaseFrame();
        return false;
    }

    // 2️⃣ Copy GPU texture to our CPU‑readable staging texture
    m_ctx->CopyResource(m_staging.Get(), srcTex.Get());

    // 3️⃣ Map the staging texture so we can read it from CPU memory
    D3D11_MAPPED_SUBRESOURCE mapped = {};
    hr = m_ctx->Map(m_staging.Get(), 0, D3D11_MAP_READ, 0, &mapped);
    if (FAILED(hr)) {
        std::cerr << "Failed to map staging texture.\n";
        m_dup->ReleaseFrame();
        return false;
    }

    // 4️⃣ Wrap the mapped pointer in a cv::Mat (no copy)
    // OpenCV expects row pitch = width*channels (but DXGI may pad rows)
    // So we create a Mat that references the exact memory layout.
    out = cv::Mat(static_cast<int>(m_height),
                  static_cast<int>(m_width),
                  CV_8UC4,               // BGRA
                  mapped.pData,
                  static_cast<size_t>(mapped.RowPitch));

    // 5️⃣ Unmap and release the frame back to DXGI
    m_ctx->Unmap(m_staging.Get(), 0);
    m_dup->ReleaseFrame();
    return true;
}
