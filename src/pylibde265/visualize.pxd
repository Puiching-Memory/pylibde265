from pylibde265.image cimport de265_image
from libc.stdint cimport uint32_t,int64_t,uint8_t

cdef extern from "visualize.h" nogil:
    void draw_CB_grid(const de265_image* img, uint8_t* dst, int stride, uint32_t value, int pixelSize)
    void draw_TB_grid(const de265_image* img, uint8_t* dst, int stride, uint32_t value, int pixelSize)
    void draw_PB_grid(const de265_image* img, uint8_t* dst, int stride, uint32_t value, int pixelSize)
    void draw_PB_pred_modes(const de265_image* img, uint8_t* dst, int stride, int pixelSize)
    void draw_intra_pred_modes(const de265_image* img, uint8_t* dst, int stride, uint32_t value, int pixelSize)
    void draw_QuantPY(const de265_image* img, uint8_t* dst, int stride, int pixelSize)
    void draw_Motion(const de265_image* img, uint8_t* dst, int stride, int pixelSize)
    void draw_Slices(const de265_image* img, uint8_t* dst, int stride, int pixelSize)
    void draw_Tiles(const de265_image* img, uint8_t* dst, int stride, int pixelSize)
