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
    *   Using the `visualize` module to inspect internal H.265 coding structures.
    *   Visualizing Coding Blocks (CB), Prediction Blocks (PB), Transforms (TB), Motion Vectors, etc.

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
