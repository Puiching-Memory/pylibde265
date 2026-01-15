import pylibde265
import sys

def main():
    filename = "multimedia/video/test_mp4s/output_standard.mp4"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    print(f"Opening MP4 file: {filename}")
    
    try:
        demuxer = pylibde265.FileDemuxer(filename)
        print(f"Total samples: {len(demuxer)}")
        print(f"FPS: {demuxer.get_fps():.2f}")
    except Exception as e:
        print(f"Error opening MP4: {e}")
        return

    # Use pythonic wrapper
    decoder = pylibde265.decoder(threads=4)

    # Push VPS/SPS/PPS configuration
    headers = demuxer.get_headers()
    print(f"Headers size: {len(headers)} bytes")
    decoder.push_data(headers)

    count = 0
    # Process headers/start decoding
    for img in decoder.decode():
        count += 1
        print(f"Decoded frame {count}: {img.width()}x{img.height()}")

    # Iterate over frames
    for frame_data in demuxer:
        decoder.push_data(frame_data)
        for img in decoder.decode():
             count += 1
             print(f"Decoded frame {count}: {img.width()}x{img.height()} pts={img.pts}")

    # Flush remaining frames
    decoder.flush()
    for img in decoder.decode():
         count += 1
         print(f"Decoded frame {count} (flushed)")

    print(f"Total decoded frames: {count}")

if __name__ == "__main__":
    main()
