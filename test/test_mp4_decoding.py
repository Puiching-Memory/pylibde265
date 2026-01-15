import hashlib
import numpy as np
import pylibde265.de265 as de265
from pylibde265._de265 import FileDemuxer
import os
import pytest

REF_FILE = "multimedia/video/Kinkaku-ji.h265"
MP4_DIR = "multimedia/video/test_mp4s"

def calculate_checksum(img):
    md5 = hashlib.md5()
    y = img.plane(0)
    if y is not None:
        md5.update(y.tobytes())
    chroma = img.chroma_format
    if chroma != de265.ChromaFormat.CHROMA_MONO:
        u = img.plane(1)
        v = img.plane(2)
        if u is not None: md5.update(u.tobytes())
        if v is not None: md5.update(v.tobytes())
    return md5.hexdigest()

@pytest.fixture(scope="module")
def ref_checksums():
    if not os.path.exists(REF_FILE):
        pytest.skip(f"Reference file not found: {REF_FILE}")
    
    dec = de265.decoder()
    checksums = []
    for img in dec.load_file(REF_FILE):
        checksums.append(calculate_checksum(img))
    return checksums

def get_mp4_files():
    if not os.path.exists(MP4_DIR):
        return []
    return [f for f in os.listdir(MP4_DIR) if f.endswith(".mp4")]

@pytest.mark.parametrize("mp4_name", get_mp4_files())
def test_mp4_integrity(mp4_name, ref_checksums):
    mp4_path = os.path.join(MP4_DIR, mp4_name)
    demuxer = FileDemuxer(mp4_path)
    dec = de265.decoder()
    
    # Push headers
    headers = demuxer.get_headers()
    dec.push_data(headers)
    
    mp4_checksums = []
    for frame_data in demuxer:
        dec.push_data(frame_data)
        for img in dec.decode():
             mp4_checksums.append(calculate_checksum(img))
             
    dec.flush()
    for img in dec.decode():
         mp4_checksums.append(calculate_checksum(img))

    assert len(mp4_checksums) == len(ref_checksums), f"Frame count mismatch for {mp4_name}"
    
    for i in range(len(ref_checksums)):
        assert mp4_checksums[i] == ref_checksums[i], f"Checksum mismatch at frame {i} in {mp4_name}"
