#include "heuristic_engine.h"
#include <iostream>
#include <algorithm>
#include <limits>

HeuristicEngine::HeuristicEngine() {
#ifdef HAVE_ONNXRUNTIME
    m_useCNN = false;
    initializeONNX();
#endif
}

HeuristicEngine::~HeuristicEngine() {
#ifdef HAVE_ONNXRUNTIME
    m_onnxSession.reset();
#endif
}

Prediction HeuristicEngine::evaluate(const cv::Mat& board, const std::string& curPiece) {
#ifdef HAVE_ONNXRUNTIME
    if (m_useCNN) {
        return predictCNN(board, curPiece);
    }
#endif

    // Use heuristic evaluation
    Prediction bestPred;
    bestPred.score = -std::numeric_limits<float>::max();
    bestPred.piece_type = curPiece;

    // Get all possible rotations for this piece
    std::vector<cv::Mat> rotations = getPieceShapes(curPiece);

    // Try all possible positions and rotations
    for (int rot = 0; rot < static_cast<int>(rotations.size()); ++rot) {
        const cv::Mat& piece = rotations[rot];
        
        // Try all possible columns
        for (int col = 0; col < 10; ++col) {
            // Check if piece can be placed at this column
            int dropRow = dropPiece(board, piece, col);
            if (dropRow < 0) continue; // Can't place here

            // Create new board with piece placed
            cv::Mat newBoard = placePiece(board, piece, col, dropRow);
            
            // Clear lines and get count
            int linesCleared = clearLines(newBoard);
            
            // Evaluate this position
            float score = evaluatePosition(newBoard, linesCleared);
            
            // Update best prediction
            if (score > bestPred.score) {
                bestPred.score = score;
                bestPred.rotation = rot;
                bestPred.column = col;
            }
        }
    }

    return bestPred;
}

std::vector<cv::Mat> HeuristicEngine::getPieceShapes(const std::string& pieceType) const {
    std::vector<cv::Mat> shapes;
    
    if (pieceType == "I") {
        // I-piece: 4x1 horizontal and 1x4 vertical
        cv::Mat h = (cv::Mat_<uint8_t>(1, 4) << 1, 1, 1, 1);
        cv::Mat v = (cv::Mat_<uint8_t>(4, 1) << 1, 1, 1, 1);
        shapes = {h, v};
    } else if (pieceType == "O") {
        // O-piece: 2x2 square
        cv::Mat o = (cv::Mat_<uint8_t>(2, 2) << 1, 1, 1, 1);
        shapes = {o};
    } else if (pieceType == "T") {
        // T-piece: 4 rotations
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 0, 1, 0, 1, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 0, 1, 1, 1, 0);
        cv::Mat r2 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 1, 0, 1, 0);
        cv::Mat r3 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 1, 1, 0, 1);
        shapes = {r0, r1, r2, r3};
    } else if (pieceType == "S") {
        // S-piece: 2 rotations
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 0, 1, 1, 1, 1, 0);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 0, 1, 1, 0, 1);
        shapes = {r0, r1};
    } else if (pieceType == "Z") {
        // Z-piece: 2 rotations
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 0, 0, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 1, 1, 1, 0);
        shapes = {r0, r1};
    } else if (pieceType == "J") {
        // J-piece: 4 rotations
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 1, 0, 0, 1, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 1, 1, 0, 1, 0);
        cv::Mat r2 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 1, 0, 0, 1);
        cv::Mat r3 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 0, 1, 1, 1);
        shapes = {r0, r1, r2, r3};
    } else if (pieceType == "L") {
        // L-piece: 4 rotations
        cv::Mat r0 = (cv::Mat_<uint8_t>(2, 3) << 0, 0, 1, 1, 1, 1);
        cv::Mat r1 = (cv::Mat_<uint8_t>(3, 2) << 1, 1, 0, 1, 0, 1);
        cv::Mat r2 = (cv::Mat_<uint8_t>(2, 3) << 1, 1, 1, 1, 0, 0);
        cv::Mat r3 = (cv::Mat_<uint8_t>(3, 2) << 0, 1, 1, 1, 1, 0);
        shapes = {r0, r1, r2, r3};
    }
    
    return shapes;
}

bool HeuristicEngine::canPlace(const cv::Mat& board, const cv::Mat& piece, int col, int row) const {
    int pieceH = piece.rows;
    int pieceW = piece.cols;
    
    for (int y = 0; y < pieceH; ++y) {
        for (int x = 0; x < pieceW; ++x) {
            if (piece.at<uint8_t>(y, x)) {
                int boardY = row + y;
                int boardX = col + x;
                
                // Check boundaries
                if (boardX < 0 || boardX >= 10 || boardY >= 20) {
                    return false;
                }
                
                // Check collision with existing blocks
                if (boardY >= 0 && board.at<uint8_t>(boardY, boardX)) {
                    return false;
                }
            }
        }
    }
    return true;
}

cv::Mat HeuristicEngine::placePiece(const cv::Mat& board, const cv::Mat& piece, int col, int row) const {
    cv::Mat newBoard = board.clone();
    int pieceH = piece.rows;
    int pieceW = piece.cols;
    
    for (int y = 0; y < pieceH; ++y) {
        for (int x = 0; x < pieceW; ++x) {
            if (piece.at<uint8_t>(y, x)) {
                int boardY = row + y;
                int boardX = col + x;
                if (boardY >= 0 && boardY < 20 && boardX >= 0 && boardX < 10) {
                    newBoard.at<uint8_t>(boardY, boardX) = 1;
                }
            }
        }
    }
    
    return newBoard;
}

int HeuristicEngine::dropPiece(const cv::Mat& board, const cv::Mat& piece, int col) const {
    // Start from top and drop down
    for (int row = -piece.rows; row < 20; ++row) {
        if (!canPlace(board, piece, col, row + 1)) {
            return row;
        }
    }
    return -1; // Can't place
}

int HeuristicEngine::clearLines(cv::Mat& board) const {
    int linesCleared = 0;
    
    for (int y = 19; y >= 0; --y) {
        bool lineFull = true;
        for (int x = 0; x < 10; ++x) {
            if (!board.at<uint8_t>(y, x)) {
                lineFull = false;
                break;
            }
        }
        
        if (lineFull) {
            // Remove this line and shift everything down
            for (int shiftY = y; shiftY > 0; --shiftY) {
                for (int x = 0; x < 10; ++x) {
                    board.at<uint8_t>(shiftY, x) = board.at<uint8_t>(shiftY - 1, x);
                }
            }
            
            // Clear top line
            for (int x = 0; x < 10; ++x) {
                board.at<uint8_t>(0, x) = 0;
            }
            
            linesCleared++;
            y++; // Check the same line again
        }
    }
    
    return linesCleared;
}

float HeuristicEngine::evaluatePosition(const cv::Mat& board, int linesCleared) const {
    float score = 0.0f;
    
    // Lines cleared is very good
    score += linesCleared * WEIGHT_LINES;
    
    // Lower aggregate height is better
    int aggregateHeight = calculateAggregateHeight(board);
    score += aggregateHeight * WEIGHT_HEIGHT;
    
    // Fewer holes is better
    int holes = countHoles(board);
    score += holes * WEIGHT_HOLES;
    
    // Less bumpiness is better
    int bumpiness = calculateBumpiness(board);
    score += bumpiness * WEIGHT_BUMPINESS;
    
    return score;
}

int HeuristicEngine::calculateAggregateHeight(const cv::Mat& board) const {
    int totalHeight = 0;
    
    for (int x = 0; x < 10; ++x) {
        int columnHeight = 0;
        for (int y = 19; y >= 0; --y) {
            if (board.at<uint8_t>(y, x)) {
                columnHeight = y + 1;
                break;
            }
        }
        totalHeight += columnHeight;
    }
    
    return totalHeight;
}

int HeuristicEngine::countHoles(const cv::Mat& board) const {
    int holes = 0;
    
    for (int x = 0; x < 10; ++x) {
        bool foundBlock = false;
        for (int y = 0; y < 20; ++y) {
            if (board.at<uint8_t>(y, x)) {
                foundBlock = true;
            } else if (foundBlock && !board.at<uint8_t>(y, x)) {
                holes++;
            }
        }
    }
    
    return holes;
}

int HeuristicEngine::calculateBumpiness(const cv::Mat& board) const {
    int bumpiness = 0;
    int prevHeight = 0;
    
    for (int x = 0; x < 10; ++x) {
        int columnHeight = 0;
        for (int y = 19; y >= 0; --y) {
            if (board.at<uint8_t>(y, x)) {
                columnHeight = y + 1;
                break;
            }
        }
        
        if (x > 0) {
            bumpiness += std::abs(columnHeight - prevHeight);
        }
        prevHeight = columnHeight;
    }
    
    return bumpiness;
}

#ifdef HAVE_ONNXRUNTIME
void HeuristicEngine::initializeONNX() {
    try {
        // Try to load ONNX model
        Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "tetris_onnx");
        Ort::SessionOptions session_options;
        
        std::string modelPath = "tetris_cnn.onnx";
        std::ifstream file(modelPath);
        if (file.good()) {
            m_onnxSession = std::make_unique<Ort::Session>(env, modelPath.c_str(), session_options);
            m_useCNN = true;
            std::cout << "Loaded ONNX CNN model: " << modelPath << std::endl;
        }
    } catch (const std::exception& e) {
        std::cout << "Failed to load ONNX model, using heuristic: " << e.what() << std::endl;
        m_useCNN = false;
    }
}

Prediction HeuristicEngine::predictCNN(const cv::Mat& board, const std::string& curPiece) {
    // This is a stub implementation - real CNN inference would go here
    // For now, fall back to heuristic
    return evaluate(board, curPiece);
}
#endif
