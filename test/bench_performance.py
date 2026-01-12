import pylibde265.de265 as de265
import time
import os
import numpy as np

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"

def bench():
    if not os.path.exists(VIDEO_PATH):
        print(f"Video not found: {VIDEO_PATH}")
        return

    configs = [1, 2, 4, 8, 16]
    cpu_count = os.cpu_count() or 1
    configs = [c for c in configs if c <= cpu_count]

    print(f"{'Threads':<10} | {'Decode (ms)':<15} | {'RGB (ms)':<10} | {'Total FPS':<10}")
    print("-" * 55)

    for threads in configs:
        # Test
        decode_times = []
        rgb_times = []
        
        # We run 50 iterations to get a stable average
        for _ in range(50):
            # Clear previous results explicitly before creating new decoder
            frames = [] 
            dec = None 
            
            dec = de265.decoder(threads=threads)
            # Measure decode
            t0 = time.perf_counter()
            frames = list(dec.load_file(VIDEO_PATH))
            t1 = time.perf_counter()
            
            if frames:
                decode_times.append((t1 - t0) / len(frames))
                
                # Measure RGB (on the first frame)
                t2 = time.perf_counter()
                _ = frames[0].to_rgb()
                t3 = time.perf_counter()
                rgb_times.append(t3 - t2)
            
            # Explicitly clear before next iteration
            frames = []
            dec = None

        
        avg_d = np.mean(decode_times) * 1000
        avg_r = np.mean(rgb_times) * 1000
        fps = 1000 / (avg_d + avg_r)
        
        print(f"{threads:<10} | {avg_d:<15.2f} | {avg_r:<10.2f} | {fps:<10.1f}")

if __name__ == "__main__":
    try:
        bench()
    except Exception as e:
        import traceback
        traceback.print_exc()


