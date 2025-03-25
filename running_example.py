"""
to run this example, you need install pylibde265 and matplotlib
---
here is my environment:
matplotlib==3.10.1
"""

import pylibde265.de265
import matplotlib.pyplot as plt
import os
import numpy as np

def ycbcr_to_rgb(ycbcr_image):
    """
    YCbCr --> RGB (BT.601)
    ---
    
    args:
        ycbcr_image: numpy.ndarray (height, width, 3) [0, 255]
    
    return:
        numpy.ndarray (height, width, 3) [0, 255]
    """
    ycbcr = ycbcr_image.astype(np.float32)
    height, width, _ = ycbcr.shape
    
    inv_matrix = np.array([
        [1.164,  0.0,   1.596],
        [1.164, -0.813, -0.391],
        [1.164,  2.018, 0.0]
    ])
    shift = np.array([16.0, 128.0, 128.0])
    
    ycbcr_shifted = ycbcr - shift
    rgb_linear = np.dot(ycbcr_shifted, inv_matrix.T)
    rgb = np.clip(rgb_linear, 0, 255).astype(np.uint8)
    
    return rgb

print(dir(pylibde265.de265))
print(f"libde265 version: {pylibde265.de265.get_version()}")
print(f"pylibde265 version: {pylibde265.__version__}")

VEDIO_PATH = "./multimedia/video/Kinkaku-ji.h265"
NUMBER_OF_THREADS = os.cpu_count()

decoder = pylibde265.de265.decoder(NUMBER_OF_THREADS)

error = decoder.load(VEDIO_PATH)
frame = 0
for image_martix in decoder.decode():
    frame += 1

    print(f"frame ------{frame}------")
    print(f"width: {decoder.w} height: {decoder.h}")
    print(f"chroma: {decoder.chroma} bps: {decoder.bps}")
    print(f"pts: {decoder.pts} matrix_coeff: {decoder.matrix_coeff}")
    print(f"current TID {decoder.get_current_TID()} / {decoder.get_highest_TID()}")


    image_martix = ycbcr_to_rgb(image_martix)
    plt.imshow(image_martix)
    plt.show()

    break