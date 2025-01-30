# cython:language_level=3

from libc.stdint cimport uint32_t,int64_t,uint8_t
from libc.stdio cimport printf
import numpy as np
from scipy.ndimage import zoom  
import time
from pylibde265 cimport pyde265

def get_version():
    return pyde265.de265_get_version().decode('ascii')

cdef class decode_decoder(object):
    cdef pyde265.de265_decoder_context* ctx

    def __cinit__(self,threads:int):
        self.ctx = pyde265.de265_new_decoder()
        pyde265.de265_start_worker_threads(self.ctx,threads)

        pyde265.de265_set_parameter_bool(self.ctx,pyde265.de265_param.DE265_DECODER_PARAM_DISABLE_DEBLOCKING,0)
        pyde265.de265_set_parameter_bool(self.ctx,pyde265.de265_param.DE265_DECODER_PARAM_DISABLE_SAO,0)


    def __dealloc__(self):
        pyde265.de265_free_decoder(self.ctx)


    def load(self,data):
        buffer = bytearray(102400)
        cdef char* ba = buffer
        cdef int user_data = 0
        cdef int pts = 0
        bytes_read = data.readinto(buffer)

        while bytes_read > 0:
            dec_error = pyde265.de265_push_data(self.ctx, ba, bytes_read, pts, &user_data)
            #logger.debug([dec_error,bytes_read])
            pts += bytes_read
            bytes_read = data.readinto(buffer)

        dec_error = pyde265.de265_flush_data(self.ctx)
        return dec_error

    def decode_frame(self):
        
        cdef int more = 1
        cdef const uint8_t* bufferY = <uint8_t *>0
        cdef const uint8_t* bufferCb = <uint8_t *>0
        cdef const uint8_t* bufferCr = <uint8_t *>0
        cdef int outstride = 0
        
        while more > 0:
            start_t = time.time()
            more = 0
            
            with nogil:
                dec_error = pyde265.de265_decode(self.ctx, &more)
                #logger.debug(f'decode:{dec_error},more?{more}')
                image_ptr = pyde265.de265_get_next_picture(self.ctx)

                if image_ptr == NULL:
                    #logger.debug("Image pointer is null -> not yielding any image")
                    continue
            with open('./cache/dec.txt','a') as file:
                print(time.time()-start_t,file=file)
            #logger.debug('get image')
            w = pyde265.de265_get_image_width(image_ptr,0)
            h = pyde265.de265_get_image_height(image_ptr,0)
            chroma = pyde265.de265_get_chroma_format(image_ptr)
            bps = pyde265.de265_get_bits_per_pixel(image_ptr,0)
            pts = pyde265.de265_get_image_PTS(image_ptr)
            ttd_max = pyde265.de265_get_highest_TID(self.ctx)
            ttd =  pyde265.de265_get_current_TID(self.ctx)
            #print(w,h,chroma,bps,pts)
            
            if chroma == 1: #4:2:0
                wC = w // 2
                hC = h // 2
            elif chroma == 2:#4:2:2
                wC = w // 2
                hC = h
            elif chroma == 3: #4:4:4
                wC = w
                hC = h
            else: #chroma==0
                print(f'unsupport chroma format:{chroma}')
           
            bufferY = pyde265.de265_get_image_plane(image_ptr,0,&outstride)
            planeY = np.frombuffer(bufferY[0:h*w], dtype='uint8').reshape((h, w))  
            
            bufferCb = pyde265.de265_get_image_plane(image_ptr,1,&outstride)
            planeCb = np.frombuffer(bufferCb[0:hC*wC], dtype='uint8').reshape((hC, wC)) 
            planeCb = zoom(planeCb,(w//wC,h//hC),order=0)

            bufferCr = pyde265.de265_get_image_plane(image_ptr,2,&outstride)
            planeCr = np.frombuffer(bufferCr[0:hC*wC], dtype='uint8').reshape((hC, wC))
            planeCr = zoom(planeCr,(w//wC,h//hC),order=0)

            image = np.dstack((planeY,planeCb,planeCr))
            
            
            return {'width':w,
                    'height':h,
                    'chroma':chroma,
                    'bps':bps,
                    'pts':pts,
                    'ttd_max':ttd_max,
                    'ttd':ttd,
                    'image':image}

        return None

    def decode(self):
        next_image = self.decode_frame()
        while next_image is not None:
            yield next_image
            next_image = self.decode_frame()
            self.free_image()
            
            
        
    def free_image(self):
        pyde265.de265_release_next_picture(self.ctx)

    def stop(self):
        pass

    def get_PTS(self):
        pass




