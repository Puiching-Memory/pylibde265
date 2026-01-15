# pylibde265 Examples

This directory contains examples demonstrating how to use the `pylibde265` library for H.265/HEVC video decoding.

## Examples List

1.  **[01_basic_decoding.py](01_basic_decoding.py)**
    *   Basic usage of `decoder.load_file()`.
    *   Iterating through frames.

2.  **[02_stream_decoding.py](02_stream_decoding.py)**
    *   Advanced usage for streaming data (e.g., network streams).
    *   Using `decoder.push_data()` and `decoder.decode()`.

3.  **[03_metadata_config.py](03_metadata_config.py)**
    *   Accessing frame metadata (PTS, resolution, chroma format, NAL headers).
    *   Configuring decoder parameters (e.g., disabling deblocking).

4.  **[04_image_processing.py](04_image_processing.py)**
    *   Converting decoded frames to RGB.
    *   Accessing raw YUV planes.
    *   Saving frames to disk using Pillow (PIL).

5.  **[05_visualization.py](05_visualization.py)**
    *   Visualizing decoded frames using `matplotlib` (requires `pip install matplotlib`).

6.  **[06_mp4_decoding.py](06_mp4_decoding.py)**
    *   Directly decoding H.265 streams from MP4/MOV files using `FileDemuxer`.

7.  **[07_visual_player.py](07_visual_player.py)**
    *   Interactive visual player using OpenCV.
    *   Real-time playback speed control based on extracted video FPS.
    *   Progress bar display using `tqdm`.

## Prerequisites

Install module dependencies:

```bash
pip install -e .
pip install matplotlib pillow numpy
```

## Running Examples

Execute the python scripts directly:

```bash
python examples/01_basic_decoding.py
```
