#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "de265.h"
#include <vector>
#include <memory>
#include <algorithm>

namespace py = pybind11;

// Wrapper for de265_image
class PyImage {
public:
    PyImage(const de265_image* img, bool release_on_delete = false, de265_decoder_context* ctx = nullptr)
        : img(img), release_on_delete(release_on_delete), ctx(ctx) {}

    ~PyImage() {
        if (release_on_delete && ctx) {
            de265_release_next_picture(ctx);
        }
    }

    int get_width(int channel) const { return de265_get_image_width(img, channel); }
    int get_height(int channel) const { return de265_get_image_height(img, channel); }
    de265_chroma get_chroma_format() const { return de265_get_chroma_format(img); }
    int get_bits_per_pixel(int channel) const { return de265_get_bits_per_pixel(img, channel); }
    de265_PTS get_pts() const { return de265_get_image_PTS(img); }

    py::object get_plane(int channel) const {
        int stride;
        const uint8_t* data = de265_get_image_plane(img, channel, &stride);
        if (!data) return py::none();
        
        int height = de265_get_image_height(img, channel);
        int width = de265_get_image_width(img, channel);
        int bpp = de265_get_bits_per_pixel(img, channel);
        
        if (bpp > 8) {
            return py::array_t<uint16_t>(
                {height, width},
                {stride, 2},
                (const uint16_t*)data,
                py::cast(this)
            );
        } else {
            return py::array_t<uint8_t>(
                {height, width},
                {stride, 1},
                data,
                py::cast(this)
            );
        }
    }

    py::dict get_nal_header() const {
        int type, layer_id, temporal_id;
        const char* name;
        de265_get_image_NAL_header(img, &type, &name, &layer_id, &temporal_id);
        py::dict d;
        d["type"] = type;
        d["name"] = name ? std::string(name) : "";
        d["layer_id"] = layer_id;
        d["temporal_id"] = temporal_id;
        return d;
    }

    int get_full_range_flag() const { return de265_get_image_full_range_flag(img); }
    int get_colour_primaries() const { return de265_get_image_colour_primaries(img); }
    int get_transfer_characteristics() const { return de265_get_image_transfer_characteristics(img); }
    int get_matrix_coefficients() const { return de265_get_image_matrix_coefficients(img); }

    py::array_t<uint8_t> to_rgb() const {
        int width = de265_get_image_width(img, 0);
        int height = de265_get_image_height(img, 0);
        de265_chroma chroma = de265_get_chroma_format(img);

        int y_stride, cb_stride, cr_stride;
        const uint8_t* y_ptr = de265_get_image_plane(img, 0, &y_stride);
        const uint8_t* cb_ptr = de265_get_image_plane(img, 1, &cb_stride);
        const uint8_t* cr_ptr = de265_get_image_plane(img, 2, &cr_stride);

        if (!y_ptr) return py::array_t<uint8_t>();

        py::array_t<uint8_t> result({height, width, 3});
        auto r = result.mutable_unchecked<3>();

        // Optimized BT.601 conversion
        for (int y = 0; y < height; ++y) {
            int y_off = y * y_stride;
            
            // Chroma offsets
            int cy = y;
            if (chroma == de265_chroma_420) cy >>= 1;
            int c_off = cy * cb_stride; // Assuming cb_stride == cr_stride

            for (int x = 0; x < width; ++x) {
                int cx = x;
                if (chroma == de265_chroma_420 || chroma == de265_chroma_422) cx >>= 1;

                float Y = (float)y_ptr[y_off + x];
                float Cb = cb_ptr ? (float)cb_ptr[c_off + cx] : 128.0f;
                float Cr = cr_ptr ? (float)cr_ptr[c_off + cx] : 128.0f;

                float R = 1.164f * (Y - 16.0f) + 1.596f * (Cr - 128.0f);
                float G = 1.164f * (Y - 16.0f) - 0.391f * (Cb - 128.0f) - 0.813f * (Cr - 128.0f);
                float B = 1.164f * (Y - 16.0f) + 2.018f * (Cb - 128.0f);

                r(y, x, 0) = (uint8_t)std::max(0.0f, std::min(255.0f, R));
                r(y, x, 1) = (uint8_t)std::max(0.0f, std::min(255.0f, G));
                r(y, x, 2) = (uint8_t)std::max(0.0f, std::min(255.0f, B));
            }
        }
        return result;
    }

    const de265_image* get_ptr() const { return img; }

private:
    const de265_image* img;
    bool release_on_delete;
    de265_decoder_context* ctx;
};

class Decoder {
public:
    Decoder() {
        ctx = de265_new_decoder();
    }

    ~Decoder() {
        if (ctx) {
            de265_free_decoder(ctx);
        }
    }

    de265_error start_worker_threads(int threads) {
        return de265_start_worker_threads(ctx, threads);
    }

    de265_error push_data(py::bytes data, de265_PTS pts) {
        std::string s = data;
        return de265_push_data(ctx, s.data(), (int)s.size(), pts, nullptr);
    }

    void push_end_of_NAL() { de265_push_end_of_NAL(ctx); }
    void push_end_of_frame() { de265_push_end_of_frame(ctx); }
    de265_error flush_data() { return de265_flush_data(ctx); }

    py::tuple decode() {
        int more = 0;
        de265_error err;
        {
            py::gil_scoped_release release;
            err = de265_decode(ctx, &more);
        }
        return py::make_tuple(err, (bool)more);
    }

    std::unique_ptr<PyImage> get_next_picture() {
        const de265_image* img = de265_get_next_picture(ctx);
        if (!img) return nullptr;
        return std::unique_ptr<PyImage>(new PyImage(img, true, ctx));
    }

    void reset() { de265_reset(ctx); }

    int get_number_of_input_bytes_pending() { return de265_get_number_of_input_bytes_pending(ctx); }
    int get_highest_TID() { return de265_get_highest_TID(ctx); }
    int get_current_TID() { return de265_get_current_TID(ctx); }
    void set_limit_TID(int tid) { de265_set_limit_TID(ctx, tid); }
    void set_framerate_ratio(int percent) { de265_set_framerate_ratio(ctx, percent); }
    int change_framerate(int more_vs_less) { return de265_change_framerate(ctx, more_vs_less); }

    void set_parameter_bool(de265_param p, bool v) { de265_set_parameter_bool(ctx, p, v ? 1 : 0); }
    void set_parameter_int(de265_param p, int v) { de265_set_parameter_int(ctx, p, v); }
    bool get_parameter_bool(de265_param p) { return de265_get_parameter_bool(ctx, p) != 0; }

private:
    de265_decoder_context* ctx = nullptr;
};

PYBIND11_MODULE(_de265, m) {
    py::enum_<de265_error>(m, "de265_error")
        .value("OK", DE265_OK)
        .value("ERROR_NO_SUCH_FILE", DE265_ERROR_NO_SUCH_FILE)
        .value("ERROR_COEFFICIENT_OUT_OF_IMAGE_BOUNDS", DE265_ERROR_COEFFICIENT_OUT_OF_IMAGE_BOUNDS)
        .value("ERROR_CHECKSUM_MISMATCH", DE265_ERROR_CHECKSUM_MISMATCH)
        .value("ERROR_CTB_OUTSIDE_IMAGE_AREA", DE265_ERROR_CTB_OUTSIDE_IMAGE_AREA)
        .value("ERROR_OUT_OF_MEMORY", DE265_ERROR_OUT_OF_MEMORY)
        .value("ERROR_CODED_PARAMETER_OUT_OF_RANGE", DE265_ERROR_CODED_PARAMETER_OUT_OF_RANGE)
        .value("ERROR_IMAGE_BUFFER_FULL", DE265_ERROR_IMAGE_BUFFER_FULL)
        .value("ERROR_CANNOT_START_THREADPOOL", DE265_ERROR_CANNOT_START_THREADPOOL)
        .value("ERROR_LIBRARY_INITIALIZATION_FAILED", DE265_ERROR_LIBRARY_INITIALIZATION_FAILED)
        .value("ERROR_LIBRARY_NOT_INITIALIZED", DE265_ERROR_LIBRARY_NOT_INITIALIZED)
        .value("ERROR_WAITING_FOR_INPUT_DATA", DE265_ERROR_WAITING_FOR_INPUT_DATA)
        .value("ERROR_CANNOT_PROCESS_SEI", DE265_ERROR_CANNOT_PROCESS_SEI)
        .value("ERROR_PARAMETER_PARSING", DE265_ERROR_PARAMETER_PARSING)
        .value("ERROR_NO_INITIAL_SLICE_HEADER", DE265_ERROR_NO_INITIAL_SLICE_HEADER)
        .value("ERROR_PREMATURE_END_OF_SLICE", DE265_ERROR_PREMATURE_END_OF_SLICE)
        .value("ERROR_UNSPECIFIED_DECODING_ERROR", DE265_ERROR_UNSPECIFIED_DECODING_ERROR)
        .value("ERROR_NOT_IMPLEMENTED_YET", DE265_ERROR_NOT_IMPLEMENTED_YET)
        .value("WARNING_NO_WPP_CANNOT_USE_MULTITHREADING", DE265_WARNING_NO_WPP_CANNOT_USE_MULTITHREADING)
        .value("WARNING_WARNING_BUFFER_FULL", DE265_WARNING_WARNING_BUFFER_FULL)
        .value("WARNING_PREMATURE_END_OF_SLICE_SEGMENT", DE265_WARNING_PREMATURE_END_OF_SLICE_SEGMENT)
        .value("WARNING_INCORRECT_ENTRY_POINT_OFFSET", DE265_WARNING_INCORRECT_ENTRY_POINT_OFFSET)
        .value("WARNING_CTB_OUTSIDE_IMAGE_AREA", DE265_WARNING_CTB_OUTSIDE_IMAGE_AREA)
        .export_values();

    py::enum_<de265_chroma>(m, "de265_chroma")
        .value("CHROMA_MONO", de265_chroma_mono)
        .value("CHROMA_420", de265_chroma_420)
        .value("CHROMA_422", de265_chroma_422)
        .value("CHROMA_444", de265_chroma_444)
        .export_values();

    py::enum_<de265_param>(m, "de265_param")
        .value("PARAM_BOOL_SEI_CHECK_HASH", DE265_DECODER_PARAM_BOOL_SEI_CHECK_HASH)
        .value("PARAM_DUMP_SPS_HEADERS", DE265_DECODER_PARAM_DUMP_SPS_HEADERS)
        .value("PARAM_DUMP_VPS_HEADERS", DE265_DECODER_PARAM_DUMP_VPS_HEADERS)
        .value("PARAM_DUMP_PPS_HEADERS", DE265_DECODER_PARAM_DUMP_PPS_HEADERS)
        .value("PARAM_DUMP_SLICE_HEADERS", DE265_DECODER_PARAM_DUMP_SLICE_HEADERS)
        .value("PARAM_ACCELERATION_CODE", DE265_DECODER_PARAM_ACCELERATION_CODE)
        .value("PARAM_SUPPRESS_FAULTY_PICTURES", DE265_DECODER_PARAM_SUPPRESS_FAULTY_PICTURES)
        .value("PARAM_DISABLE_DEBLOCKING", DE265_DECODER_PARAM_DISABLE_DEBLOCKING)
        .value("PARAM_DISABLE_SAO", DE265_DECODER_PARAM_DISABLE_SAO)
        .export_values();

    m.def("get_version", []() { return std::string(de265_get_version()); });
    m.def("get_error_text", [](int err) { return std::string(de265_get_error_text((de265_error)err)); });
    m.def("isOk", [](int err) { return (bool)de265_isOK((de265_error)err); });
    m.def("set_verbosity", &de265_set_verbosity);

    py::class_<PyImage>(m, "Image")
        .def_property_readonly("pts", &PyImage::get_pts)
        .def_property_readonly("chroma_format", &PyImage::get_chroma_format)
        .def("get_width", &PyImage::get_width)
        .def("get_height", &PyImage::get_height)
        .def("get_bits_per_pixel", &PyImage::get_bits_per_pixel)
        .def("get_plane", &PyImage::get_plane)
        .def("get_nal_header", &PyImage::get_nal_header)
        .def_property_readonly("full_range", &PyImage::get_full_range_flag)
        .def_property_readonly("colour_primaries", &PyImage::get_colour_primaries)
        .def_property_readonly("transfer_characteristics", &PyImage::get_transfer_characteristics)
        .def_property_readonly("matrix_coefficients", &PyImage::get_matrix_coefficients)
        .def("to_rgb", &PyImage::to_rgb)
        .def("get_image_ptr", [](PyImage &self) {
            return py::capsule(self.get_ptr(), "de265_image");
        });

    py::class_<Decoder>(m, "decoder")
        .def(py::init<>())
        .def("start_worker_threads", &Decoder::start_worker_threads)
        .def("push_data", &Decoder::push_data, py::arg("data"), py::arg("pts") = 0)
        .def("push_end_of_NAL", &Decoder::push_end_of_NAL)
        .def("push_end_of_frame", &Decoder::push_end_of_frame)
        .def("flush_data", &Decoder::flush_data)
        .def("decode", &Decoder::decode)
        .def("get_next_picture", &Decoder::get_next_picture)
        .def("reset", &Decoder::reset)
        .def("get_number_of_input_bytes_pending", &Decoder::get_number_of_input_bytes_pending)
        .def("get_highest_TID", &Decoder::get_highest_TID)
        .def("get_current_TID", &Decoder::get_current_TID)
        .def("set_limit_TID", &Decoder::set_limit_TID)
        .def("set_framerate_ratio", &Decoder::set_framerate_ratio)
        .def("change_framerate", &Decoder::change_framerate)
        .def("set_parameter_bool", &Decoder::set_parameter_bool)
        .def("set_parameter_int", &Decoder::set_parameter_int)
        .def("get_parameter_bool", &Decoder::get_parameter_bool);
}

