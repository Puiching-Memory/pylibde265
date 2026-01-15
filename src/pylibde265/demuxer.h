#pragma once
#include <string>
#include <vector>
#include <cstdio>
#include <stdexcept>
#include <algorithm>
#include <pybind11/pybind11.h>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#ifdef ERROR
#undef ERROR
#endif
#define fseek_64 _fseeki64
#define ftell_64 _ftelli64
static std::wstring utf8_to_utf16(const std::string& utf8) {
    if (utf8.empty()) return L"";
    int size = MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), -1, NULL, 0);
    std::wstring utf16(size, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), -1, &utf16[0], size);
    return utf16;
}
#else
#define fseek_64 fseeko
#define ftell_64 ftello
#endif

// Include minimp4 declaration first to define types
#include "minimp4.h"

// Define implementation and include again to pull in code
// Ideally this handled in a .cpp, but for single-header requirement we do it here.
// Note: This header should essentially be treated as a private implementation header
// included by only one source file, or guarded/namespaced carefully.
#ifndef MINIMP4_IMPLEMENTATION_INCLUDED
#define MINIMP4_IMPLEMENTATION_INCLUDED
#define MINIMP4_IMPLEMENTATION
#include "minimp4.h"
#endif

namespace py = pybind11;

class FileDemuxer {
    struct Sample {
        uint64_t offset;
        uint32_t size;
    };
    FILE* f = nullptr;
    MP4D_demux_t mp4 = {0};
    unsigned track_idx = 0;
    unsigned sample_idx = 0;
    std::vector<Sample> all_samples;
    std::string headers; // VPS/SPS/PPS
    int nal_length_size = 4;
    double fps = 25.0;
    
    static uint32_t read_u32_be(FILE* f) {
        uint8_t b[4];
        if (fread(b, 1, 4, f) != 4) return 0;
        return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3];
    }

    static uint64_t read_u64_be(FILE* f) {
        uint64_t h = read_u32_be(f);
        uint64_t l = read_u32_be(f);
        return (h << 32) | l;
    }

    static uint16_t read_u16(const uint8_t* p) {
        return (uint16_t)((p[0] << 8) | p[1]);
    }

    void parse_hevc_decoder_configuration_record(const uint8_t* data, size_t size) {
        if (size < 23) return;
        uint8_t version = data[0];
        if (version != 1) return;
        
        // byte 21: lengthSizeMinusOne
        nal_length_size = (data[21] & 0x03) + 1;
        
        // byte 22: numOfArrays
        int num_arrays = data[22];
        const uint8_t* p = data + 23;
        const uint8_t* end = data + size;
        
        for (int i = 0; i < num_arrays; i++) {
            if (p + 3 > end) break;
            // byte 0: array_completeness(1), reserved(1), NAL_unit_type(6)
            int num_nalus = read_u16(p + 1);
            p += 3;
            
            for (int k = 0; k < num_nalus; k++) {
                if (p + 2 > end) break;
                int nal_len = read_u16(p);
                p += 2;
                if (p + nal_len > end) break;
                
                // Append Start Code 00 00 00 01
                headers.append("\x00\x00\x00\x01", 4);
                headers.append((const char*)p, nal_len);
                p += nal_len;
            }
        }
    }

    void scan_fragments(int64_t fsize, uint32_t target_track_id) {
        fseek_64(f, 0, SEEK_SET);
        while (ftell_64(f) < fsize) {
            int64_t atom_start = ftell_64(f);
            uint32_t size = read_u32_be(f);
            uint32_t type = read_u32_be(f);
            if (feof(f)) break;

            int64_t atom_size = size;
            if (size == 1) atom_size = (int64_t)read_u64_be(f);
            if (size == 0) atom_size = fsize - atom_start;

            if (type == BOX_moof) {
                parse_moof(atom_start, atom_size, target_track_id);
            }
            fseek_64(f, (int64_t)(atom_start + atom_size), SEEK_SET);
        }
    }

    void parse_moof(int64_t moof_start, int64_t moof_size, uint32_t target_track_id) {
        int64_t end = moof_start + moof_size;
        uint32_t current_track_id = 0;
        uint64_t base_data_offset = moof_start;
        uint32_t default_sample_size = 0;
        uint32_t default_sample_duration = 0;

        while (ftell_64(f) < end) {
            int64_t atom_start = ftell_64(f);
            uint32_t size = read_u32_be(f);
            uint32_t type = read_u32_be(f);
            if (feof(f)) break;

            int64_t atom_size = size;
            if (size == 1) atom_size = (int64_t)read_u64_be(f);

            if (type == BOX_traf) {
                // container box, just continue
            } else if (type == BOX_tfhd) {
                uint32_t ver_flags = read_u32_be(f);
                current_track_id = read_u32_be(f);
                
                base_data_offset = moof_start;
                if (ver_flags & 0x000001) base_data_offset = read_u64_be(f);
                if (ver_flags & 0x000002) read_u32_be(f); // sample-description-index
                if (ver_flags & 0x000008) default_sample_duration = read_u32_be(f); // default-sample-duration
                if (ver_flags & 0x000010) default_sample_size = read_u32_be(f);
                
                fseek_64(f, (int64_t)(atom_start + atom_size), SEEK_SET);
            } else if (type == BOX_trun) {
                if (current_track_id == target_track_id) {
                    uint32_t flags = read_u32_be(f);
                    uint32_t s_count = read_u32_be(f);
                    int32_t data_off = (flags & 0x01) ? (int32_t)read_u32_be(f) : 0;
                    if (flags & 0x04) read_u32_be(f); // first_sample_flags

                    // Improve FPS detection: if we have default_sample_duration and no FPS yet
                    if (fps == 25.0 && default_sample_duration > 0 && mp4.track[track_idx].timescale > 0) {
                        fps = (double)mp4.track[track_idx].timescale / default_sample_duration;
                    }

                    uint64_t current_offset = base_data_offset + data_off;
                    for (uint32_t i=0; i<s_count; i++) {
                        if (flags & 0x100) {
                            uint32_t s_duration = read_u32_be(f);
                            if (fps == 25.0 && s_duration > 0 && mp4.track[track_idx].timescale > 0) {
                                fps = (double)mp4.track[track_idx].timescale / s_duration;
                            }
                        }
                        uint32_t s_size = (flags & 0x200) ? read_u32_be(f) : default_sample_size;
                        if (flags & 0x400) read_u32_be(f); // flags
                        if (flags & 0x800) read_u32_be(f); // composition_offset
                        
                        all_samples.push_back({current_offset, s_size});
                        current_offset += s_size;
                    }
                }
                fseek_64(f, (int64_t)(atom_start + atom_size), SEEK_SET);
            } else {
                fseek_64(f, (int64_t)(atom_start + atom_size), SEEK_SET);
            }
        }
    }

public:
    FileDemuxer(const std::string& filename) {
#ifdef _WIN32
        f = _wfopen(utf8_to_utf16(filename).c_str(), L"rb");
#else
        f = fopen(filename.c_str(), "rb");
#endif
        if (!f) throw std::runtime_error("Could not open file: " + filename);
        
        auto read_callback = [](int64_t offset, void *buffer, size_t size, void *token) -> int {
            FILE* f = (FILE*)token;
            if (fseek_64(f, (int64_t)offset, SEEK_SET) != 0) return 1;
            return fread(buffer, 1, size, f) != size;
        };
        
        fseek_64(f, 0, SEEK_END);
        int64_t fsize_val = ftell_64(f);
        fseek_64(f, 0, SEEK_SET);
        
        if (fsize_val == -1) {
            fclose(f);
            throw std::runtime_error("ftell failed for file: " + filename);
        }
        
        if (!MP4D_open(&mp4, read_callback, f, fsize_val)) {
                fclose(f);
                MP4D_close(&mp4); 
                f = nullptr; 
                throw std::runtime_error("MP4D_open failed for file: " + filename);
        }
        
        bool found = false;
        // Priority search for HEVC track
        for (unsigned i = 0; i < mp4.track_count; i++) {
            if (mp4.track[i].object_type_indication == MP4_OBJECT_TYPE_HEVC) {
                track_idx = i;
                found = true;
                break;
            }
        }
        
        // Fallback: Any Video track
        if (!found) {
                for (unsigned i = 0; i < mp4.track_count; i++) {
                if (mp4.track[i].handler_type == MP4D_HANDLER_TYPE_VIDE) {
                        track_idx = i;
                        found = true;
                        break;
                }
                }
        }

        if (!found) {
            MP4D_close(&mp4);
            fclose(f);
            f = nullptr;
            throw std::runtime_error("No video track found");
        }

        auto* track = &mp4.track[track_idx];
        
        // Collect standard samples
        for (unsigned i = 0; i < track->sample_count; i++) {
            unsigned frame_bytes, timestamp, duration;
            MP4D_file_offset_t offset = MP4D_frame_offset(&mp4, track_idx, i, &frame_bytes, &timestamp, &duration);
            all_samples.push_back({(uint64_t)offset, frame_bytes});
            if (i == 0 && duration > 0) {
                fps = (double)track->timescale / duration;
            }
        }

        // Scan for fragments
        scan_fragments(fsize_val, track->track_id);

        if (track->dsi && track->dsi_bytes > 22) {
            parse_hevc_decoder_configuration_record(track->dsi, track->dsi_bytes);
        }
    }

    ~FileDemuxer() {
        MP4D_close(&mp4);
        if (f) fclose(f);
    }
    
    FileDemuxer(const FileDemuxer&) = delete;
    FileDemuxer& operator=(const FileDemuxer&) = delete;

    py::bytes get_headers() {
        return py::bytes(headers);
    }

    size_t total_samples() const {
        return all_samples.size();
    }

    double get_fps() const {
        return fps;
    }

    py::object get_next_frame() { // returns bytes or None
        if (sample_idx >= all_samples.size()) return py::none();
        
        uint64_t offset = all_samples[sample_idx].offset;
        uint32_t frame_bytes = all_samples[sample_idx].size;
        sample_idx++;
        
        std::vector<uint8_t> buffer(frame_bytes);
        if (fseek_64(f, (int64_t)offset, SEEK_SET) != 0) return py::none();
        if (fread(buffer.data(), 1, frame_bytes, f) != frame_bytes) return py::none();
        
        // Replace length prefixes with start codes
        std::string annexb_frame;
        size_t pos = 0;
        while (pos + nal_length_size <= buffer.size()) {
            uint32_t len = 0;
            if (nal_length_size == 4) {
                len = (buffer[pos] << 24) | (buffer[pos+1] << 16) | (buffer[pos+2] << 8) | buffer[pos+3];
            } else if (nal_length_size == 2) {
                len = (buffer[pos]<<8) | buffer[pos+1];
            } else if (nal_length_size == 1) {
                len = buffer[pos];
            } else { // 3
                len = (buffer[pos]<<16) | (buffer[pos+1]<<8) | buffer[pos+2];
            }
            
            pos += nal_length_size;
            if (pos + len > buffer.size()) break; // truncated
            
            annexb_frame.append("\x00\x00\x00\x01", 4);
            annexb_frame.append((const char*)buffer.data() + pos, len);
            pos += len;
        }
        
        return py::bytes(annexb_frame);
    }

    FileDemuxer& iter() { return *this; }
    py::bytes next() {
        py::object res = get_next_frame();
        if (res.is_none()) throw py::stop_iteration();
        return res;
    }
};
