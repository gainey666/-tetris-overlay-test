#pragma once

#include <d3d11.h>
#include <dxgi1_2.h>
#include <opencv2/opencv.hpp>
#include <chrono>
#include <vector>
#include <thread>

class FrameGrabber {
public:
    FrameGrabber();
    ~FrameGrabber();
    bool initialize();               // create DXGI resources
    cv::Mat grab();                  // returns a BGRA cv::Mat (pooled)
private:
    // DXGI objects
    ID3D11Device*            device_;
    ID3D11DeviceContext*     context_;
    IDXGIOutputDuplication*  duplication_;
    bool                     initialized_;

    // ---- NEW: pacing, pooling, recovery ---------------------------------
    std::vector<cv::Mat>    pool_;
    size_t                  pool_idx_;
    std::chrono::steady_clock::time_point last_ts_;
    double                   frame_interval_;   // seconds per frame
    void prep_pool(int w, int h);
    void wait_for_next_frame();
    bool recover_from_error(HRESULT hr);
    // --------------------------------------------------------------------
};
