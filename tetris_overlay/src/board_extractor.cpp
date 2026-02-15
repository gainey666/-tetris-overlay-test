#include "board_extractor.h"
#include <iostream>

BoardExtractor::BoardExtractor(const cv::Rect& roi) : m_roi(roi) {}

cv::Mat BoardExtractor::extract(const cv::Mat& frame) const {
    // 1️⃣ Crop to the ROI
    cv::Mat boardImg = frame(m_roi);

    // 2️⃣ Convert BGRA → HSV (OpenCV expects BGR; we ignore alpha)
    cv::Mat hsv;
    cv::cvtColor(boardImg, hsv, cv::COLOR_BGR2HSV);

    // 3️⃣ Threshold to keep any bright block colour.
    //    The exact bounds may need tweaking for your theme.
    cv::Scalar lower(0, 50, 50);   // H low, S low, V low
    cv::Scalar upper(180, 255, 255);
    cv::Mat mask;
    cv::inRange(hsv, lower, upper, mask);

    // 4️⃣ Fill tiny holes (common when anti‑aliasing is present)
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, {3,3});
    cv::morphologyEx(mask, mask, cv::MORPH_CLOSE, kernel);

    // 5️⃣ Down‑sample each cell to a single pixel (average pooling)
    cv::Mat boardSmall;
    cv::resize(mask, boardSmall, {10,20}, 0,0, cv::INTER_AREA);

    // 6️⃣ Binary threshold (0/1)
    boardSmall = (boardSmall > 30);
    boardSmall.convertTo(boardSmall, CV_8U);   // ensure 0/1 values

    return boardSmall;   // shape (20 rows, 10 cols)
}
