# cython:language_level=3

from libc.stdint cimport uint32_t,int64_t,uint8_t
from libc.stdio cimport printf
import numpy as np
from scipy.ndimage import zoom  
from pylibde265 cimport pyde265

def get_version():
    return pyde265.de265_get_version().decode('ascii')

cdef class decoder(object):
    cdef int threads
    cdef int buffer_size
    cdef pyde265.de265_decoder_context* ctx
    cdef readonly int w,h,chroma,bps,pts,ttd_max,ttd

    def __cinit__(self,int threads,int buffer_size=102400):
        self.ctx = pyde265.de265_new_decoder()
        pyde265.de265_start_worker_threads(self.ctx,threads)

        self.buffer_size = buffer_size


    def __dealloc__(self):
        pyde265.de265_free_decoder(self.ctx)


    def load(self,str vedio_path):
        buffer = bytearray(self.buffer_size)
        cdef char* ba = buffer
        cdef int user_data = 0
        cdef int pts = 0

        data = open(vedio_path, "rb")

        bytes_read = data.readinto(buffer)

        while bytes_read > 0:
            dec_error = pyde265.de265_push_data(self.ctx, ba, bytes_read, pts, &user_data)
            # print([dec_error,bytes_read])
            pts += bytes_read
            bytes_read = data.readinto(buffer)

        dec_error = pyde265.de265_flush_data(self.ctx)
        data.close()

        return dec_error


    cdef decode_frame(self):
        cdef int more = 1
        cdef const uint8_t* bufferY = NULL
        cdef const uint8_t* bufferCb = NULL
        cdef const uint8_t* bufferCr = NULL
        cdef int outstride = 0
        
        while more > 0:
            more = 0
            
            with nogil:
                dec_error = pyde265.de265_decode(self.ctx, &more)
                # print(f'decode:{dec_error},more?{more}')
                image_ptr = pyde265.de265_get_next_picture(self.ctx)

                if image_ptr == NULL:
                    # print("Image pointer is null -> not yielding any image")
                    continue
            # print('get image')
            self.w = pyde265.de265_get_image_width(image_ptr,0)
            self.h = pyde265.de265_get_image_height(image_ptr,0)
            self.chroma = pyde265.de265_get_chroma_format(image_ptr)
            self.bps = pyde265.de265_get_bits_per_pixel(image_ptr,0)
            self.pts = pyde265.de265_get_image_PTS(image_ptr)
            self.ttd_max = pyde265.de265_get_highest_TID(self.ctx)
            self.ttd =  pyde265.de265_get_current_TID(self.ctx)
            
            if self.chroma == 1: #4:2:0
                wC = self.w // 2
                hC = self.h // 2
            elif self.chroma == 2:#4:2:2
                wC = self.w // 2
                hC = self.h
            elif self.chroma == 3: #4:4:4
                wC = self.w
                hC = self.h
            else: # chroma==0
                raise ValueError(f"unsupport chroma format:{self.chroma}")
           
            bufferY = pyde265.de265_get_image_plane(image_ptr,0,&outstride)
            planeY = np.frombuffer(bufferY[0:self.h*self.w], dtype='uint8').reshape((self.h, self.w))  
            
            bufferCb = pyde265.de265_get_image_plane(image_ptr,1,&outstride)
            planeCb = np.frombuffer(bufferCb[0:hC*wC], dtype='uint8').reshape((hC, wC)) 
            planeCb = zoom(planeCb,(self.w//wC,self.h//hC),order=0)

            bufferCr = pyde265.de265_get_image_plane(image_ptr,2,&outstride)
            planeCr = np.frombuffer(bufferCr[0:hC*wC], dtype='uint8').reshape((hC, wC))
            planeCr = zoom(planeCr,(self.w//wC,self.h//hC),order=0)

            image = np.dstack((planeY,planeCb,planeCr))
            
            return image

        return None


    def decode(self):
        next_image = self.decode_frame()
        while next_image is not None:
            yield next_image
            next_image = self.decode_frame()
            self.free_image()
            
            
    def free_image(self):
        pyde265.de265_release_next_picture(self.ctx)

