#include "dxgi_frame_grabber.h"
#include <windows.h>
#include <stdexcept>
#include <thread>
#include <vector>
#include <opencv2/opencv.hpp>

FrameGrabber::FrameGrabber()
    : device_(nullptr), context_(nullptr), duplication_(nullptr),
      initialized_(false), pool_idx_(0), frame_interval_(1.0/60.0), last_ts_() {}

FrameGrabber::~FrameGrabber() {
    if (duplication_) duplication_->Release();
    if (context_)    context_->Release();
    if (device_)    device_->Release();
}

// ------------------------------------------------------------
bool FrameGrabber::initialize() {
    // ---- DXGI device/duplication creation (unchanged) ------------------
    HRESULT hr = D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE,
                                   nullptr, 0, nullptr, 0,
                                   D3D11_SDK_VERSION, &device_, nullptr, &context_);
    if (FAILED(hr)) return false;

    IDXGIDevice* dxgiDevice = nullptr;
    hr = device_->QueryInterface(__uuidof(IDXGIDevice), reinterpret_cast<void**>(&dxgiDevice));
    if (FAILED(hr)) return false;

    IDXGIAdapter* adapter = nullptr;
    hr = dxgiDevice->GetAdapter(&adapter);
    dxgiDevice->Release();
    if (FAILED(hr)) return false;

    IDXGIOutput* output = nullptr;
    hr = adapter->EnumOutputs(0, &output);
    adapter->Release();
    if (FAILED(hr)) return false;

    IDXGIOutput1* output1 = nullptr;
    hr = output->QueryInterface(__uuidof(IDXGIOutput1), reinterpret_cast<void**>(&output1));
    output->Release();
    if (FAILED(hr)) return false;

    hr = output1->DuplicateOutput(device_, &duplication_);
    output1->Release();
    if (FAILED(hr)) return false;
    // -----------------------------------------------------------------

    // Get desktop size to allocate the pool
    DXGI_OUTDUPL_DESC desc;
    duplication_->GetDesc(&desc);
    prep_pool(static_cast<int>(desc.ModeDesc.Width),
               static_cast<int>(desc.ModeDesc.Height));

    // set pacing based on env var (or default 60fps)
    const char* env_fps = std::getenv("DXGI_TARGET_FPS");
    int fps = env_fps ? std::atoi(env_fps) : 60;
    frame_interval_ = 1.0 / static_cast<double>(fps);
    last_ts_ = std::chrono::steady_clock::now();

    initialized_ = true;
    return true;
}

// ------------------------------------------------------------
void FrameGrabber::prep_pool(int w, int h) {
    const char* env_sz = std::getenv("DXGI_POOL_SIZE");
    int pool_sz = env_sz ? std::atoi(env_sz) : 3;
    pool_.clear();
    for (int i = 0; i < pool_sz; ++i)
        pool_.emplace_back(h, w, CV_8UC4);   // BGRA
    pool_idx_ = 0;
}

// ------------------------------------------------------------
void FrameGrabber::wait_for_next_frame() {
    auto now = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(now - last_ts_).count();
    if (elapsed < frame_interval_) {
        std::this_thread::sleep_for(
            std::chrono::duration<double>(frame_interval_ - elapsed));
    }
    last_ts_ = std::chrono::steady_clock::now();
}

// ------------------------------------------------------------
bool FrameGrabber::recover_from_error(HRESULT hr) {
    if (hr == DXGI_ERROR_ACCESS_LOST ||
        hr == DXGI_ERROR_DEVICE_REMOVED ||
        hr == DXGI_ERROR_DEVICE_RESET) {
        // Release all DXGI objects
        if (duplication_) { duplication_->Release(); duplication_ = nullptr; }
        if (context_)    { context_->Release();    context_    = nullptr; }
        if (device_)    { device_->Release();    device_    = nullptr; }
        initialized_ = false;
        return initialize();   // try to re‑init
    }
    return false;
}

// ------------------------------------------------------------
cv::Mat FrameGrabber::grab() {
    if (!initialized_) return cv::Mat();

    wait_for_next_frame();

    DXGI_OUTDUPL_FRAME_INFO frameInfo;
    IDXGIResource* desktopResource = nullptr;
    HRESULT hr = duplication_->AcquireNextFrame(500, &frameInfo, &desktopResource);
    if (FAILED(hr)) {
        if (!recover_from_error(hr)) return cv::Mat();   // unrecoverable
        // retry once after recovery
        hr = duplication_->AcquireNextFrame(500, &frameInfo, &desktopResource);
        if (FAILED(hr)) return cv::Mat();
    }

    ID3D11Texture2D* acquiredDesktopImage = nullptr;
    hr = desktopResource->QueryInterface(__uuidof(ID3D11Texture2D),
                                         reinterpret_cast<void**>(&acquiredDesktopImage));
    desktopResource->Release();
    if (FAILED(hr)) {
        duplication_->ReleaseFrame();
        return cv::Mat();
    }

    // ---- copy to a pre‑allocated buffer from the pool --------------------
    cv::Mat& dst = pool_[pool_idx_];
    pool_idx_ = (pool_idx_ + 1) % pool_.size();

    // create staging texture for CPU read
    D3D11_TEXTURE2D_DESC desc;
    acquiredDesktopImage->GetDesc(&desc);
    D3D11_TEXTURE2D_DESC stagingDesc = {};
    stagingDesc.Width = desc.Width;
    stagingDesc.Height = desc.Height;
    stagingDesc.MipLevels = 1;
    stagingDesc.ArraySize = 1;
    stagingDesc.Format = desc.Format;
    stagingDesc.SampleDesc.Count = 1;
    stagingDesc.Usage = D3D11_USAGE_STAGING;
    stagingDesc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;

    ID3D11Texture2D* stagingTexture = nullptr;
    hr = device_->CreateTexture2D(&stagingDesc, nullptr, &stagingTexture);
    if (FAILED(hr)) {
        acquiredDesktopImage->Release();
        duplication_->ReleaseFrame();
        return cv::Mat();
    }

    context_->CopyResource(stagingTexture, acquiredDesktopImage);
    D3D11_MAPPED_SUBRESOURCE mapped{};
    hr = context_->Map(stagingTexture, 0, D3D11_MAP_READ, 0, &mapped);
    if (SUCCEEDED(hr)) {
        const BYTE* src = reinterpret_cast<const BYTE*>(mapped.pData);
        for (int y = 0; y < desc.Height; ++y) {
            memcpy(dst.ptr(y), src + y * mapped.RowPitch, desc.Width * 4);
        }
        context_->Unmap(stagingTexture, 0);
    }

    // cleanup per‑frame resources
    stagingTexture->Release();
    acquiredDesktopImage->Release();
    duplication_->ReleaseFrame();

    // Return a *copy* so the pool can be reused safely
    return dst.clone();
}
