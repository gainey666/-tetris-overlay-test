#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <vector>

#include "board_processor.hpp"

namespace py = pybind11;

py::array_t<uint8_t> process_board_py(py::array_t<uint8_t> input) {
    py::buffer_info buf = input.request();
    if (buf.ndim != 3 || buf.shape[2] != 3) {
        throw std::runtime_error("Input must be an HxWx3 uint8 array");
    }

    int height = static_cast<int>(buf.shape[0]);
    int width = static_cast<int>(buf.shape[1]);

    cv::Mat frame(height, width, CV_8UC3, buf.ptr);
    std::vector<uint8_t> mask = process_board(frame);

    return py::array_t<uint8_t>(
        {static_cast<ssize_t>(mask.size())},
        {static_cast<ssize_t>(sizeof(uint8_t))},
        mask.data()
    );
}

PYBIND11_MODULE(board_processor_cpp, m) {
    m.doc() = "C++ board-processor exposed via pybind11";
    m.def("process_board", &process_board_py, "Convert a BGR frame to a 20x10 mask");
}
