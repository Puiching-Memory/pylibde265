#import pylibde265 as decode
import pylibde265.pyde265

print(dir(pylibde265.pyde265))

import time
import PIL.Image
import numpy as np
import cupy as cp 

print(pylibde265.pyde265.get_version())


#vedio_path = './Kinkaku-ji.h265'
vedio_path = r"D:\GitHub\pylibde265\multimedia\video\Kinkaku-ji.h265"

dec = pylibde265.pyde265.decode_decoder(10)

with open(vedio_path,'rb') as data:
    re = dec.load(data)
    frame = 0
    for re in dec.decode():
        start_t = time.time()
        frame += 1
        #print(re['pts'])
        #print(re['ttd'],re['ttd_max'])
        #print(re)
        image_data = re['image']
        image_data = cp.asnumpy(image_data)
        image = PIL.Image.fromarray(image_data,mode='YCbCr')
        
        with open('./cache/py.txt','a') as file:
            print(time.time()-start_t,file=file)
        #image.save(f'./cache/{str(frame).zfill(9)}.jpg')
        #image.show()
        