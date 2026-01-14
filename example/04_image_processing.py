import pylibde265.de265 as de265
from PIL import Image as PILImage
import numpy as np
import os

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"
OUTPUT_DIR = "output_frames"

def main():
    """
    Demonstrates how to access pixel data, convert to RGB, and save images using Pillow.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    dec = de265.decoder()
    
    print(f"Decoding {VIDEO_PATH} and saving frames to '{OUTPUT_DIR}'...")
    
    frame_count = 0
    for img in dec.load_file(VIDEO_PATH):
        # 1. Convert to RGB
        # to_rgb() returns a standard numpy array (height, width, 3)
        rgb_array = img.to_rgb()
        
        # Save RGB image using Pillow
        pil_img = PILImage.fromarray(rgb_array)
        rgb_filename = os.path.join(OUTPUT_DIR, f"frame_{frame_count}_rgb.png")
        pil_img.save(rgb_filename)
        print(f"Saved {rgb_filename}")
        
        # 2. Access Raw YUV Planes
        # yuv() returns (y, u, v) numpy arrays. 
        # u and v can be None if the image is monochrome.
        y, u, v = img.yuv()
        
        print(f"  Y plane shape: {y.shape}")
        if u is not None:
            print(f"  U plane shape: {u.shape}")
        
        # Save Luma (Y) plane as grayscale image
        y_img = PILImage.fromarray(y)
        y_filename = os.path.join(OUTPUT_DIR, f"frame_{frame_count}_y.jpg")
        y_img.save(y_filename)
        print(f"Saved {y_filename}")
        
        frame_count += 1
        
    print("Done.")

if __name__ == "__main__":
    main()
