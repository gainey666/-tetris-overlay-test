#pragma once

#include <string>
#include <vector>

#ifdef HAVE_ONNXRUNTIME
#include <onnxruntime_cxx_api.h>
#endif

#ifndef NO_OPENCV
#include <opencv2/opencv.hpp>
#endif

/// <summary>
/// Prediction result structure
/// </summary>
struct Prediction {
    int rotation;        ///< Piece rotation (0-3)
    int column;          ///< Column position (0-9)
    float score;         ///< Evaluation score
    std::string piece_type; ///< Piece type ("I","O","T","S","Z","J","L")
};

/// <summary>
/// Tetris piece evaluation engine using heuristic scoring or optional CNN
/// </summary>
class HeuristicEngine {
public:
    HeuristicEngine();
    ~HeuristicEngine();

#ifdef NO_OPENCV
    /// <summary>
    /// Simple evaluation without board (demo mode)
    /// </summary>
    /// <param name="dummyBoard">Placeholder parameter</param>
    /// <param name="curPiece">Current piece type</param>
    /// <returns>Demo prediction</returns>
    Prediction evaluate(int dummyBoard, const std::string& curPiece);
#else
    /// <summary>
    /// Evaluate the best move for current board and piece
    /// </summary>
    /// <param name="board">20x10 binary board matrix</param>
    /// <param name="curPiece">Current piece type</param>
    /// <returns>Best prediction</returns>
    Prediction evaluate(const cv::Mat& board, const std::string& curPiece);
#endif

private:
#ifdef HAVE_ONNXRUNTIME
    /// <summary>
    /// Initialize ONNX runtime session for CNN predictions
    /// </summary>
    void initializeONNX();

    /// <summary>
    /// Predict using ONNX CNN model
    /// </summary>
    /// <param name="board">Board matrix</param>
    /// <param name="curPiece">Current piece</param>
    /// <returns>CNN prediction</returns>
    Prediction predictCNN(const cv::Mat& board, const std::string& curPiece);

    std::unique_ptr<Ort::Session> m_onnxSession;
    bool m_useCNN;
#endif
};
