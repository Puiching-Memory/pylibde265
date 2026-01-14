import pylibde265.de265 as de265
import os
import time

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"

def main():
    """
    Simulates streaming decoding by reading chunks of data and pushing them to the decoder.
    Useful for network streams or custom file readers.
    """
    if not os.path.exists(VIDEO_PATH):
        print(f"File not found: {VIDEO_PATH}")
        return

    dec = de265.decoder()
    
    CHUNK_SIZE = 4096 * 4
    
    count = 0
    with open(VIDEO_PATH, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
                
            # Push raw H.265 bitstream data
            dec.push_data(data)
            
            # Retrieve available frames
            # decode() yields all frames that can be fully decoded from current buffer
            for img in dec.decode():
                 print(f"Stream Decoded Frame {count} PTS={img.pts}")
                 count += 1
                 
        # Flush the decoder to get remaining delayed frames (reordering)
        print("Flushing decoder...")
        dec.flush()
        for img in dec.decode():
             print(f"Flushed Frame {count} PTS={img.pts}")
             count += 1
             
    print(f"Total Stream Decoded: {count}")

if __name__ == "__main__":
    main()
