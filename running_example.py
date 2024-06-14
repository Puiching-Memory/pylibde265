import pylibde265
import time
import PIL.Image
import numpy as np
import cupy as cp 

print(pylibde265.get_version())


#vedio_path = './Kinkaku-ji.h265'
vedio_path = './2233.hevc'

dec = pylibde265.pylibde265_decoder(10)

with open(vedio_path,'rb') as data:
    re = dec.load(data)
    frame = 0
    for re in dec.decode():
        frame += 1
        #print(re['pts'])
        #print(re['ttd'],re['ttd_max'])
        image_data = re['image']
        image_data = cp.asnumpy(image_data)
        image = PIL.Image.fromarray(image_data,mode='YCbCr')
        image.save(f'./cache/{str(frame).zfill(9)}.jpg')
        