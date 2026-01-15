<div align="center">
  <p>
    <a href="https://github.com/Puiching-Memory/pylibde265" target="_blank">
      <img width="100%" src="./multimedia/image/title.png" alt="pylibde265 head image"></a>
  </p>

<div>
    <a href=""><img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="windows:support"></a>
    <a href=""><img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="linux:support"></a>
    <a href=""><img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white" alt="macos:support"></a>
    <br>
    <a href=""><img src="https://img.shields.io/github/downloads/Puiching-Memory/pylibde265/total" alt="downloads:all"></a>
    <a href=""><img src="https://img.shields.io/github/downloads/Puiching-Memory/pylibde265/latest/total" alt="downloads:latest_verson"></a>
    <a href=""><img src="https://img.shields.io/pypi/dm/pylibde265" alt="downloads-dm:pypi"></a>
    <a href=""><img src="https://img.shields.io/pypi/v/pylibde265" alt="version:pypi"></a>
    <a href=""><img src="https://img.shields.io/github/directory-file-count/Puiching-Memory/pylibde265" alt="count:file/dir"></a>
    <a href=""><img src="https://img.shields.io/github/repo-size/Puiching-Memory/pylibde265" alt="count:size"></a>
  </div>

  [中文](README_zh.md) | [English](README.md)

</div>

# pylibde265

Decode HEVC(H.265) video in python.

### Warning! This repository is still in early release, the code is subject to frequent disruptive changes, and we cannot guarantee compatibility with the current version.

# Concept

<div>
  <a href=""><img src="./multimedia/image/vedio_steam.svg" alt="image:vedio_steam"></a>
</div>

Common video files, such as .mp4, are containers that include video streams (HEVC encoded) and audio streams (AAC encoded).

libde265 is responsible for decoding the HEVC encoded video stream into raw bitstreams.

Starting from v0.1.0, pylibde265 includes a lightweight MP4 demuxer that supports decoding HEVC video streams directly from .mp4/.mov files.

# Quick Start

```bash
pip install pylibde265
```

```python
import pylibde265.de265
import matplotlib.pyplot as plt
import os

# Initialize decoder (specify number of threads)
dec = pylibde265.de265.decoder(threads=os.cpu_count() or 1)

# Stream load and decode HEVC (.265/.hevc) file
for img in dec.load_file("your_video.h265"):
    print(f"Frame PTS: {img.pts}, {img.width()}x{img.height()}")
    
    # Get raw YUV components (numpy view, no copy)
    # y, cb, cr = img.yuv()
    
    # Convert to RGB (C++ accelerated, supports 420/422/444 and 8-12bit)
    rgb = img.to_rgb()
    
    plt.imshow(rgb)
    plt.show()
    break
```

![example_preview.png](./multimedia/image/example.png)

## Advanced Usage: Memory Stream Processing

If you are processing stream data from network or memory:

```python
dec = pylibde265.de265.decoder()
with open("stream.h265", "rb") as f:
    while True:
        chunk = f.read(4096)
        if not chunk: break
        
        dec.push_data(chunk)
        for img in dec.decode():
             # Process image
             process(img.to_rgb())
```

## Direct MP4 Decoding

```python
import pylibde265

demuxer = pylibde265.FileDemuxer("video.mp4")
decoder = pylibde265.decoder()

# Get video info
print(f"FPS: {demuxer.get_fps()}, Total frames: {len(demuxer)}")

# Initialize with headers (VPS/SPS/PPS)
decoder.push_data(demuxer.get_headers())

# Iterate through packets
for frame_data in demuxer:
    decoder.push_data(frame_data)
    for img in decoder.decode():
        # Process image (e.g., convert to RGB)
        rgb = img.to_rgb()
```

# More Examples

This project provides detailed example codes located in the `example/` directory, covering aspects from basic decoding to visualization:

*   **[01_basic_decoding.py](example/01_basic_decoding.py)**: Basic file decoding introduction.
*   **[02_stream_decoding.py](example/02_stream_decoding.py)**: Memory/Network stream data processing.
*   **[03_metadata_config.py](example/03_metadata_config.py)**: Access metadata like PTS, resolution, NAL Headers, and parameter configuration.
*   **[04_image_processing.py](example/04_image_processing.py)**: Save frames as images, access raw YUV data.
*   **[05_visualization.py](example/05_visualization.py)**: Visualization of H.265 coding structures (Coding Blocks, Motion Vectors, etc.).
*   **[06_mp4_decoding.py](example/06_mp4_decoding.py)**: Direct MP4 file decoding example.
*   **[07_visual_player.py](example/07_visual_player.py)**: Visual player with a progress bar and FPS-synced playback using OpenCV and tqdm.

For detailed instructions, please refer to [example/README.md](example/README.md).

# Performance

* **High Performance C++ Core**: All pixel processing and color conversion (YUV to RGB) has been fully migrated to the C++ layer, using `pybind11` for zero-copy data exchange.
* **Multi-threading Support**: Fully utilizes libde265's multi-threaded decoding capabilities, performing excellently on multi-core processors.
* **Performance Benchmarks (720p H.265)**:
    * **Decoding Speed**: > 100 FPS (single frame ~8ms).
    * **Color Conversion**: ~6ms (C++ accelerated, supports 4:2:0/4:2:2/4:4:4).
    * **Total Throughput**: Can stably reach 30+ FPS real-time playback rate under 4 threads.

Specific performance data (based on `test/bench_performance.py`):

| Threads | Decode (ms) | RGB Conversion (ms) | Total FPS |
| :----- | :-------- | :------------ | :------- |
| 1      | 73.18     | 6.20          | 12.6     |
| 4      | 27.64     | 5.72          | 30.0     |
| 16     | 22.19     | 5.79          | 35.7     |

# Build from Source

## Requirements
- C++11 compatible compiler (Windows: VS 2022 / GCC / Clang)
- CMake 3.15+
- Python 3.9+

## Use uv (Recommended)

1. Clone repository: `git clone https://github.com/Puiching-Memory/pylibde265.git`
2. Install dependencies and build automatically:

```bash
# Create and activate environment
uv venv
.venv\Scripts\activate

# Install in editable mode (internally calls CMake to build C++ modules)
uv pip install -e .[dev]
```

## Running Tests

Standardized tests are provided using `pytest`:

```bash
pytest test/
```

# Roadmap

* [x] **High Performance C++ Color Conversion**: Support various sampling formats and bit depths.
* [x] **Stream Data Loading**: Support `push_data` real-time decoding.
* [x] **Demuxer**: Built-in lightweight demuxer supporting standard and Fragmented MP4 (fMP4).
* [ ] **Hardware Acceleration**: Integrate DXVA2/D3D11VA.


# Acknowledgements

Author:

* @梦归云帆 (MengGuiYunFan)

References:

* [libde265](https://github.com/strukturag/libde265)--C/C++ repo: Author [@strukturag](https://github.com/strukturag)
* [minimp4](https://github.com/lieff/minimp4)--The demuxer kernel in this project: Author [@lieff](https://github.com/lieff)
* [pyde265](https://github.com/kloppjp/pyde265)--Provided py bindings for linux: Author [@kloppjp](https://github.com/kloppjp)

Stats Badges:

* https://dev.to/envoy_/150-badges-for-github-pnk
* https://shields.io/

Data Analysis:

* https://pypistats.org/packages/pylibde265
