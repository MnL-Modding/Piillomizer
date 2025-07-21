import io
import os
import pathlib
import struct
import sys
import random

from mnllib.n3ds import fs_std_romfs_path
from mnllib.dt import SOUND_DATA_PATH

#For just shuffling the music already in the game
def shuffle(input_folder, mode):
    OFFSET = 0x034A3E2C
    with fs_std_romfs_path(SOUND_DATA_PATH, data_dir=input_folder).open('r+b') as file:
        file.seek(OFFSET + 0x04)
        record_count, = struct.unpack('<I', file.read(4))
        file.seek(OFFSET + 0x20)
        record_offsets_lengths = []
        for i in range(record_count):
            index, length, offset, padding = struct.unpack('<IIII', file.read(16))
            record_offsets_lengths.append((offset, length))
        records = []
        for offset, length in record_offsets_lengths:
            file.seek(OFFSET + offset)
            records.append(file.read(length))

        static_records = records[25:29]
        del records[25:29]
        if not(mode):
            random.shuffle(records)
        else:
            old_records = records
            records = []
            randi = random.randint(0,51)
            positions = [[7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 28, 29, 31, 32, 33, 35, 37, 38, 40, 41, 42],[0, 5, 6, 21, 26, 51],
                         [1, 2, 4, 10, 23, 25, 30, 36, 39, 43, 44, 45, 46, 49, 50], [3, 22, 27, 47, 48], [34]]
            has_done = []
            for i in range(52):
                if i in positions[0]:
                    while not(randi in positions[0]) or randi in has_done:
                        randi = positions[0][random.randint(0, len(positions[0])-1)]
                if i in positions[1]:
                    while not(randi in positions[1]) or randi in has_done:
                        randi = positions[1][random.randint(0, len(positions[1])-1)]
                if i in positions[2]:
                    while not(randi in positions[2]) or randi in has_done:
                        randi = positions[2][random.randint(0, len(positions[2])-1)]
                if i in positions[3]:
                    while not(randi in positions[3]) or randi in has_done:
                        randi = positions[3][random.randint(0, len(positions[3])-1)]
                if i in positions[4]:
                    while not(randi in positions[4]) or randi in has_done:
                        randi = positions[4][random.randint(0, len(positions[4])-1)]
                records.append(old_records[randi])
                has_done.append(randi)
        records[25:25] = static_records

        file.seek(OFFSET + 0x20)
        offset = record_offsets_lengths[0][0]
        for record in records:
            file.write(struct.pack('<IIII', 0, len(record), offset, 0))
            offset += len(record)
        file.seek(OFFSET + record_offsets_lengths[0][0])
        for record in records:
            file.write(record)

#For randomly importing based on a directory
def import_random(section, input_folder, filenames_all, mode):
    folder = pathlib.Path(input_folder)
    with fs_std_romfs_path(SOUND_DATA_PATH, data_dir=folder).open('r+b') as sound_data:
        while (section_type := int.from_bytes(sound_data.read(4), 'little')) != section:
            sound_data.seek(0x4, os.SEEK_CUR)
            if (next_section_offset_data := sound_data.read(4)) == b'':
                print(f"Section {section} not found!", file=sys.stderr)
                sys.exit(3)
            next_section_offset, = struct.unpack('<I', next_section_offset_data)
            sound_data.seek(next_section_offset - 0xC, os.SEEK_CUR)
        section_offset = sound_data.tell() - 0x4
        record_count, next_section_offset, data_start_offset = struct.unpack('<III', sound_data.read(12))
        sound_data.seek(0x10 + record_count * 16, os.SEEK_CUR)
        name_table = sound_data.read(data_start_offset - 0x20 - record_count * 16)
        name_table_io = io.BytesIO(name_table)
        record_offsets_lengths = []
        for i in range(record_count):
            index, length, offset, padding = struct.unpack('<IIII', sound_data.read(16))
            if i == 25 or i == 26 or i == 27 or i == 28:
                record_offsets_lengths.append((offset, length))
        records = []
        for offset, length in record_offsets_lengths:
            sound_data.seek(0x034A3E2C + offset)
            records.append(sound_data.read(length))
        filenames = []
        randi = random.randint(0, len(filenames_all[0])-1)
        has_done = [[],[],[],[],[],[]]
        category = 0
        for i in range(52):
            if mode:
                if i == 0 or i == 5 or i == 6 or i == 21 or i == 26 or i == 51:
                    category = 1
                if i == 1 or i == 2 or i == 4 or i == 10 or i == 23 or i == 25 or i == 30 or i == 36 or i == 39 or (i >= 43 and i <= 46) or i == 49 or i == 50:
                    category = 2
                if i == 3 or i == 22 or i == 27 or i == 47 or i == 48:
                    category = 3
                if (i >= 7 and i <= 9) or (i >= 11 and i <= 20) or i == 24 or i == 28 or i == 29 or i == 31 or i == 32 or i == 33 or i == 35 or i == 37 or i == 38 or (i >= 40 and i <= 42):
                    category = 0
                if i == 34:
                    category = 4
            else:
                category = random.randint(0,4)
                randi = random.randint(0, len(filenames_all[category])-1)
            while randi in has_done[category] or randi > len(filenames_all[category]):
                if not(mode):
                    category = random.randint(0,5)
                randi = random.randint(0, len(filenames_all[category])-1)
            filenames.append(filenames_all[category][randi])
            has_done[category].append(randi)
        sound_data.seek(section_offset + next_section_offset)
        sound_data_remainder = bytearray(sound_data.read())

        new_records_header = bytearray()
        new_section_data = bytearray()
        for file in range(len(filenames)):
            if file == 25:
                for i in range(4):
                    section_data_len = len(record_offsets_lengths[i])
                    offset = 0x20 + record_count * 16 + len(name_table) + section_data_len
                    new_section_data += records[i]
                    new_records_header += struct.pack('<III4x', 0, len(new_section_data) - section_data_len, offset)
            print(f"Packing {filenames[file]}...")
            section_data_len = len(new_section_data)
            offset = 0x20 + record_count * 16 + len(name_table) + section_data_len
            with (folder / f'{filenames[file]}').open('rb') as f:
                new_section_data += f.read()
            new_records_header += struct.pack('<III4x', 0, len(new_section_data) - section_data_len, offset)
        new_section_data += b'\x00' * ((-len(new_section_data)) % 4)
        print("Saving file...")
        sound_data.seek(section_offset + 0x4)
        sound_data.write(struct.pack('<III',
            record_count,
            0x20 + len(new_records_header) + len(name_table) + len(new_section_data),
            0x20 + len(new_records_header) + len(name_table),
        ))
        sound_data.seek(0x10, os.SEEK_CUR)
        sound_data.write(new_records_header)
        sound_data.write(name_table)
        sound_data.write(new_section_data)
        sound_data_remainder_offset = sound_data.tell()
        section_offset = 0
        while section_offset < len(sound_data_remainder):
            sound_data_remainder[section_offset + 0x10:section_offset + 0x14] = struct.pack('<I', sound_data_remainder_offset + section_offset)
            section_offset += struct.unpack_from('<I', sound_data_remainder, offset=section_offset + 0x8)[0]
        sound_data.write(sound_data_remainder)
        sound_data.truncate()
