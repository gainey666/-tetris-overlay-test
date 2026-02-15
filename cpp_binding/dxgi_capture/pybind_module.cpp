#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "dxgi_frame_grabber.h"

namespace py = pybind11;

PYBIND11_MODULE(dxgi_capture, m) {
    m.doc() = "DXGI Frame Grabber for Windows";

    py::class_<FrameGrabber>(m, "FrameGrabber")
        .def(py::init<>())
        .def("initialize", &FrameGrabber::initialize)
        .def("grab", &FrameGrabber::grab);
}
