import pylibde265.de265 as de265
import os

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"

def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"File not found: {VIDEO_PATH}")
        return

    # Initialize decoder
    dec = de265.decoder()
    
    print(f"Decoding {VIDEO_PATH}...")
    
    # Use load_file for simple file decoding
    # It returns a generator that yields Image objects
    count = 0
    for img in dec.load_file(VIDEO_PATH):
        print(f"Frame {count}: {img.width()}x{img.height()}, PTS={img.pts}")
        count += 1
        
    print(f"Decoded {count} frames.")

if __name__ == "__main__":
    main()
