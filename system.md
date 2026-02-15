# System Architecture & Data Flow

+----------------------+   +------------------------+   +----------------------+ 
| CaptureAgent         | → | BoardProcessorAgent    | → | PredictionAgent      |
| (opencv VideoCapture)|   | (opencv threshold)     |   | (onnx / dummy model) |
+----------------------+   +------------------------+   +----------------------+
                                                 ↓
                                         +---------------------+
                                         | OverlayRendererAgent|
                                         +---------------------+
                                                 ↓
                                             +---------+
                                             | RunAgent|
                                             +---------+
                                                 ↓
                                           +-------------+
                                           | ShutdownAgent|
                                           +-------------+

1. CaptureAgent pushes `numpy.ndarray` frames into a queue.
2. BoardProcessorAgent converts frames into a 20×10 binary mask.
3. PredictionAgent reads masks and produces dummy piece predictions.
4. OverlayRendererAgent draws masks + predictions via pygame.
5. RunAgent ties the pipeline together, while ShutdownAgent cleans up.

Future migration replaces the left‑hand agents with native C++ modules exposed through pybind11, while keeping the Python orchestrator intact.
