import pylibde265.pyde265
import matplotlib.pyplot as plt
import colour

print(dir(pylibde265.pyde265))
print(f"libde265 version: {pylibde265.pyde265.get_version()}")

VEDIO_PATH = r"multimedia\video\Kinkaku-ji.h265"
NUMBER_OF_THREADS = 10

dec = pylibde265.pyde265.decode_decoder(NUMBER_OF_THREADS)

with open(VEDIO_PATH, "rb") as data:
    re = dec.load(data)
    frame = 0
    for re in dec.decode():
        frame += 1

        print(f"frame ------{frame}------")
        print(f"width: {re["width"]} height: {re['height']}")
        print(f"chroma: {re["chroma"]} bps: {re['bps']}")
        print(f"pts: {re['pts']} ttd: {re['ttd']} ttd_max: {re['ttd_max']}")

        image_martix = re["image"]
        image_martix = colour.YCbCr_to_RGB(
            image_martix,
            in_bits=8,
            in_int=True,
            in_legal=True,
            out_bits=8,
            out_legal=True,
        )
        plt.imshow(image_martix)
        plt.show()

        break
