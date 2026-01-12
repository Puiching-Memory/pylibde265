#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "de265.h"
#include "visualize.h"

namespace py = pybind11;

PYBIND11_MODULE(_visualize, m) {
    m.def("draw_CB_grid", [](py::capsule img_cap, py::array_t<uint8_t> dst, uint32_t value, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_CB_grid(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), value, pixelSize);
    });
    m.def("draw_TB_grid", [](py::capsule img_cap, py::array_t<uint8_t> dst, uint32_t value, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_TB_grid(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), value, pixelSize);
    });
    m.def("draw_PB_grid", [](py::capsule img_cap, py::array_t<uint8_t> dst, uint32_t value, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_PB_grid(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), value, pixelSize);
    });
    m.def("draw_PB_pred_modes", [](py::capsule img_cap, py::array_t<uint8_t> dst, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_PB_pred_modes(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), pixelSize);
    });
    m.def("draw_intra_pred_modes", [](py::capsule img_cap, py::array_t<uint8_t> dst, uint32_t value, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_intra_pred_modes(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), value, pixelSize);
    });
    m.def("draw_QuantPY", [](py::capsule img_cap, py::array_t<uint8_t> dst, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_QuantPY(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), pixelSize);
    });
    m.def("draw_Motion", [](py::capsule img_cap, py::array_t<uint8_t> dst, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_Motion(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), pixelSize);
    });
    m.def("draw_Slices", [](py::capsule img_cap, py::array_t<uint8_t> dst, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_Slices(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), pixelSize);
    });
    m.def("draw_Tiles", [](py::capsule img_cap, py::array_t<uint8_t> dst, int pixelSize) {
        const de265_image* img = (const de265_image*)img_cap.get_pointer();
        draw_Tiles(img, (uint8_t*)dst.mutable_data(), (int)dst.strides(0), pixelSize);
    });
}
