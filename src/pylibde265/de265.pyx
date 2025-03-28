from libc.stdint cimport uint32_t,int64_t,uint8_t
from libc.stdio cimport printf
from cython.parallel import prange
import numpy as np
cimport numpy as cnp
# from scipy.ndimage import zoom  
from typing import Union
from pylibde265 cimport de265

def get_version() -> str:
    return de265.de265_get_version().decode('ascii')

def get_error_text(err_number: int) -> str:
    return de265.de265_get_error_text(err_number).decode('ascii')

def isOk(err_number: int) -> bool:
    return de265.de265_isOK(err_number)

def set_verbosity(level: int) -> None:
    de265.de265_set_verbosity(level)

        
cdef class decoder(object):
    cdef int threads
    cdef int buffer_size
    cdef de265.de265_decoder_context* ctx
    cdef readonly int w,h,chroma,bps,pts,matrix_coeff
    cdef readonly int wC,hC

    def __cinit__(self,int threads,int buffer_size=102400):
        self.ctx = de265.de265_new_decoder()
        de265.de265_start_worker_threads(self.ctx,threads)

    def __init__(self,int threads,int buffer_size=102400):
        self.buffer_size = buffer_size

    def __dealloc__(self):
        de265.de265_free_decoder(self.ctx)

    def load(self,str vedio_path):
        buffer = bytearray(self.buffer_size)
        cdef char* ba = buffer
        cdef int user_data = 0
        cdef int pts = 0

        data = open(vedio_path, "rb")

        bytes_read = data.readinto(buffer)

        while bytes_read > 0:
            dec_error = de265.de265_push_data(self.ctx, ba, bytes_read, pts, &user_data)
            # print([dec_error,bytes_read])
            pts += bytes_read
            bytes_read = data.readinto(buffer)

        dec_error = de265.de265_flush_data(self.ctx)
        data.close()

        return dec_error

    cdef cnp.ndarray decode_frame(self):
        cdef int more = 1
        cdef const uint8_t* bufferY = NULL
        cdef const uint8_t* bufferCb = NULL
        cdef const uint8_t* bufferCr = NULL
        cdef int ystride = 0, cstride = 0
        cdef cnp.ndarray image
        cdef unsigned char[:, :, ::1] image_view
        cdef int i, j

        while more > 0:
            more = 0
            
            with nogil:
                dec_error = de265.de265_decode(self.ctx, &more)
                # print(f'decode:{dec_error},more?{more}')
                image_ptr = de265.de265_get_next_picture(self.ctx)

                if image_ptr == NULL:
                    # print("Image pointer is null -> not yielding any image")
                    continue
                    
                # print('get image')
                self.w = de265.de265_get_image_width(image_ptr,0)
                self.h = de265.de265_get_image_height(image_ptr,0)
                self.chroma = de265.de265_get_chroma_format(image_ptr)
                self.bps = de265.de265_get_bits_per_pixel(image_ptr,0)
                self.pts = de265.de265_get_image_PTS(image_ptr)
                self.matrix_coeff = de265.de265_get_image_matrix_coefficients(image_ptr)
                
                if self.chroma == 1: # 4:2:0
                    self.wC = self.w // 2
                    self.hC = self.h // 2
                elif self.chroma == 2: # 4:2:2
                    self.wC = self.w // 2
                    self.hC = self.h
                elif self.chroma == 3: # 4:4:4
                    self.wC = self.w
                    self.hC = self.h
                else: # chroma==0
                    raise ValueError(f"unsupport chroma format:{self.chroma}")
           
                bufferY = de265.de265_get_image_plane(image_ptr,0,&ystride)
                bufferCb = de265.de265_get_image_plane(image_ptr,1,&cstride)
                bufferCr = de265.de265_get_image_plane(image_ptr,2,&cstride)
            
            image = np.empty((self.h, self.w, 3), dtype=np.uint8)

            planeY = np.frombuffer(bufferY[0:self.h*self.w], dtype='uint8').reshape((self.h, self.w))  
            planeCb = np.frombuffer(bufferCb[0:self.hC*self.wC], dtype='uint8').reshape((self.hC, self.wC))
            planeCr = np.frombuffer(bufferCr[0:self.hC*self.wC], dtype='uint8').reshape((self.hC, self.wC))
            
            #planeCb = zoom(planeCb,(self.w//self.wC,self.h//self.hC),order=0)
            #planeCr = zoom(planeCr,(self.w//self.wC,self.h//self.hC),order=0)

            planeCb = planeCb.repeat(self.w // self.wC, axis=1).repeat(self.h // self.hC, axis=0)
            planeCr = planeCr.repeat(self.w // self.wC, axis=1).repeat(self.h // self.hC, axis=0)

            image[:, :, 0] = planeY
            image[:, :, 1] = planeCb
            image[:, :, 2] = planeCr
            
            return image

        return None

    def decode(self):
        next_image = self.decode_frame()
        while next_image is not None:
            yield next_image
            next_image = self.decode_frame()
            self.free_image()
                 
    def free_image(self):
        de265.de265_release_next_picture(self.ctx)

    def get_highest_TID(self) -> int:
        return de265.de265_get_highest_TID(self.ctx)

    def get_current_TID(self) -> int:
        return de265.de265_get_current_TID(self.ctx)

    def set_limit_TID(self, ttd: int):
        de265.de265_set_limit_TID(self.ctx,ttd)

    def set_framerate_ratio(self, percent: int):
        # 0 ~ 100 (%)
        de265.de265_set_framerate_ratio(self.ctx, percent)

    def change_framerate(self, more_vs_less: int) -> int:
        # 1: more, -1: less
        return de265.de265_change_framerate(self.ctx, more_vs_less)

    def set_parameter(self, param: int, value: Union[int, bool]):
        if type(value) == bool:
            de265.de265_set_parameter_bool(self.ctx, param, value)
        elif type(value) == int:
            de265.de265_set_parameter_int(self.ctx, param, value)

    def get_parameter(self, param: int) -> bool:
        return bool(de265.de265_get_parameter_bool(self.ctx, param))