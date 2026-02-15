#include <iostream>
#include <thread>
#include <chrono>

#ifndef NO_OPENCV
#include <opencv2/opencv.hpp>
#endif

#include "frame_grabber.h"
#include "board_extractor.h"
#include "heuristic_engine.h"
#include "overlay_renderer.h"
#include "calibrate.h"
#include "utils.h"

/// <summary>
/// Run performance benchmark for all pipeline stages
/// </summary>
/// <param name="grabber">Frame grabber instance</param>
/// <param name="extractor">Board extractor instance</param>
/// <param name="engine">Heuristic engine instance</param>
/// <param name="renderer">Overlay renderer instance</param>
void runBenchmark(FrameGrabber& grabber, BoardExtractor& extractor, HeuristicEngine& engine, OverlayRenderer& renderer) {
    std::cout << "\n=== Performance Benchmark (200ms) ===" << std::endl;
    
    const int benchmarkDuration = 200; // milliseconds
    const std::string testPiece = "T"; // Test piece for evaluation
    
    Utils::Timer totalTimer;
    Utils::Timer captureTimer;
    Utils::Timer extractionTimer;
    Utils::Timer predictionTimer;
    Utils::Timer overlayTimer;
    
    int frameCount = 0;
    double totalCaptureTime = 0.0;
    double totalExtractionTime = 0.0;
    double totalPredictionTime = 0.0;
    double totalOverlayTime = 0.0;
    
    totalTimer.start();
    
    while (totalTimer.elapsed() < benchmarkDuration) {
        // Test capture
        captureTimer.start();
        cv::Mat frame;
        bool captureSuccess = grabber.grab(frame);
        totalCaptureTime += captureTimer.stop();
        
        if (!captureSuccess) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            continue;
        }
        
        // Test board extraction
        extractionTimer.start();
        cv::Mat board = extractor.extract(frame);
        totalExtractionTime += extractionTimer.stop();
        
        if (board.empty()) {
            continue;
        }
        
        // Test prediction
        predictionTimer.start();
        Prediction pred = engine.evaluate(board, testPiece);
        totalPredictionTime += predictionTimer.stop();
        
        // Test overlay rendering
        overlayTimer.start();
        renderer.drawGhost(pred);
        totalOverlayTime += overlayTimer.stop();
        
        frameCount++;
    }
    
    // Calculate averages
    if (frameCount > 0) {
        double avgCapture = totalCaptureTime / frameCount;
        double avgExtraction = totalExtractionTime / frameCount;
        double avgPrediction = totalPredictionTime / frameCount;
        double avgOverlay = totalOverlayTime / frameCount;
        double avgTotal = avgCapture + avgExtraction + avgPrediction + avgOverlay;
        
        printf("Capture   : %.2f ms\n", avgCapture);
        printf("Board proc: %.2f ms\n", avgExtraction);
        printf("Predict   : %.2f ms\n", avgPrediction);
        printf("Overlay   : %.2f ms\n", avgOverlay);
        printf("Total per frame: %.2f ms (≈ %.0f FPS)\n", avgTotal, 1000.0 / avgTotal);
        printf("Frames processed: %d\n", frameCount);
    } else {
        std::cout << "No frames processed during benchmark" << std::endl;
    }
    
    std::cout << "=== Benchmark Complete ===\n" << std::endl;
}

/// <summary>
/// Main overlay loop
/// </summary>
/// <param name="grabber">Frame grabber instance</param>
/// <param name="extractor">Board extractor instance</param>
/// <param name="engine">Heuristic engine instance</param>
/// <param name="renderer">Overlay renderer instance</param>
void overlayLoop(FrameGrabber& grabber, BoardExtractor& extractor, HeuristicEngine& engine, OverlayRenderer& renderer) {
    std::cout << "Starting overlay loop... Press ESC to exit." << std::endl;
    
    // Simple piece detection (placeholder - in real implementation this would be more sophisticated)
    std::string currentPiece = "T";
    int pieceChangeCounter = 0;
    
    while (true) {
        // Capture frame
        cv::Mat frame;
        if (!grabber.grab(frame)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            continue;
        }
        
        // Extract board
        cv::Mat board = extractor.extract(frame);
        if (board.empty()) {
            continue;
        }
        
        // Simulate piece changes (placeholder logic)
        pieceChangeCounter++;
        if (pieceChangeCounter > 300) { // Change piece every ~5 seconds at 60fps
            const std::string pieces[] = {"I", "O", "T", "S", "Z", "J", "L"};
            currentPiece = pieces[rand() % 7];
            pieceChangeCounter = 0;
        }
        
        // Get prediction
        Prediction pred = engine.evaluate(board, currentPiece);
        
        // Update overlay
        renderer.drawGhost(pred);
        
        // Small delay to prevent excessive CPU usage
        std::this_thread::sleep_for(std::chrono::milliseconds(16)); // ~60 FPS
    }
}

int main(int argc, char* argv[]) {
    std::cout << "Tetris Overlay - Real-time Best Move Predictor" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Check for calibration flag
    bool runCalibration = false;
    if (argc > 1 && std::string(argv[1]) == "--calibrate") {
        runCalibration = true;
    }
    
    // Load calibration
    cv::Rect roi;
    if (runCalibration) {
        Calibrator calibrator;
        if (!calibrator.run()) {
            std::cerr << "Calibration failed" << std::endl;
            return 1;
        }
        roi = calibrator.getROI();
    } else {
        Calibrator calibrator;
        if (!calibrator.loadFromFile("calibration.json")) {
            std::cerr << "No calibration found. Run with --calibrate first." << std::endl;
            return 1;
        }
        roi = calibrator.getROI();
    }
    
    // Initialize components
    FrameGrabber grabber;
    if (!grabber.initialize()) {
        std::cerr << "Failed to initialize frame grabber" << std::endl;
        return 1;
    }
    
    BoardExtractor extractor(roi);
    HeuristicEngine engine;
    
    // Calculate cell size for overlay
    int cellSize = roi.width / 10; // Standard Tetris board is 10 columns wide
    
    // Position overlay to match game window
    OverlayRenderer renderer(roi.width, roi.height, cellSize);
    renderer.setPosition(roi.x, roi.y);
    
    if (!renderer.initialize()) {
        std::cerr << "Failed to initialize overlay renderer" << std::endl;
        return 1;
    }
    
    std::cout << "All components initialized successfully." << std::endl;
    
    // Run benchmark
    runBenchmark(grabber, extractor, engine, renderer);
    
    // Start overlay in separate thread
    std::thread overlayThread([&]() {
        overlayLoop(grabber, extractor, engine, renderer);
    });
    
    // Handle overlay window messages in main thread
    renderer.start();
    
    // Cleanup (this code won't be reached due to renderer.start() blocking)
    overlayThread.join();
    
    return 0;
}
