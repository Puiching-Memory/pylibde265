import pylibde265.de265 as de265
import os

def test_version():
    version = de265.get_version()
    print(f"libde265 version: {version}")
    assert version

def test_decoder_creation():
    dec = de265.decoder(threads=2)
    assert dec is not None
    print("Decoder created successfully")

def test_decode_loop():
    VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"
    if not os.path.exists(VIDEO_PATH):
        print(f"Skip test, file not found: {VIDEO_PATH}")
        return

    dec = de265.decoder(threads=2)
    count = 0
    for img in dec.load_file(VIDEO_PATH):
        assert img.width() > 0
        assert img.height() > 0
        y, cb, cr = img.yuv()
        assert y is not None
        count += 1
        if count >= 5:
            break
    
    print(f"Decoded {count} frames")

if __name__ == "__main__":
    test_version()
    test_decoder_creation()
    test_decode_loop()

