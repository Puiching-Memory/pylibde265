"""
to run this example, you need install pylibde265 and matplotlib and colour-science package.
---
here is my environment:
matplotlib==3.10.0
colour-science==0.4.6
"""

import pylibde265.pyde265
import matplotlib.pyplot as plt
import colour
import os
from pyinstrument import Profiler

profiler = Profiler()
profiler.start()

print(dir(pylibde265.pyde265))
print(f"libde265 version: {pylibde265.pyde265.get_version()}")

VEDIO_PATH = "./multimedia/video/Kinkaku-ji.h265"
NUMBER_OF_THREADS = os.cpu_count()

decoder = pylibde265.pyde265.decoder(NUMBER_OF_THREADS)

error = decoder.load(VEDIO_PATH)
frame = 0
for image_martix in decoder.decode():
    frame += 1

    print(f"frame ------{frame}------")
    print(f"width: {decoder.w} height: {decoder.h}")
    print(f"chroma: {decoder.chroma} bps: {decoder.bps}")
    print(f"pts: {decoder.pts} ttd: {decoder.ttd} ttd_max: {decoder.ttd_max}")

    image_martix = colour.YCbCr_to_RGB(
        image_martix,
        in_bits=8,
        in_int=True,
        in_legal=True,
        out_bits=8,
        out_legal=True,
    )
    # plt.imshow(image_martix)
    # plt.show()

    break

profiler.stop()
print(profiler.output_text(unicode=True, color=True))