#pragma once
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

/**
 * @brief Convert a captured BGRA frame into a 20×10 binary board matrix.
 *
 * The class is constructed once with the ROI of the Tetris board (in screen
 * coordinates). `extract` then returns a CV_8U matrix where 1 = block,
 * 0 = empty.
 */
class BoardExtractor {
public:
    explicit BoardExtractor(const cv::Rect& roi);
    /** @return CV_8U 20×10 matrix (0/1) */
    cv::Mat extract(const cv::Mat& frame) const;
private:
    cv::Rect m_roi;
};
