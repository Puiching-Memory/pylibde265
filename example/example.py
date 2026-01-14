"""
to run this example, you need install pylibde265 and matplotlib
"""

import pylibde265.de265
import matplotlib.pyplot as plt
import os

print(f"libde265 version: {pylibde265.de265.get_version()}")
print(f"pylibde265 version: {pylibde265.__version__}")

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"
NUMBER_OF_THREADS = os.cpu_count() or 1

dec = pylibde265.de265.decoder(NUMBER_OF_THREADS)

frame = 0
for img in dec.load_file(VIDEO_PATH):
    frame += 1

    print(f"frame ------{frame}------")
    print(f"width: {img.width()} height: {img.height()}")
    print(f"chroma: {img.chroma_format} pts: {img.pts}")
    
    # Use the new C++ accelerated color conversion
    image_matrix = img.to_rgb()

    plt.imshow(image_matrix)
    plt.title(f"PTS: {img.pts} ({img.width()}x{img.height()}) - C++ RGB")
    plt.show()

    if frame >= 1:
        break
