import struct
import sys

def find_box(f, target_type, max_depth=3, depth=0):
    while True:
        header = f.read(8)
        if not header:
            return None
        length, box_type = struct.unpack('>I4s', header)
        box_type = box_type.decode('ascii')
        if length == 1:
            length = struct.unpack('>Q', f.read(8))[0]
            content_length = length - 16
        elif length == 0:
            content_length = -1
        else:
            content_length = length - 8

        if box_type == target_type:
            return (box_type, content_length, f.tell())
        else:
            if depth < max_depth and box_type in ['moov', 'trak', 'mdia', 'minf', 'stbl']:
                pos = f.tell()
                result = find_box(f, target_type, max_depth, depth+1)
                f.seek(pos + content_length)
                if result:
                    return result
            else:
                f.seek(content_length, 1)

def parse_hvcc(data):
    pos = 0
    configuration_version = data[pos]
    pos += 1
    pos += 4  # general_profile_space(2b) + tier_flag(1b) + profile_idc(5b) + compatibility_flags(4B)
    pos += 6  # constraint_flags(6B)
    general_level_idc = data[pos]
    pos += 1
    length_size_minus_one = (data[pos] >> 4) & 0x03
    pos += 2  # skip reserved and numOfArrays

    num_arrays = data[pos]
    pos += 1

    nal_units = []
    for _ in range(num_arrays):
        array_completeness = (data[pos] >> 6) & 0x01
        nal_unit_type = data[pos] & 0x3F
        pos += 1
        num_nalus = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        for __ in range(num_nalus):
            nal_length = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            nal_data = data[pos:pos+nal_length]
            pos += nal_length
            nal_units.append((nal_unit_type, nal_data))
    return length_size_minus_one + 1, nal_units

def extract_h265(input_file, output_file):
    with open(input_file, 'rb') as f:
        # 查找moov盒子
        moov_info = find_box(f, 'moov')
        if not moov_info:
            raise ValueError("moov box not found")
        f.seek(moov_info[2])

        # 查找视频trak
        trak_pos = None
        while True:
            box_info = find_box(f, 'trak')
            if not box_info:
                break
            pos = f.tell()
            # 检查是否为视频track
            hdlr_info = find_box(f, 'hdlr')
            if hdlr_info:
                f.seek(hdlr_info[2])
                handler_type = f.read(4)
                if handler_type == b'vide':
                    trak_pos = pos - 8
                    break
            f.seek(pos + box_info[1])

        if not trak_pos:
            raise ValueError("Video track not found")

        f.seek(trak_pos)
        # 查找stsd盒子
        stsd_info = find_box(f, 'stsd')
        if not stsd_info:
            raise ValueError("stsd box not found")
        f.seek(stsd_info[2])
        f.read(4)  # 跳过entry count
        entry_type = f.read(4).decode('ascii')
        if entry_type not in ['hvc1', 'hev1']:
            raise ValueError("Not H.265 track")
        
        # 查找hvcC盒子
        hvcc_info = find_box(f, 'hvcC')
        if not hvcc_info:
            raise ValueError("hvcC box not found")
        f.seek(hvcc_info[2])
        hvcc_data = f.read(hvcc_info[1])
        length_size, nal_units = parse_hvcc(hvcc_data)

        # 提取参数集并写入输出文件
        with open(output_file, 'wb') as out:
            for nal_type, nal_data in nal_units:
                out.write(b'\x00\x00\x00\x01' + nal_data)

            # 解析stbl获取sample信息
            f.seek(trak_pos)
            stbl_info = find_box(f, 'stbl')
            f.seek(stbl_info[2])

            # 解析stsz获取sample大小
            stsz_info = find_box(f, 'stsz')
            f.seek(stsz_info[2])
            stsz_data = f.read(stsz_info[1])
            sample_size = struct.unpack('>I', stsz_data[4:8])[0]
            sample_count = struct.unpack('>I', stsz_data[8:12])[0]
            if sample_size == 0:
                sizes = struct.unpack(f'>{sample_count}I', stsz_data[12:12+4*sample_count])
            else:
                sizes = [sample_size] * sample_count

            # 解析stco获取chunk偏移
            stco_info = find_box(f, 'stco')
            if not stco_info:
                stco_info = find_box(f, 'co64')
            f.seek(stco_info[2])
            stco_data = f.read(stco_info[1])
            chunk_count = struct.unpack('>I', stco_data[4:8])[0]
            if stco_info[0] == 'stco':
                offsets = struct.unpack(f'>{chunk_count}I', stco_data[8:8+4*chunk_count])
            else:  # co64
                offsets = struct.unpack(f'>{chunk_count}Q', stco_data[8:8+8*chunk_count])

            # 解析stsc获取chunk到sample的映射
            f.seek(stbl_info[2])
            stsc_info = find_box(f, 'stsc')
            f.seek(stsc_info[2])
            stsc_data = f.read(stsc_info[1])
            entry_count = struct.unpack('>I', stsc_data[4:8])[0]
            entries = []
            pos = 8
            for _ in range(entry_count):
                first_chunk, samples_per_chunk, sample_desc_index = struct.unpack('>III', stsc_data[pos:pos+12])
                entries.append((first_chunk, samples_per_chunk))
                pos += 12

            # 重建chunk到sample的映射
            chunks = []
            current_entry = 0
            for i in range(chunk_count):
                while current_entry +1 < entry_count and i+1 >= entries[current_entry+1][0]:
                    current_entry +=1
                chunks.append(entries[current_entry][1])

            # 遍历所有chunk并读取sample数据
            file_pos = 0
            sample_index = 0
            for chunk_idx in range(chunk_count):
                chunk_offset = offsets[chunk_idx]
                samples_in_chunk = chunks[chunk_idx]
                for _ in range(samples_in_chunk):
                    if sample_index >= len(sizes):
                        break
                    size = sizes[sample_index]
                    f.seek(chunk_offset)
                    data = f.read(size)
                    chunk_offset += size
                    sample_index +=1

                    # 解析NAL单元
                    pos = 0
                    while pos < len(data):
                        if length_size == 4:
                            nal_length = struct.unpack('>I', data[pos:pos+4])[0]
                            pos +=4
                        elif length_size == 2:
                            nal_length = struct.unpack('>H', data[pos:pos+2])[0]
                            pos +=2
                        else:
                            raise ValueError("Unsupported length size")
                        nal_unit = data[pos:pos+nal_length]
                        pos += nal_length
                        out.write(b'\x00\x00\x00\x01' + nal_unit)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_h265.py input.mp4 output.h265")
        sys.exit(1)
    extract_h265(sys.argv[1], sys.argv[2])