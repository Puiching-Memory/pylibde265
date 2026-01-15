import cv2
import pylibde265
import argparse
import sys
import time
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='pylibde265 Visual Player with Progress Bar')
    parser.add_argument('input', help='Input MP4 file path')
    parser.add_argument('--scale', type=float, default=0.5, help='Visualization scale (default: 0.5)')
    args = parser.parse_args()

    try:
        # 1. Initialize demuxer
        demuxer = pylibde265.FileDemuxer(args.input)
        
        # 2. Get headers (VPS/SPS/PPS)
        headers = demuxer.get_headers()
        
        # 3. Initialize decoder
        decoder = pylibde265.decoder()
        if headers:
            decoder.push_data(headers)
        
        # 4. Get total frames and FPS for progress bar & playback
        total_frames = len(demuxer)
        fps = demuxer.get_fps()
        print(f"Total frames to process: {total_frames}")
        print(f"Video FPS: {fps:.2f}")

        # 5. Process loop with progress bar
        frame_delay = int(1000 / fps) if fps > 0 else 1
        with tqdm(total=total_frames, desc="Decoding") as pbar:
            for packet in demuxer:
                if packet:
                    decoder.push_data(packet)
                    
                    # Pull all available images from decoder
                    for img in decoder.decode():
                        # Convert to RGB (NumPy array)
                        rgb = img.to_rgb()
                        
                        # Convert RGB to BGR for OpenCV
                        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                        
                        # Resize for display
                        if args.scale != 1.0:
                            h, w = bgr.shape[:2]
                            bgr = cv2.resize(bgr, (int(w * args.scale), int(h * args.scale)))
                        
                        # Show frame
                        cv2.imshow('pylibde265 Player', bgr)
                        
                        # Update progress bar
                        pbar.update(1)
                        
                        # Handle keyboard events (controlled by FPS)
                        key = cv2.waitKey(frame_delay) & 0xFF
                        if key == ord('q'):
                            print("\nStopped by user.")
                            return
                        elif key == ord(' '): # Pause
                            cv2.waitKey(0)

        cv2.destroyAllWindows()
        print("\nDecoding finished.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
