#pragma once
#include <windows.h>
#include <dxgi1_2.h>
#include <d3d11.h>
#include <opencv2/core.hpp>

/**
 * @brief Captures the primary monitor using DXGI Desktop Duplication.
 *
 * The class owns the DXGI factory, output duplication, a D3D11 device,
 * and a staging texture that can be mapped as a cv::Mat (BGRA format).
 * All heavy resources are created once in the constructor.
 */
class FrameGrabber {
public:
    FrameGrabber();
    ~FrameGrabber();

    /**
     * @brief Grab the latest frame and wrap it in a cv::Mat.
     *
     * The returned Mat points directly into the mapped staging texture,
     * so **no data copy** is performed. Do **not** keep the Mat beyond the next
     * call to `grab` – the mapping is released when the next frame is acquired.
     *
     * @param out  Output cv::Mat (type CV_8UC4, B,G,R,A order).
     * @return true on success, false on failure (error printed to std::cerr).
     */
    bool grab(cv::Mat& out);

private:
    // COM objects
    Microsoft::WRL::ComPtr<IDXGIFactory2>        m_factory;
    Microsoft::WRL::ComPtr<IDXGIOutputDuplication> m_dup;
    Microsoft::WRL::ComPtr<ID3D11Device>       m_device;
    Microsoft::WRL::ComPtr<ID3D11DeviceContext> m_ctx;
    Microsoft::WRL::ComPtr<ID3D11Texture2D>    m_staging;   // CPU‑readable

    // Frame dimensions (set during construction)
    UINT m_width{};
    UINT m_height{};
};
