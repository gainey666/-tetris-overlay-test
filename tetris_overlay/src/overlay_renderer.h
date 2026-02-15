#pragma once

#include <windows.h>
#include <d2d1_1.h>
#include <wrl/client.h>
#include "heuristic_engine.h"

using Microsoft::WRL::ComPtr;

/// <summary>
/// Transparent, click-through overlay window using Direct2D
/// </summary>
class OverlayRenderer {
public:
    /// <summary>
    /// Constructor
    /// </summary>
    /// <param name="width">Overlay width in pixels</param>
    /// <param name="height">Overlay height in pixels</param>
    /// <param name="cellSize">Size of each Tetris cell in pixels</param>
    OverlayRenderer(int width, int height, int cellSize);

    ~OverlayRenderer();

    /// <summary>
    /// Initialize Direct2D resources and create overlay window
    /// </summary>
    /// <returns>true on success, false on failure</returns>
    bool initialize();

    /// <summary>
    /// Draw ghost piece at predicted position
    /// </summary>
    /// <param name="pred">Prediction containing piece position</param>
    void drawGhost(const Prediction& pred);

    /// <summary>
    /// Start the overlay message loop
    /// </summary>
    void start();

    /// <summary>
    /// Update overlay position to match game window
    /// </summary>
    /// <param name="x">Window X position</param>
    /// <param name="y">Window Y position</param>
    void setPosition(int x, int y);

private:
    /// <summary>
    /// Create transparent overlay window
    /// </summary>
    /// <returns>true on success, false on failure</returns>
    bool createWindow();

    /// <summary>
    /// Initialize Direct2D factory and render target
    /// </summary>
    /// <returns>true on success, false on failure</returns>
    bool initializeDirect2D();

    /// <summary>
    /// Window procedure for message handling
    /// </summary>
    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

    /// <summary>
    /// Draw a single tetromino block
    /// </summary>
    /// <param name="x">Block X position</param>
    /// <param name="y">Block Y position</param>
    void drawBlock(int x, int y);

    /// <summary>
    /// Get piece shape matrix for drawing
    /// </summary>
    /// <param name="pieceType">Piece type</param>
    /// <param name="rotation">Rotation index</param>
    /// <returns>Piece shape matrix</returns>
    cv::Mat getPieceShape(const std::string& pieceType, int rotation) const;

    HWND m_hwnd;                                    ///< Window handle
    ComPtr<ID2D1Factory1> m_factory;                ///< Direct2D factory
    ComPtr<ID2D1HwndRenderTarget> m_renderTarget;   ///< Render target for window
    ComPtr<ID2D1SolidColorBrush> m_brush;            ///< Brush for drawing
    
    int m_width;                                    ///< Overlay width
    int m_height;                                   ///< Overlay height
    int m_cellSize;                                 ///< Size of each cell
    int m_posX;                                     ///< Window X position
    int m_posY;                                     ///< Window Y position
    
    Prediction m_currentPrediction;                 ///< Current prediction to draw
    bool m_hasPrediction;                           ///< Whether we have a valid prediction
    
    static OverlayRenderer* s_instance;             ///< Static instance for window proc
};
