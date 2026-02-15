# Future Development Roadmap

## Immediate Next Steps (Week 1)
1. **ONNX Model Integration**
   - Download real tetris_perfect.onnx model
   - Test with real model instead of mock
   - Validate input/output format with Netron

2. **Enhanced AI Features**
   - Implement hold piece logic
   - Add multi-piece look-ahead (2-3 pieces)
   - Integrate combo and B2B scoring

## Medium Term (Month 1)
3. **Visual Improvements**
   - Implement Pygame transparent overlay
   - Add ghost piece visualization
   - Create configuration GUI

4. **Performance Optimization**
   - Profile and optimize bottlenecks
   - Add frame pacing controls
   - Implement adaptive quality settings

## Long Term (Month 2-3)
5. **Advanced Features**
   - Real game capture integration (DXGI)
   - Multi-monitor support
   - Recording and replay functionality

6. **Distribution**
   - Create Windows installer
   - Add auto-update mechanism
   - Package for Linux/macOS

## Technical Debt
- Add comprehensive unit tests
- Implement proper error handling
- Add logging configuration
- Create CI/CD pipeline

## Security & Maintenance
- Add model validation
- Implement secure update checks
- Create user documentation
- Add troubleshooting guide

## Metrics to Track
- Inference latency (target: <10ms)
- Memory usage (target: <100MB)
- CPU usage (target: <5% idle)
- User adoption and feedback
