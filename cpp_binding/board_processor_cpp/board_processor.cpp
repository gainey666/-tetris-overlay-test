#include "board_processor.hpp"

std::vector<uint8_t> process_board(const cv::Mat& frame) {
    cv::Mat gray;
    cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

    cv::Mat blurred;
    cv::GaussianBlur(gray, blurred, cv::Size(5, 5), 0);

    cv::Mat thresh;
    cv::adaptiveThreshold(
        blurred,
        thresh,
        255,
        cv::ADAPTIVE_THRESH_GAUSSIAN_C,
        cv::THRESH_BINARY,
        11,
        2
    );

    cv::Mat resized;
    cv::resize(thresh, resized, cv::Size(20, 10), 0, 0, cv::INTER_NEAREST);

    std::vector<uint8_t> out;
    out.reserve(20 * 10);
    for (int r = 0; r < resized.rows; ++r) {
        const uint8_t* row_ptr = resized.ptr<uint8_t>(r);
        for (int c = 0; c < resized.cols; ++c) {
            out.push_back(row_ptr[c] > 127 ? 255 : 0);
        }
    }
    return out;
}
