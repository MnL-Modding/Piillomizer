import math
import struct
import random
import os
from tqdm import tqdm
from mldtr import randomize_repack
from mnllib.n3ds import fs_std_code_bin_path, fs_std_romfs_path
from mnllib.dt import FMAPDAT_PATH, NUMBER_OF_ROOMS, \
    determine_version_from_code_bin, load_enemy_stats, save_enemy_stats, FEventScriptManager, \
    FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS, FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS

def get_room(id):
    if 0x000 <= id <= 0x00C or id == 0x00F or id == 0x018 or id == 0x1C8 or 0x050 <= id <= 0x055:
        return "Mushrise Park"
    elif id == 0x00E or 0x010 <= id <= 0x017 or id == 0x019 or id == 0x01A or id == 0x05D or 0x60 <= id <= 0x62 or id == 0x0AF or 0x101 <= id <= 0x104 or id == 0x138 or id == 0x1DC or id == 0x28A:
        return "Dozing Sands"
    elif id == 0x01B or id == 0x01C or 0x056 <= id <= 0x05C or id == 0x063 or id == 0x064 or id == 0x1DE:
        return "Blimport"
    elif 0x01D <= id <= 0x030 or id == 0x032 or id == 0x0B0 or id == 0x09D or 0x0F1 <= id <= 0x0F3 or id == 0x199 or id == 0x19A or id == 0x1CD or id == 0x1CE:
        return "Dreamy Mushrise Park"
    elif 0x033 <= id <= 0x037 or id == 0x039 or 0x03C <= id <= 0x044 or 0x108 <= id <= 0x10A or id == 0x288:
        return "Wakeport"
    elif id == 0x038 or id == 0x03A or id == 0x03B or 0x045 <= id <= 0x04F:
        return "Driftwood Shore"
    elif 0x066 <= id <= 0x081 or id == 0x100 or id == 0x10B or id == 0x10C:
        return "Mount Pajamaja"
    elif id == 0x082 or 0x084 <= id <= 0x09B or 0x136 <= id <= 0x13B or id == 0x1D8:
        return "Pi'illo Castle"
    elif 0x0A1 <= id <= 0x0AE or 0x0D8 <= id <= 0x0DE or 0x0F4 <= id <= 0x0FA:
        return "Dreamy Pi'illo Castle"
    elif 0x0B1 <= id <= 0x0C7 or 0x0E4 <= id <= 0x0F0 or 0x13C <= id <= 0x13E or id == 0x1D6:
        return "Dreamy Dozing Sands"
    elif 0x0D2 <= id <= 0x0D6 or 0x161 <= id <= 0x182 or id == 0x1C9 or id == 0x1CA:
        return "Dreamy Driftwood Shore"
    elif 0x0FB <= id <= 0x0FD or 0x219 <= id <= 0x238:
        return "Dreamy Somnom Woods"
    elif id == 0x106 or 0x10D <= id <= 0x134 or id == 0x12B or id == 0x12C or id == 0x1CF or id == 0x1E1 or id == 0x294 or id == 0x295:
        return "Dreamy Wakeport"
    elif id == 0x13F or 0x1E7 <= id <= 0x20E or id == 0x250 or id == 0x290:
        return "Dreamy Mount Pajamaja"
    elif 0x140 <= id <= 0x160 or id == 0x218:
        return "Neo Bowser Castle"
    elif 0x183 <= id <= 0x196:
        return "Somnom Woods"
    elif 0x252 <= id <= 0x27B:
        return "Dreamy Neo Bowser Castle"
    else:
        return "Unknown"

def get_zone_id(room, id):
    #Returns the zone id corresponding to the room and item id being checked
    if (room == 0x000 or room == 0x001 or 0x006 <= room <= 0x008 or room == 0x00B or room == 0x1C8 or
        0x01E <= room <= 0x02F or room == 0x033 or room == 0x0B0 or room == 0x108 or room == 0x183):
        return 4
    elif room == 0x01B or room == 0x056 or room == 0x058 or room == 0x05B or room == 0x05C:
        return 0
    elif 0x084 <= room <= 0x0A7 or room == 0x136 or room == 0x1D8:
        return 1
    elif 0x002 <= room <= 0x005 or room == 0x009 or room == 0x00A or room == 0x00C or room == 0x018:
        if id == 0x43:
            return 4
        return 5
    elif 0x0F4 <= room <= 0x0FA:
        return 2
    elif 0x0AC <= room <= 0x0AE or 0x0D8 <= room <= 0x0DA or 0x0DB <= room <= 0x0DE or 0x139 <= room <= 0x13B:
        return 3
    elif (room == 0x00E or room == 0x012 or room == 0x038 or room == 0x045 or room == 0x046 or room == 0x04A or room == 0x04B or room == 0x04F or
          room == 0x05D or room == 0x062 or room == 0x0AF or room == 0x0B1 or 0x13C <= room <= 0x13E or 0x178 <= room <= 0x17A or room == 0x17E):
        if id == 0xff:
            return 8
        return 6
    elif (room == 0x010 or room == 0x011 or room == 0x013 or room == 0x014 or room == 0x017 or room == 0x019 or room == 0x060 or 0x0B2 <= room <= 0x0B9 or
        0x0EC <= room <= 0x0EE or room == 0x101 or room == 0x1D6 or room == 0x1DC or room == 0x28A):
        return 7
    elif (room == 0x01A or room == 0x061 or 0x0BA <= room <= 0x0C7 or 0x0E4 <= room <= 0x0EB or room == 0x0EF or room == 0x0F0 or
        0x102 <= room <= 0x104 or room == 0x138 or room == 0x292 or room == 0x293):
        return 8
    elif 0x034 <= room <= 0x036 or room == 0x039 or 0x03C <= room <= 0x044 or room == 0x106 or 0x10D <= room <= 0x122 or 0x12D <= room <= 0x130 or room == 0x288:
        if id == 0x5ec:
            return 10
        return 9
    elif room == 0x109 or room == 0x10A or 0x123 <= room <= 0x12C or 0x131 <= room <= 0x134 or room == 0x1CF or room == 0x1E1 or room == 0x294 or room == 0x295:
        return 10
    elif room == 0x066:
        return 11
    elif 0x067 <= room <= 0x073 or room == 0x081 or room == 0x13F or room == 0x1E7 or room == 0x1E8 or 0x208 <= room <= 0x20A or 0x20C <= room <= 0x20E:
        return 12
    elif 0x074 <= room <= 0x076 or 0x078 <= room <= room <= 0x07C or room == 0x100 or room == 0x10B or room == 0x10C or 0x205 <= room <= 0x207 or room == 0x250 or room == 0x290:
        if id == 0x64f:
            return 14
        return 13
    elif room == 0x077 or 0x07D <= room <= 0x080 or 0x1E9 <= room <= 0x1ED:
        return 14
    elif 0x1EE <= room <= 0x202 or room == 0x204:
        return 15
    elif (room == 0x03A or room == 0x03B or 0x047 <= room <= 0x049 or room == 0x04C or room == 0x04D or 0x0D2 <= room <= 0x0D4 or 0x173 <= room <= 0x177 or
          0x17B <= room <= 0x17D or 0x17F <= room <= 0x182):
        if id == 0x611 or id == 0x612:
            return 6
        return 16
    elif room == 0x0D5 or room == 0x0D6 or 0x161 <= room <= 0x172 or room == 0x1C9 or room == 0x1CA:
        return 17
    elif 0x184 <= room <= 0x189 or room == 0x234 or room == 0x235 or room == 0x238:
        return 18
    elif 0x18A <= room <= 0x194 or 0x219 <= room <= 0x223 or room == 0x236 or room == 0x237:
        return 19
    elif 0x0FB <= room <= 0x0FD or room == 0x195 or room == 0x196 or 0x224 <= room <= 0x233 or room == 0x29D:
        return 20
    elif 0x140 <= room <= 0x14B or 0x252 <= room <= 0x259:
        return 21
    elif 0x14C <= room <= 0x155 or room == 0x218 or 0x25A <= room <= 0x263:
        return 22
    elif 0x156 <= room <= 0x15C or 0x264 <= room <= 0x26D or room == 0x28F:
        return 23
    elif 0x26E <= room <= 0x27B:
        return 24
    return -1

def get_minimap(room_id):
    if get_room(room_id) == "Mushrise Park":
        return 0x245

def get_spot_type(spot):
    if spot[2] % 0x10 == 2:
        return 5
    elif spot[2] % 0x10 == 4:
        return 6
    elif spot[2] // 0x10000 == 1 and spot[2] % 0x10 != 0x8:
        if (spot[2] // 0x8000) % 2 == 1:
            return 2
        return 3
    elif (spot[2] // 0x8000) % 2 == 1 and spot[2] % 0x10 != 0x8:
        return 4
    elif spot[-2] == 0:
        return 1
    return 0

def find_index_in_2d_list(arr, target_value):
    for row_index, row in enumerate(arr):
        for col_index, element in enumerate(row):
            if element == target_value:
                return (row_index, col_index)
    return None  # Return None if the element is not found

def is_available(logic, key, settings):
    #Sets up the variables to check the logic
    available = True
    was_true = False
    for d in range(len(logic)-1):
        #Checks if you have the items needed for the check
        if (key[logic[d+1]] < 1 and logic[d+1] > -1) or logic[d+1] == -3 or ((logic[d+1] == 1 or logic[d+1] == 2) and key[0] == 0) or (logic[d+1] == 4 and key[3] == 0):
            available = False
        #If it's an or statement, it resets the generation for the next statement
        #while setting wasTrue depending on whether the chunk was true or not
        if logic[d+1] == -1:
            #try:
            #    if logic[0] == 87 and logic[1] == 15 and key[15] == 1:
            #        print(available)
            #except IndexError:
            #    pass
            if not available:
                available = True
            else:
                was_true = True
    if was_true:
        available = True
    return available
#46d8f468
def randomize_data(input_folder, stat_mult, settings, seed):
    with tqdm(total=962, desc="Initializing...") as pbar:
        #Sets the seed to what it was in main
        random.seed(seed)
        pbar.update(1)

        if settings[3][0] == -1:
            settings[3][0] = random.randint(0, 1)

        #An array containing the maximum values of each item
        max_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0]

        #Logic for each area in Dream Team [Blimport, Pi'illo Castle, Pi'illo Castle Dream's Deep, Under Blimport Bridge, Mushrise Park Main, Mushrise Park Hammers,
        # Dozing Sands Entrance, Dozing Sands Tracks, Dozing Sands Dreamstone,
        # Wakeport Main, Wakeport Ultibed, Mount Pajamaja Before Base, Mount Pajamaja Base Main, Mount Pajamaja Middle, Mount Pajamaja Peak, Mount Pajamaja Summit Dreampoint,
        # Driftwood Shore Main, Driftwood Shore Dream Egg Area, Somnom Woods Before First Pi'illo, Somnom Woods After First Pi'illo, Somnom Woods After Tracks,
        # Neo Bowser Castle Before First Spin Requirement, Neo Bowser Castle After First Spin R, Neo Bowser Castle After Kamek 3, Neo Bowser Castle Bowser's Dream]

        #The first entry in each chunk of logic means nothing, and is just there so you know what the room is.
        #After that, the key items are as follows:
        # -3 - NOT POSSIBLE
        # -2 - OR but ONLY WITH GLITCHES
        # -1 - OR Statement
        # 0 - Hammers
        # 1 - Mini Mario
        # 2 - Mole Mario
        # 3 - Spin Jump
        # 4 - Side Drill
        # 5 - Ball Hop
        # 6 - Luiginary Works
        # 7 - Luiginary Ball
        # 8 - Luiginary Stack Ground Pound
        # 9 - Luiginary Stack Spring Jump
        # 10 - Luiginary Cone Jump
        # 11 - Luiginary Cone Storm
        # 12 - Luiginary Ball Hookshot
        # 13 - Luiginary Ball Hammer
        # 14 - Access to Deep Pi'illo Castle
        # 15 - Blimport Bridge
        # 16 - Mushrise Park Gate
        # 17 - First Dozite
        # 18 - Track Dozite 1
        # 19 - Track Dozite 2
        # 20 - Track Dozite 3
        # 21 - Track Dozite 4
        # 22 - Access to Wakeport
        # 23 - Access to Mount Pajamaja
        # 24 - Dream Egg 1
        # 25 - Dream Egg 2
        # 26 - Dream Egg 3
        # 27 - Access to Neo Bowser Castle

        area_logic = [[0], [1, 14], [2, 14, 6, 7, 12, 13], [3, 15], [4, 15], [5, 15, 0], [6, 15, 16], [7, 15, 16, 17, 1, -1, 15, 16, 17, 2, -1, 15, 16, 1, 5, -1, 15, 16, 2, 5],
                      [8, 15, 16, 17, 18, 19, 20, 21, -1, 15, 16, 5], [9, 15, 22], [10, 14, 15, 16, 22, 1, 2, 4, 5, 6, 7, 8, 13],
                      [11, 1], [12, 23, 1, -1, 1, 5], [13, 1, 4, 5, -1, 23, 1, 4, 6, 8, 10], [14, 23, 1, 4, 6, 8, 10, -1, 1, 5], [15, 23, 1, 4, 6, 8, 10, 11, -1, 1, 4, 5, 6, 8, 10, 11],
                      [16, 15, 16, 1, 3], [17, 15, 16, 24, 1, 3, 6], [18, 15, 1, 5], [19, 15, 1, 4, 5, 6], [20, 15, 1, 2, 4, 5, 6], [21, 15, 27, 1, 5],
                      [22, 15, 27, 1, 3, 5], [23, 15, 27, 1, 3, 5, 6], [24, 15, 27, 1, 4, 5, 6, 7, 8, 10, 12, 13]]

        area_replace = []
        if settings[1][0] == 1:
            if settings[1][1] == 1:
                area_replace = [[7, 15, 16, 17, 1, -1, 15, 16, 17, 2], [8, 15, 16, 17, 18, 19, 20, 21], [10, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6, 7, 8, 13],
                                [11], [12, 23, 0], [13, 23, 0, 4, 6, 8, 10], [14, 23, 0, 4, 6, 8, 10], [15, 23, 0, 4, 6, 8, 10, 11], [16, 15, 16, 0, 3], [17, 15, 16, 24, 0, 3, 6],
                                [18, 15, 0, 5], [19, 15, 0, 4, 5, 6], [20, 15, 2, 4, 5, 6],
                                [21, 15, 27, 5], [22, 15, 27, 3, 5], [23, 15, 27, 0, 3, 5, 6], [24, 15, 27, 0, 4, 5, 6, 7, 8, 10, 12, 13]]
            else:
                area_replace = [[11], [12, 23, 0, -1, 0, 5], [13, 23, 0, 4, 5, 6, -1, 0, 4, 5], [14, 23, 0, 4, 6, 8, 10, -1, 0, 5], [15, 23, 0, 4, 6, 8, 10, 11, -1, 0, 4, 5, 6, 8, 10, 11],
                                [16, 15, 16, 0, 3], [17, 15, 16, 24, 0, 3, 6], [18, 15, 0, 5], [19, 15, 0, 4, 5, 6], [20, 15, 2, 4, 5, 6],
                                [21, 15, 27, 5], [22, 15, 27, 3, 5], [23, 15, 27, 0, 3, 5, 6], [24, 15, 27, 0, 4, 5, 6, 7, 8, 10, 12, 13]]
        elif settings[1][1] == 1:
            area_replace = [[7, 15, 16, 17, 1, -1, 15, 16, 17, 2], [8, 15, 16, 17, 18, 19, 20, 21], [10, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6, 7, 8, 13],
                            [12, 23, 1], [13, 23, 1, 4, 6, 8, 10], [14, 23, 1, 4, 6, 8, 10], [15, 23, 1, 4, 6, 8, 10, 11]]
        for a in area_replace:
            area_logic[a[0]] = a

        #Sets base stats to be added on, creating a custom level curve
        #[Level, HP, POW, DEF, SPEED, EXP, COINS]
        init_enemy_stats = [2, 8, 27 * stat_mult[0], 12, 15, 3 * stat_mult[1], 1]
        init_boss_stats = [0, 0, 0 * stat_mult[0], 0, 0, 0 * stat_mult[1], 0]

        if stat_mult[0] < 0:
            stat_mult[0] = 0xFFFF

        # Opens code.bin for enemy stat randomization
        code_bin_path = fs_std_code_bin_path(data_dir=input_folder)
        #enemy_stats_rand = []
        #boss_stats_rand = []
        #dream_boss_stats_rand = []
        #filler_stats_rand = []
        #for enemy in range(len(enemy_stats)):
        #    pbar.update(1)
        #    if stat_mult[0] > -1:
        #        enemy_stats[enemy].power *= stat_mult[0]
        #        if enemy_stats[enemy].power > 0xFFFF:
        #            enemy_stats[enemy].power = 0xFFFF
        #    else:
        #        enemy_stats[enemy].power = 0xFFFF
        #    if enemy == 87:
        #        enemy_stats[enemy].exp *= 4
        #    if stat_mult[1] > 0:
        #       enemy_stats[enemy].exp *= stat_mult[1]
        #        if enemy_stats[enemy].exp > 0xFFFF:
        #            enemy_stats[enemy].exp = 0xFFFF
        #    if enemy == 19 or enemy == 33 or enemy == 45 or enemy == 47 or enemy == 49 or enemy == 64 or enemy == 72 or enemy == 78 or enemy == 99 or enemy == 112 or enemy == 121 or enemy == 123 or enemy == 124:
        #        enemy_stats[enemy].hp *= 2
        #        enemy_stats[enemy].exp *= 5
        #        if enemy == 33:
        #            enemy_stats[enemy].exp *= 6
        #    elif enemy == 31 or enemy == 46:
        #        enemy_stats[enemy].exp *= 2
        #    elif enemy == 35:
        #        enemy_stats[enemy].exp *= 3
        #    elif enemy == 17:
        #        enemy_stats[enemy].hp *= 4
        #        enemy_stats[enemy].power *= 4
        #        enemy_stats[enemy].defense *= 4
        #        enemy_stats[enemy].speed = 0x1F
        #        enemy_stats[enemy].exp *= 4
        #    elif enemy == 107:
        #        enemy_stats[enemy].hp *= 2
        #        enemy_stats[enemy].power *= 2
        #        enemy_stats[enemy].defense *= 2
        #        enemy_stats[enemy].speed *= 2
        #        enemy_stats[enemy].exp *= 2
        #    if (enemy > 12 and not(14 <= enemy <= 16) and enemy != 20 and
        #            enemy != 22 and enemy != 24 and enemy != 26 and
        #            enemy != 28 and enemy != 32 and enemy != 34 and
        #            enemy != 40 and enemy != 43 and enemy != 44 and
        #            enemy != 51 and not(53 <= enemy <= 56) and
        #            enemy != 63 and enemy != 83 and enemy != 88 and enemy != 89 and enemy != 92 and
        #            enemy != 93 and enemy != 97 and enemy != 103 and enemy != 105 and enemy != 108 and
        #            enemy != 114 and enemy != 132 and not(134 <= enemy <= 136) and enemy < 139):
        #        #Appends data to enemy array if it's an enemy
        #        if (enemy == 13 or enemy == 18 or enemy == 25 or
        #                enemy == 27 or enemy == 29 or enemy == 38 or
        #                enemy == 39 or enemy == 41 or enemy == 48 or (58 <= enemy <= 61) or
        #                (68 <= enemy <= 71) or (85 <= enemy <= 94) or
        #                (100 <= enemy <= 102) or enemy == 104 or enemy == 106 or
        #                enemy == 113 or (115 <= enemy <= 120) or enemy == 19 or
        #                enemy == 21 or enemy == 31 or
        #              enemy == 33 or enemy == 35 or enemy == 45 or
        #              enemy == 46 or enemy == 47 or enemy == 49 or
        #              enemy == 50 or (64 <= enemy <= 67) or (72 <= enemy <= 78) or
        #              enemy == 84 or enemy == 98 or enemy == 99 or
        #              (110 <= enemy <= 112) or (121 <= enemy <= 125) or enemy == 133):
        #            if enemy == 85:
        #                enemy_stats_rand.append([92, enemy_stats[92].hp, enemy_stats[92].power, enemy_stats[92].defense,
        #                                         enemy_stats[92].speed, enemy_stats[92].exp, enemy_stats[92].coins, 0, enemy_stats[92].item_chance, enemy_stats[92].item_type,
        #                                         enemy_stats[92].rare_item_chance, enemy_stats[92].rare_item_type, enemy_stats[92].level])
        #                enemy_stats_rand.append([93, enemy_stats[93].hp, enemy_stats[93].power, enemy_stats[93].defense,
        #                                         enemy_stats[93].speed, enemy_stats[93].exp, enemy_stats[93].coins, 0, enemy_stats[93].item_chance, enemy_stats[93].item_type,
        #                                         enemy_stats[93].rare_item_chance, enemy_stats[93].rare_item_type, enemy_stats[93].level])
        #            enemy_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
        #                                     enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, 0,
        #                                     enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
        #        #Appends data to boss array if it's a boss
        #        elif (enemy == 17 or enemy == 30 or enemy == 42 or
        #              enemy == 62 or enemy == 95 or enemy == 96 or
        #              enemy == 107 or enemy == 108):
        #            boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
        #                                     enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, 0,
        #                                     enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
        #        #Appends data to dream boss array if it's a dream boss
       #         elif (enemy == 23 or enemy == 36 or enemy == 52 or
       #               (79 <= enemy <= 81) or (126 <= enemy <= 131) or enemy == 137):
       #             dream_boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
       #                                      enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, 0,
       #                                      enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
       #         #Appends data to filler array if it's a "filler" enemy (one used in bosses that only exists for spectacle)
       #         else:
       #             filler_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
       #                                      enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, 0,
       #                                      enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])

        #Logic for real world enemies
        enemy_logic = [[[0xd]], [[0x13]], [[0x54]], [[0x12], [0x13, 6], [0x15, 6]], [[0x5d], [0x5c], [0x57], [0x55], [0x56], [0x1f], [0x21], [0x23]], [[0x1b], [0x19], [0x1d]],
                       [[0x26], [0x27], [0x2d], [0x44, 5], [0x45, 5], [0x46, 5], [0x47, 5], [0x48, 0, 5], [0x49, 0, 5], [0x4d, 0, 5], [0x4e, 0, 5]], [[0x29], [0x2f, 6], [0x2e, 6]], [[0x5e, 5], [0x29], [0x2f, 6], [0x2e, 6]],
                       [[0x30], [0x31, 0], [0x32, 1, 6, -1, 5, 6]], [[0x5b], [0x62], [0x63]], [], [[0x3a], [0x3b], [0x3c], [0x3d], [0x40]], [[0x41, 6], [0x42, 6], [0x57], [0x55], [0x56], [0x5a, 5]], [], [[0x43]],
                       [[0x44], [0x45], [0x47], [0x46], [0x5b], [0x57], [0x55], [0x56], [0x48, 6], [0x49, 6], [0x4d, 6], [0x4e, 6], [0x4a, 6], [0x4b, 6], [0x4c, 6]], [],
                       [[0x65], [0x66, 3], [0x67, 3], [0x68, 3], [0x69, 3], [0x6e], [0x6f]], [[0x64], [0x6a], [0x70]], [], [[0x71], [0x74], [0x79, 6], [0x7c, 6], [0x7d, 6]], [[0x75], [0x76], [0x77], [0x78], [0x7b, 6], [0x7a]], [], []]

        #Logic for bosses
        boss_logic = [[], [[0x11], [0x17]], [], [], [[0x1e], [0x24, 6]], [], [], [], [[0x2a, 18, 19, 20, 21]], [[0x34, 1, 2, 6, 8, 9, -1, 2, 5, 6, 8, 9]], [[0x5f]], [], [], [], [[0x3e]],
                      [], [[0x4f, 25, 26, 10]], [], [], [[0x6b]], [], [[0x7e, 0, 3, 6]], [[0x7f, 0, 6], [0x80, 0, 6]], [], [[0x89], [0x91]]]

        pbar.update(6)

        #Loads in FMap as a 3D array
        parsed_fmapdat = []
        with (
            code_bin_path.open('r+b') as code_bin,
            fs_std_romfs_path(FMAPDAT_PATH, data_dir=input_folder).open('rb') as fmapdat,
        ):
            version_pair = determine_version_from_code_bin(code_bin)
            code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 8)
            fmapdat_number_of_chunks = struct.unpack('<I', code_bin.read(4))[0] // 8 - 2
            code_bin.seek(4, os.SEEK_CUR)
            for fmapdat_chunk_index in range(fmapdat_number_of_chunks):
                fmapdat_chunk_offset, fmapdat_chunk_len = struct.unpack('<II', code_bin.read(4 * 2))
                fmapdat.seek(fmapdat_chunk_offset)
                if fmapdat_chunk_index < NUMBER_OF_ROOMS:
                    current_sections = []
                    for section_offset, section_length in struct.iter_unpack('<II', fmapdat.read(13 * 4 * 2)):
                        fmapdat.seek(fmapdat_chunk_offset + section_offset)
                        current_sections.append(bytearray(fmapdat.read(section_length)))
                    parsed_fmapdat.append(current_sections)
                else:
                    parsed_fmapdat.append(fmapdat.read(fmapdat_chunk_len))

            # Fixes the experience cap to go way higher
            if version_pair[0] == 'E':
                if version_pair[1] == '1.1':
                    code_bin.seek(0x3FF0D0)
                    code_bin.write(bytes.fromhex("50 C3"))
                    code_bin.seek(0x44FD30)
                    code_bin.write(bytes.fromhex("50 C3"))
                else:
                    code_bin.seek(0x3FF1BC)
                    code_bin.write(bytes.fromhex("50 C3"))
                    code_bin.seek(0x45034C)
                    code_bin.write(bytes.fromhex("50 C3"))

        #print(len(parsed_fmapdat[0x40][6]))

        #Fixes the loading zones in Dozing Sands
        parsed_fmapdat[0xaf][6][28*4+2:28*4+4] = 0x102.to_bytes(2, 'little')
        parsed_fmapdat[0xaf][6][28*5+2:28*5+4] = 0x102.to_bytes(2, 'little')

        #Fixes the softlock/crash that occurs if you go back to the starting area
        parsed_fmapdat[0x1de][6][28:28*2] = parsed_fmapdat[0x64][6]

        #Initializes the item pool
        item_pool = []

        #Initializes the ids that can be used for the new blocks
        unused_blocks = [0, 1, 2, 3, 4, 5, 6, 44, 48, 49, 50, 51, 93, 105, 106, 134, 135, 136, 137, 138, 139, 140, 179, 180, 181, 182, 183, 156, 453, 454, 455, 456, 457, 458, 459, 460, 483,
                         484, 485, 514, 515, 516, 517, 518, 519, 520, 521, 522, 524, 525, 526, 527, 528, 234, 239, 240, 241, 242, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314,
                         2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 243, 244, 2412, 2413, 2414, 2415, 2416, 2417, 2418,
                         2419, 2420, 2421, 2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2442, 2443, 2444,
                         2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470,
                         2471, 2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481, 2482, 2483]

        # Creates an item_locals array with all the blocks and bean spots
        item_locals = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        # Updates the collision for Nerfed Ball Hop
        if settings[1][1] == 1:
            spot = [[0x1BD4, 0x1BDC, 0x1BE4, 0x1BEC, 0x1C0C, 0x1C14, 0x1C1C, 0x1C24, 0x1F8C,
                    0x1F94, 0x1F9C, 0x1FA4,], [0x69C, 0x6A4, 0x6AC, 0x70C, 0x714, 0x71C,
                    0x744, 0x74C, 0x754, 0x77C, 0x784, 0x78C, 0x794, 0x7B4, 0x7BC,
                    0x7C4, 0x7CC, 0x7EC, 0x7F4, 0x7FC, 0x804, 0x824, 0x82C, 0x834,
                    0x83C, 0x85C, 0x864, 0x86C, 0x874, 0x894, 0x89C, 0x8A4, 0x8AC,
                    0x8CC, 0x8D4, 0x8DC, 0x8E4, 0xA8C, 0xA94, 0xA9C, 0xBDC, 0xBE4,
                    0xBEC, 0xBF4, 0xE44, 0xE4C, 0xE54, 0xE5C, 0xE7C, 0xE84, 0xE8C,
                    0xE94, 0xEEC, 0xEF4, 0xEFC, 0x1004, 0x100C, 0x1014, 0x101C, 0x103C,
                    0x1044, 0x104C, 0x1054, 0x1074, 0x107C, 0x1084, 0x108C, 0x10AC, 0x10B4,
                    0x10BC, 0x10C4, 0x10E4, 0x10EC, 0x10F4, 0x10FC, 0x111C, 0x1124, 0x112C,
                    0x1134, 0x126C, 0x1274, 0x127C, 0x1284, 0x1694, 0x169C, 0x16A4, 0x16AC]]
            for i in range(len(spot[0])):
                parsed_fmapdat[0x5D][3][spot[0][i]] = 0x78
            for i in range(len(spot[1])):
                parsed_fmapdat[0x67][3][spot[1][i]] = 0x78
        block_id = 0
        rooms_to_init = [0x001, 0x004, 0x005, 0x010, 0x011, 0x012, 0x013, 0x014, 0x017, 0x019, 0x01F, 0x020, 0x021, 0x022, 0x027, 0x028, 0x02A,
                         0x034, 0x035, 0x036, 0x038, 0x039, 0x03A, 0x03B, 0x03D, 0x040, 0x04B, 0x04C, 0x04D, 0x04F, 0x062, 0x069, 0x06A, 0x06C,
                         0x06D, 0x06F, 0x070, 0x072, 0x075, 0x076, 0x079, 0x07C, 0x0BB, 0x0BD, 0x0BE, 0x0C4, 0x0C5, 0x0C6, 0x0D2, 0x0D6, 0x0E4,
                         0x0F5, 0x0F6, 0x0FA, 0x10C, 0x124, 0x125, 0x126, 0x127, 0x128, 0x129, 0x12A, 0x13D, 0x144, 0x145, 0x146, 0x147, 0x148,
                         0x14B, 0x14C, 0x14E, 0x14F, 0x161, 0x164, 0x165, 0x167, 0x168, 0x16C, 0x177, 0x17A, 0x17D, 0x187, 0x188, 0x189, 0x18A,
                         0x18B, 0x18F, 0x190, 0x192, 0x194, 0x1E7, 0x1F0, 0x1F1, 0x1F2, 0x1F4, 0x1F6, 0x1F7, 0x1F8, 0x1F9, 0x1FA, 0x204, 0x22A,
                         0x22B, 0x22C, 0x22D, 0x22E, 0x22F, 0x231, 0x232, 0x233, 0x295,]
        actor_blacklist = []
        for room in range(NUMBER_OF_ROOMS):
            try:
                check_room = rooms_to_init.index(room)
                fevent_manager = FEventScriptManager(input_folder)
                script = fevent_manager.parsed_script(room, 0)
                temp = []
                if (room == 0x001 or room == 0x012 or room == 0x06C or room == 0x075 or room == 0x0C6 or room == 0x0F5 or room == 0x0F6 or
                    room == 0x0FA or room == 0x10C or room == 0x13D or room == 0x177 or room == 0x17A or room == 0x17D or room == 0x1E7 or room == 0x1F8):
                    trigger = 0
                    if room == 0x001:
                        trigger = 4
                    elif room == 0x012:
                        trigger = 1
                    elif room == 0x0C6:
                        trigger = 2
                    elif room == 0x1E7:
                        trigger = 9
                    #Adds blocks in place of attack piece blocks and ability cutscenes
                    new_block = [0x10, 0x0, int(((script.header.triggers[trigger][0] % 0x10000) + (script.header.triggers[trigger][1] % 0x10000))/2) - 0x20,
                                 script.header.triggers[trigger][4] % 0x10000 + 0x55,
                                 int(((script.header.triggers[trigger][0] // 0x10000) + (script.header.triggers[trigger][1] // 0x10000)) / 2), unused_blocks[block_id]]
                    if room == 0x0F5:
                        new_block[3] += 0x40
                    if room == 0x0F6 or room == 0x0C6 or room == 0x1E7:
                        new_block[3] += 0x20
                    elif room == 0x10C:
                        new_block[3] += 0x75
                    elif room == 0x06C:
                        new_block[2] += 0x55
                    elif room == 0x17D or room == 0x177 or room == 0x17A:
                        new_block[2] += 0x120
                        new_block[3] += 0x20
                    if new_block[4] > 30000:
                        new_block[4] = 0
                    #print(new_block)
                    block_id += 1
                    temp.append(new_block)
                #Exceptions for camera blocks
                if room == 0x040:
                    actor_blacklist = [6]
                elif room == 0x04D:
                    actor_blacklist = [18]
                elif room == 0x072:
                    actor_blacklist = [26]
                elif room == 0x144:
                    #First is a camera block, second is a Kamek block
                    actor_blacklist = [18, 20]
                elif room == 0x188:
                    actor_blacklist = [7]
                #Exceptions for save blocks
                elif room == 0x03A:
                    actor_blacklist = [28]
                elif room == 0x18b:
                    actor_blacklist = [23]
                #Exceptions for Dozing Sands track calling blocks
                elif room == 0x010:
                    actor_blacklist = [11]
                elif room == 0x013:
                    actor_blacklist = [19]
                elif room == 0x014:
                    actor_blacklist = [11]
                elif room == 0x019:
                    actor_blacklist = [19]
                #Exceptions for Kamek blocks
                elif room == 0x145:
                    actor_blacklist = [3]
                elif room == 0x146:
                    actor_blacklist = [3]
                elif room == 0x147:
                    actor_blacklist = [3]
                #No exceptions, no list
                else:
                    actor_blacklist = []
                for a in range(len(script.header.actors)):
                    if (script.header.actors[a][5] // 0x1000) % 0x1000 == 0x748 and script.header.actors[a][5] % 0x100 == 0x43:
                        try:
                            actor_blacklist.index(a)
                        except ValueError:
                            new_block = [0x10, 0x0, script.header.actors[a][0] % 0x10000, script.header.actors[a][0] // 0x10000,
                                         script.header.actors[a][1] % 0x10000, unused_blocks[block_id]]
                            block_id += 1
                            temp.append(new_block)
                for b in range(len(temp)):
                    for d in range(len(temp[b])):
                        parsed_fmapdat[room][7][b*12+d*2:b*12+d*2] = bytearray(struct.pack('<H', temp[b][d]))
            except ValueError:
                pass
            #print(parsed_fmapdat[room][0])
            for treasure_index in range(math.floor(len(parsed_fmapdat[room][7])/12)):
                treasure_type, item_id, x, y, z, treasure_id = struct.unpack('<HHHHHH', parsed_fmapdat[room][7][treasure_index*12:treasure_index*12+12])
                if (room != 0x00D and room != 0x015 and room != 0x016 and room != 0x01D and room != 0x037 and room != 0x04E and room != 0x052 and
                        room != 0x054 and room != 0x1D2 and room != 0x2A8 and room != 0x2A9 and treasure_type % 0x100 != 0x16 and
                        treasure_type % 0x100 != 0x17):
                    if get_zone_id(room, treasure_id) > -1:
                        pbar.update(1)
                        if treasure_type % 2 == 1:
                            treasure_type -= 1
                        item_locals[get_zone_id(room, treasure_id)].append([room, treasure_index * 12, (treasure_type + ((item_id % 2) * 0x10000)), x, y, z, treasure_id])
                        item_pool.append([treasure_type, (item_id // 2) * 2])

        #print(unused_blocks[block_id])
        #for item in item_locals:
        #   print(str(item) + "\n")
        #for item in range(len(item_pool)):
        #    if item_pool[item][1] % 2 == 1:
        #        print(item_locals[item][-1])

        item_logic = [[[0xf], [0x10, 2], [0x7], [0x8], [0x9], [0xa], [0xb], [0xc], [0xd], [0xe], [0x11], [0x12, 2], [0x13], [0x14, 2], [0x15, 2], [0x16, 2], [0x17, 2]],

                      [[0x18], [0x19], [0x1a], [0x1b, 5], [0x1c], [0x1d], [0x1e], [0x1f, 15], [0x20, 15], [0x21], [0x22, 15], [0x23], [0x9d], [0x9e], [0x9f], [0xa1], [0xa2], [0xa3], [0xa4], [0xa5],
                       [0x24, 15, 5], [0x25, 15, 5], [0x26, 15, 5], [0x27, 15, 5], [0x28, 15, 5], [0x950], [0x951], [0x952], [0x953]], [[0x910], [0x911], [0x35d], [0x35e], [0x912]],
                      [[0xa6, 6], [0xa8, 6], [0xa9, 6], [0xab, 6], [0xad, 6], [0xaf, 6], [0xb1, 6], [0x66b, 6], [0xb8, 6], [0xb9, 6], [0xba, 6], [0xbb, 6], [0xbc, 6],
                       [0xbd, 6], [0xbf, 6], [0xc1, 6], [0xc3, 6], [0xc5, 6], [0xc7, 6], [0xc9, 6], [0xcb, 6], [0xcd, 6], [0xcf, 6], [0xd1, 6], [0xd3, 6], [0xd5, 6], [0xd7, 6], [0xd9, 6],
                       [0xdb, 6], [0xdd, 6], [0xdf, 6], [0xe1, 6], [0xe3, 6], [0xe5, 6], [0xe7, 6], [0xe9, 6], [0xeb, 6], [0xec, 6], [0xed, 6], [0xee, 6], [0xf5, 6], [0xf6, 6],
                       [0x29], [0x2a], [0x2b], [0x94f], [0x2d], [0x2e], [0x2f]],

                      [[0x34, 5], [0x35, 5], [0x0], [0x36, 0, -1, 3, -1, 5], [0x37, 0], [0x38, 0], [0x39, 0], [0x3a], [0x3b, 2], [0x3c, 2], [0x3d, 2], [0x954, 2], [0x43, 2, 3, -1, 2, 5],
                       [0x48], [0x49], [0x4a, 16, 1], [0x4b, 16, 2], [0x4c, 2], [0x4d, 2], [0x4e, 0], [0x4f], [0x50], [0x51], [0x52, 2], [0x53, 2], [0x54, 2], [0x55, 2, 3, -1, 2, 5], [0x56, 4], [0x57], [0x58], [0x59, 4], [0x5a, 2],
                       [0x67], [0x68], [0x6b], [0x956, 0], [0x957, 0], [0x6c, 2], [0x6d, 2], [0x6e, 2], [0x6f, 2], [0x8c, 6], [0xb3, 6], [0x77, 6], [0x79, 6], [0x7b, 6], [0x7d, 6], [0xb4, 6], [0x7f, 6], [0x81, 6], [0xb5, 6], [0x83, 6], [0x84, 6],
                       [0x958, 6], [0x8d, 6], [0x8e, 6], [0xb6, 6], [0xb7, 6], [0x9c, 6], [0x959, 6], [0x90, 6], [0x91, 6], [0x1c5, 6], [0x92, 6], [0x93, 6], [0x98], [0x95a, 6], [0x95b, 6], [0x97, 6], [0x5e7, 3],
                       [0x5e8, 2, 3, -1, 2, 5], [0x5e9, 2, 3, -1, 2, 5], [0x94, 6], [0x5e2, 1], [0x5e3, 3, -1, 5], [0x5e4, 3, 5], [0x5e5, 5], [0x5e6, 2], [0x82c, 1], [0x82d, 1, 2], [0x75, 1], [0x76, 1, 2, 5]],
                      [[0x3e], [0x3f], [0x40], [0x41], [0x1], [0x2], [0x3], [0x4], [0x42], [0x5], [0x6], [0x2c], [0x30], [0x44], [0x45], [0x46], [0x47], [0x5b], [0x5c, 1, 5],
                       [0x955, 4, 5], [0x5e, 4, 5], [0x5f, 4, 5], [0x60, 4, 5], [0x61, 4, 5], [0x62, 4, 5], [0x63, 2, 4, 5], [0x64, 2, 4, 5], [0x65, 2, 4, 5], [0x66, 2, 4, 5], [0x70], [0x71], [0x72], [0x73], [0x74]],

                      [[0xfd, 2], [0x33], [0x5d, 2], [0x69, 1], [0x6a, 2], [0x117, 2], [0x119, 2], [0x11a, 1], [0x11b, 17], [0x11c, 2], [0x1cb], [0x60d, 1], [0x60e], [0x60f, 1], [0x610, 2], [0x611, 1], [0x612, 1],
                       [0x607, 1], [0x608, 1], [0x609, 1], [0x95e, 1], [0x204, 1, 4, -1, 5], [0x95f, 3, -1, 5], [0x60b], [0x60c, 2], [0x208, 1, 4, -1, 1, 5], [0x61b, 1, 4, -1, 0, 5], [0x61c, 1, 4, -1, 0, 5], [0x61d, 2, 4], [0x3dc, 2], [0xfe, 2],
                       [0x100], [0x101], [0x102], [0x209], [0x10c, 2], [0x10d], [0x10e], [0x109, 17, 2, 5], [0x10a, 17, 5], [0x10b, 17], [0x19d], [0x19e], [0x96d, 6],
                       [0x53b, 1, 4, -1, 0, 5], [0x53c, 1, 4, -1, 0, 5], [0x53d, 1, 4, -1, 0, 5], [0x984, 1, 4, -1, 0, 5], [0x568, 5, 6], [0x569, 5, 6]],
                      [[0x31, 2], [0x10f, 2], [0x110, 2], [0x111, 2], [0x112, 2], [0x113, 2], [0x32], [0x114, 2], [0x3c9, 2], [0x115], [0x116],
                       [0x86], [0x11d, 2], [0x11e, 2], [0x11f], [0x120], [0x121], [0x122], [0x123], [0x87], [0x124, 2], [0x125], [0x126, 2], [0x127, 2], [0x128, 2], [0x945],
                       [0x88, 1], [0x89, 1], [0x12f, 1], [0x130, 1], [0x131, 1], [0x132, 1], [0x8a], [0x8b, 1], [0x133, 2], [0x134, 5], [0x135, 2], [0x136], [0x137], [0x138, 1], [0x946, 5],
                       [0x103, 2], [0x104, 2], [0x1c4, 6], [0x1cd, 6], [0x1ce, 6], [0x1cf, 6], [0x1d0], [0x1c2], [0x1e6, 6], [0x247, 6], [0x248, 2], [0x249, 2], [0x13b, 2], [0x13c, 2],
                       [0x147, 2], [0x148, 2], [0x149, 2], [0x14a, 2], [0x14b, 2], [0x14c, 2], [0x14d, 2], [0x14e, 2], [0x14f, 2], [0x150, 2], [0x151, 2], [0x129, 2], [0x12a, 2], [0x12b, 2], [0x12c], [0x12d], [0x12e]],
                      [[0x139, 3, 5], [0x13a, 3, 5], [0xff], [0x105, 5], [0x106, 5], [0x107, 2, 5], [0x108, 2, 5], [0x903, 6], [0x904, 6], [0x905, 6], [0x906, 6], [0x907, 6], [0x200, 6], [0x201, 6],
                       [0x20b, 6], [0x211, 6], [0x908, 6], [0x221, 6], [0x222, 6], [0x909, 6], [0x90a, 6], [0x90b, 6], [0x90e, 6, 9], [0x90f, 6, 9], [0x238, 6, 9], [0x239, 6, 9],
                       [0x241, 4, 5, 6], [0x242, 4, 5, 6], [0x243, 4, 5, 6], [0x244, 4, 5, 6], [0x245], [0x246], [0x13d, 2], [0x13e, 5], [0x95c, 4, 5], [0x91a, 2, 4, 5], [0x143, 4, 5], [0x144, 4, 5],
                       [0x145, 4, 5], [0x146, 4, 5], [0x13f, 5], [0x140, 5], [0x3db, 2, 5]],

                      [[0x1c6], [0x5ea], [0x5eb, 2], [0x1c7], [0x1c8], [0x5ed, 2], [0x5ee, 2], [0x5ef], [0x1c9, 1], [0x1ca, 1], [0x5f0, 2], [0x5f1, 2], [0x5f2, 1], [0x5f3], [0x5f4, 1], [0x5f5],
                       [0x1cc, 0], [0x5f7, 0], [0x5f8], [0x5f9], [0x5fa], [0x5fb], [0x5fc], [0x603, 3], [0x202], [0x604], [0x605], [0x606], [0x203], [0x25f, 1, 2, 6, -1, 2, 5, 6], [0x260, 1, 2, 6, -1, 2, 5, 6],
                       [0x261, 1, 2, 6, -1, 2, 5, 6], [0x262, 1, 2, 6, -1, 2, 5, 6], [0x263, 1, 5, 6, -1, 2, 5, 6], [0x264, 1, 5, 6, -1, 2, 5, 6], [0x265, 1, 2, 6, -1, 2, 5, 6],
                       [0x266, 1, 2, 6, -1, 2, 5, 6], [0x267, 1, 2, 6, -1, 2, 5, 6], [0x268, 1, 2, 6, -1, 2, 5, 6], [0x269, 1, 2, 6, -1, 2, 5, 6], [0x26a, 1, 2, 6, -1, 2, 5, 6],
                       [0x26b, 1, 2, 6, -1, 2, 5, 6], [0x26c, 1, 2, 6, -1, 2, 5, 6], [0x26d, 1, 2, 6, -1, 2, 5, 6], [0x26e, 1, 2, 6, -1, 2, 5, 6], [0x26f, 1, 2, 6, -1, 2, 5, 6],
                       [0x270, 1, 2, 6, -1, 2, 5, 6], [0x271, 1, 2, 6, -1, 2, 5, 6], [0x272, 1, 2, 6, -1, 2, 5, 6], [0x273, 1, 2, 6, -1, 2, 5, 6],
                       [0x579, 1, 2, 6, -1, 2, 5, 6], [0x57a, 1, 2, 6, 8, -1, 2, 5, 6, 8], [0x274, 1, 2, 6, 8, 9, -1, 2, 5, 6, 8, 9], [0x275, 1, 2, 6, 8, 9, -1, 2, 5, 6, 8, 9],
                       [0x2f8, 0], [0x2f9, 0], [0x2fc, 2], [0x5f6, 1, -1, 5]],
                      [[0x5ec], [0x5fd], [0x5fe], [0x921], [0x922], [0x923], [0x5ff], [0x600], [0x601], [0x602], [0x276], [0x914], [0x915], [0x916], [0x917], [0x918], [0x919],
                       [0xf3], [0x2b9], [0xf4], [0x96c], [0x2bc], [0x2bd], [0x2d6], [0x2d7], [0x2d8], [0x2fd], [0x2f2], [0x2f3], [0x2f4], [0x2f5], [0x9a3], [0x2f6], [0x2f7]],

                      [[0x625, 1], [0x626], [0x627]], [[0x628], [0x629], [0x20a, 3], [0x62a, 3, -1, 5], [0x62b, 2, 3], [0x62c, 2, 3], [0x20c, 1], [0x62d, 1], [0x62e], [0x62f, 2, 4], [0x962, 2, 4],
                       [0x20d], [0x20e, 3], [0x630], [0x631, 2, 3], [0x632, 3], [0x20f], [0x633, 3, -1, 5], [0x634], [0x635], [0x636], [0x637, 2, 3, -1, 2, 5],
                       [0x638, 3], [0x963, 3, -1, 5], [0x210, 3], [0x639, 2, 3], [0xea, 3], [0x63a, 2, 3], [0x63b, 3], [0x63c, 3], [0x63d, 3],
                       [0xef, 3], [0x63e, 3], [0x63f, 3, 5], [0x91d, 3], [0x60a, 3], [0x8ab, 3], [0x640, 2, 3], [0x641, 2, 3], [0x91e, 2, 3], [0x655, 3, 5], [0x8f8, 2, 3, 5], [0x657, 3, 5],
                       [0x36f, 3, -1, 5], [0x370, 3, -1, 5], [0x98d, 3, 6, 8, -1, 5, 6, 8], [0x390, 3, 6, 8, 10, -1, 5, 6, 8, 10], [0x391, 3, 6, 8, 10, -1, 5, 6, 8, 10],
                       [0x392, 3, 6, 8, 10, -1, 5, 6, 8, 10], [0x393, 3, 6, 8, 10, -1, 5, 6, 8, 10], [0x394, 3, 6, 8, 10, -1, 5, 6, 8, 10],
                       [0x3de, 3, -1, 5], [0x3df, 3, -1, 5], [0x3e0, 3, -1, 5], [0x41a], [0x41b]],
                      [[0xf0], [0x642], [0xf1], [0x643, 6, 10], [0x644], [0x645, 2], [0x647, 2], [0x648], [0xf2], [0x649], [0x64a], [0x937, 2], [0x938, 2], [0x947],
                       [0x64b, 5], [0x64c, 5], [0x64d, 2, 5], [0x64e], [0x902], [0x650], [0x651], [0x652, 2], [0x939, 2], [0x658, 5], [0x964, 5],
                       [0x659, 5], [0x65a, 5], [0x65b, 5], [0x913], [0x65c, 2, 5], [0x65d, 2, 5], [0x3da, 5, 6], [0x3dd, 5, 6]],
                      [[0x646], [0x64f], [0x93a, 2, 5], [0x653, 2, 3], [0x654, 2, 3], [0x6f6, 6, 10], [0x6dc, 6, 10], [0x395], [0x396]],
                      [[0x397], [0x98e], [0x399], [0x39a], [0x39b], [0x39c], [0x39d], [0x39e], [0x98f], [0x990], [0x39f], [0x3a0], [0x3a1], [0x991], [0x3a2], [0x3a3], [0x3a4], [0x3a5],
                       [0x70e], [0x70f], [0x992], [0x3a8], [0x3a9], [0x3aa], [0x3ab], [0x3ac], [0x993], [0x994], [0x3ad], [0x3ae], [0x3af], [0x3b0], [0x995], [0x996], [0x3b9],
                       [0x997], [0x3ba], [0x3c1], [0x3c2], [0x3c5], [0x3c6], [0x3c7], [0x3c8], [0x95d], [0x3ca], [0x3cb], [0x3cc], [0x3d0], [0x3d1], [0x3d8], [0x3d9], [0x77b], [0x998], [0x398]],

                      [[0x1e3, 4, -1, 5], [0x1e4, 4], [0x91b], [0x91c], [0x1e5], [0x61a], [0x61e], [0x61f, 1], [0x620], [0x621], [0x622, 5], [0x623, 2], [0x624, 2],
                       [0x205, 4], [0x613, 4], [0x614, 4], [0x615, 2, 4], [0x960, 4], [0x616, 3], [0x206, 4], [0x207], [0x617], [0x618], [0x619, 2], [0x961, 2],
                       [0x90c, 6], [0x4db, 24, 6], [0x981, 6], [0x983, 4, 6, 10], [0x56a, 4], [0x56b, 4], [0x56c, 4], [0x56d, 4], [0x573, 4], [0x574, 1, 3, 5]],
                      [[0x90d], [0x4e2], [0x4e3], [0x4e4], [0x979], [0x4eb], [0x97a, 25], [0x97b, 25], [0x4f5, 25], [0x4f6, 25], [0x45e, 25, 10], [0x45f, 25, 10],
                       [0x97c, 25, 10], [0x4fb, 25, 10], [0x4fc, 25, 10], [0x4fd, 25, 10], [0x97d, 25, 10], [0x97e, 25, 10], [0x49e, 25, 26, 8, 9, 10], [0x501, 25, 26, 8, 9, 10],
                       [0x97f], [0x980], [0x505], [0x510, 25], [0x511, 25, 26, 10], [0x512, 25], [0x51a, 25]],

                      [[0x82e], [0x82f], [0x830, 2], [0x831], [0x832], [0x833], [0x834], [0x835, 2, 3], [0x984, 4], [0x836, 3], [0x837, 3], [0x838, 3],
                       [0x985, 4], [0x839, 4], [0x83a, 2, 3], [0x83b, 2, 4], [0x986, 4], [0x83c, 4], [0x825, 3], [0x826, 3], [0x827, 3], [0x828, 4, 6], [0x91f, 3], [0x920, 3]],
                      [[0x987], [0x83d], [0x988, 2], [0x83e], [0x83f], [0x840, 2], [0x841], [0x842], [0x843], [0x844], [0x845, 2], [0x989, 2], [0x846, 2], [0x847, 2],
                       [0x98a], [0x848], [0x849], [0x98b, 2], [0x84a, 2], [0x84b, 2], [0x84c, 2], [0x98c, 1, 2], [0x84d, 1, 2], [0x84e, 1, 2], [0x84f, 2], [0x96a, 2], [0x96b, 2],
                       [0x7b0], [0x7b1], [0x7b2], [0x7b3], [0x7b4], [0x7b5], [0x7b6], [0x7d8], [0x7d9], [0x7da], [0x7e0, 2], [0x7e1, 2], [0x7e2, 2], [0x7e3, 2], [0x829, 2], [0x82a, 2], [0x82b, 2]],
                      [[0x821, 8, 9, 10], [0x850], [0x851], [0x852], [0x853], [0x854], [0x855], [0x856], [0x857], [0x858], [0x859], [0x7e4], [0x7e5], [0x7e6], [0x7e7], [0x999],
                       [0x99a], [0x99b, 8, 9], [0x7e8], [0x7e9], [0x7ea], [0x7eb], [0x7ec], [0x7ed, 8, 9], [0x7ee], [0x7ef], [0x99c], [0x99d, 8, 9], [0x7f3, 8, 9], [0x7f4, 8, 10],
                       [0x99e, 8, 9], [0x803, 8, 9], [0x804], [0x805, 8, 9], [0x806, 8, 9, 10], [0x933, 8, 9], [0x99f, 8, 9, 10], [0x9a0, 8, 9, 10], [0x80a, 8, 9, 10], [0x80b, 8, 9, 10],
                       [0x9a1, 8, 9, 10], [0x80c, 8, 9, 10], [0x80d, 8, 9, 10], [0x80e, 8, 9, 10], [0x80f, 8, 9, 10], [0x9a2, 8, 9, 10], [0x812, 8, 9, 10], [0x813, 8, 9, 10]],

                      [[0x65e, 3], [0x65f, 3], [0x96e, 3], [0x660], [0x661], [0x96f], [0x662], [0x970], [0x663, 3],
                       [0x971], [0x972, 1], [0x664, 1], [0x665, 1], [0x666, 1], [0x667, 2], [0x118], [0x142], [0x668, 2], [0x669, 2], [0x66a],
                       [0x973], [0x974], [0x93b], [0x93c], [0x93d], [0x93e], [0x93f], [0x85a, 0, 3, 6], [0x85b, 0, 3, 6], [0x85c, 0, 3, 6],
                       [0x85d, 0, 3, 6], [0x85e, 0, 3, 6], [0x85f, 0, 3, 6], [0x860, 0, 3, 6], [0x861, 0, 3, 6], [0x862, 0, 3, 6], [0x863, 0, 3, 6], [0x89b, 0, 3, 6], [0x89c, 0, 3, 6], [0x89d, 0, 3, 6],
                       [0x89e, 0, 3, 6], [0x89f, 0, 3, 6], [0x8a0, 0, 3, 6], [0x8a1, 0, 3, 6], [0x8a2, 0, 3, 6], [0x8a3, 0, 3, 6]],
                      [[0x975], [0x976], [0x66e], [0x66f], [0x670, 2], [0x671, 2], [0x977], [0x965], [0x966], [0x967], [0x978], [0x673], [0x674], [0x8f9], [0x8fa],
                       [0x677], [0x678], [0x679], [0x67a], [0x67b, 2], [0x67c, 2], [0x67d], [0x67e, 2], [0x949, 0], [0x94a, 0], [0x94b, 2], [0x67f], [0x680], [0x94c], [0x94d],
                       [0x675], [0x676], [0x940], [0x941], [0x948], [0x934, 0, 6], [0x8a4, 0, 6], [0x8a7, 0, 6], [0x8a8, 0, 6], [0x8a9, 0, 6], [0x8aa, 0, 6], [0x935, 0, 6], [0x8ac, 0, 6], [0x8b6, 0, 6]],
                      [[0x681], [0x682], [0x683], [0x932, 2], [0x684, 2], [0x685, 2], [0x686], [0x687], [0x688], [0x968, 2], [0x969, 2],
                       [0x689, 1], [0x68a, 1], [0x68b], [0x68c, 2], [0x68d, 2], [0x68e, 2], [0x68f, 2], [0x8b7], [0x8b8], [0x8bf], [0x8c5], [0x8c6], [0x8c7]],
                      [[0x8e1], [0x8e2], [0x8e3], [0x8e4], [0x8e5], [0x94e], [0x8f5], [0x8f6], [0x8f7]]]

        if settings[1][0] == 1:
            item_logic[4][78] = [0x82c]
            item_logic[4][79] = [0x82d, 2]
            item_logic[4][81] = [0x76, 2, 5]
            item_logic[6][13] = [0x60f]
            item_logic[6][15] = [0x611]
            item_logic[6][16] = [0x612]
            item_logic[6][23] = [0x60b, 0, 4, -1, 5]
            item_logic[6][26] = [0x61b, 0, 4, -1, 0, 5]
            item_logic[6][27] = [0x61c, 0, 4, -1, 0, 5]
            item_logic[6][44] = [0x53b, 0, 4, -1, 0, 5]
            item_logic[6][45] = [0x53c, 0, 4, -1, 0, 5]
            item_logic[6][46] = [0x53d, 0, 4, -1, 0, 5]
            item_logic[6][47] = [0x982, 0, 4, -1, 0, 5]

        #for l in range(len(item_logic)):
        #    for t in range(len(item_logic[l])):
        #        print(str(item_logic[l][t][0] == item_locals[l][t][-1]) + " " + str(item_logic[l][t][0]))
        #        if item_logic[l][t][0] != item_locals[l][t][-1]:
        #            print(item_locals[l][t][-1])
        pbar.update(10)

        #for l in range(len(item_logic)):
        #    try:
        #        if item_logic[l][0][0] == item_locals[l][-1]:
        #            print(item_logic[l])
        #    except TypeError:
        #        if item_logic[l][0] == item_locals[l][-1]:
        #            print(item_logic[l])
        #        print(item_locals[l])
        #print(len(item_logic))
        #print(len(item_locals))

        #To be utilized: loading zone types for entrance randomization
        #Loading zone types:
        # -1 - Inaccessible
        # 0 - Entrance left
        # 1 - Entrance right
        # 2 - Entrance up
        # 3 - Entrance down
        # 4 - Launch platform entrance up
        # 5 - Launch platform entrance down
        # 6 - Pipe
        # 7 - Dozing Track Entrance Left
        # 8 - Dozing Track Entrance Right
        # 9 - Dozing Track Entrance Up
        # 10 - Dozing Track Entrance Down
        # 11 - Going Up
        # 12 - Going Down
        # 13 - Diagonal Entrance
        # 14 - Dream Entrance Dream Portal
        # 15 - Dream Entrance Left
        # 16 - Dream Entrance Right
        # 17 - Dream Entrance Up
        # 18 - Dream Entrance Down
        # 19 - Dream Entrance Pipe
        # 20 - Dream Entrance Door
        # 21 - Dream Entrance Dream Egg Walkway Going Forward
        # 22 - Dream Entrance Dream Egg Walkway Going Backward
        #exit_types = [[1, 3, 2, 0], [1, 2, 3, 2, 2, 0, 0, 0], [1, 2, 0], [0], [3, 2, 4, 0], [3, 5, 0], [1, 3, 2, 0], [1, 6, 3, 3, 2, 3, 0], [1],
        #              [1, 1, 1, 4, 2], [5, 3], [1, 2], [1, 0], [-1], [1, 3, 0], [3], [10, 7], [3, 2], [3, 0], [8, 10, 7, 7], [9, 7], [-1], [-1],
        #              [0, 0], [6], [8, 8, 10], [1, 0], [1, 3, 0], [1, 3, 2, 0], [-1], [14, 18, 17, 15], [16, 15], [16, 15], [16, 15], [16, 16, 15, 15],
        #              [15], [16, 16, 15], [16, 15, 15], [16, 16, 15, 15], [16, 19, 19, 13], [19, 19], [16, 16], [15, 15], [16], [14], [16, 15],
        #              [16, 15], [17, 15], [15], [15], [15], [2, 0], [1, 1, 0, 3, 3, 11, 3, 2, 3], [3, 3, 3, 0, 3, 2, 0, 0], [1, 1, 3, 3, 2, 3, 3],
        #              [-1], [1, 1, 3], [3, 3], [1, 1, 0, 0, 0], [3, 0, 0], [12, 2], [2], [1, 2], [2, 6, 1], [2], [2], [2], [2], [2], [3, 2], [2],
        #              [1, 1, 1, 2], [1, 0, 0, 0], [0], [2, 0], [1, 3, 0], [1, 1], [1, 1, 3, 0, 0], [-1], [2, 0], [-1], [-1], [-1], [-1], [-1], [-1],
        #              [3, 0], [-1], [1, 0], [1, 0], [6, 3, 2], [1, 3], [2, 3, 2], [1, 2, 0], [-1], [-1], [8, 10], [1, 0], [1, 0], [1, 2], [-1], [-1],

        #              [3, 2], [3, 2, 6], [1, 1, 3, 2, 0, 0], [1, 1, 3, 0], [1, 3, 0], [1, 2], [3, 0], [1], [3, 3, 3, 0, 0], [1, 2, 3, 12, 2, 2],
        #              [0], [-1], [3, 2, 11], [-1], [3, 2, 0], [2, 3], [3, 2, 2, 0], [1, 1, 1, 3, 2, 6, 0, 0, 0], [1, 1, 1, 0, 0], [1, 1], [1],
        #              [1, 1, 0, 0, 0], [0, 0], [3, 2], [1, 2], [1, 0], [0], [2],

        #              [1, 13, 3, 2, 13, 0], [-1], [2, 13], [3, 3], [1, 1, 2, 0, 0], [0], [1], [0, 13], [1, 13, 3, 2, 13, 0], [0], [13], [2], [13],
        #              [1, 3], [-1], [1], [-1], [1, 0], [2, 0], [3, 0], [1, 2], [1], [0, 0], [3], [-1], [-1], [15], [-1], [-1], [-1], [-1],
        #              [14, 20, 15], [16, 20, 20, 15], [20, 20], [16, 20, 15], [20], [16, 15], [16, 15], [16], [17, 20], [-1], [16, 14], [16, 15], [15],
        #              [1, 3, 2, 0], [16, 16], [16, 14], [14, 15, 15], [16, 15], [16, 16], [14], [14], [14, 19, 15], [16, 16], [19, 15],
        #              [19, 14, 15], [16, 15], [16, 16, 15, 15, 15, 15], [16, 15, 15], [16, 16, 15], [16, 15], [16, 19], [16, 19], [16, 15],
        #              [16, 16, 19, 19], [16, 15], [16, 15], [15, 15], [16, 15], [-1], [-1], [-1], [-1], [-1], [-1], [-1], [-1], [-1], [-1],

        #              [16, 14, 19], [20, 15], [19, 21], [19, 19], [19, 19, 19], [-1], [14, 15, 15]]

        #To be utilized: array of what's required to access specific entrances
        #room_access = [[[], [], [], []], [[], [], [], [], [], [0, 5], [0], []], [[0, -1, 5], [], [0]], [[0], [0], [0], []], [[0], [0], [0]],
        #               [[], [], [], []], [[3, -1, 5], [], [0], [], [], [0], []], [[]], [[0], [0], [0], [0, 5], [0, 5]], [[0], []], [[], []],
        #               [[0], [0]], [], [[], [], []], [[]], [[], []], [[1, -1, 2], []], [[], []], [[], [], [], []], [[], []], [], [],
        #               [[], []], [[0]], [[], [], []], [[], []], [[], [], []], [[], [], [], []], [], [[], [], [], []], [[], []], [[], []], [[], []],
        #               [[], [], [], []], [[]], [[], [], []], [[], [], []], [[], [], [], []], [[], [], [], []], [[], []], [[], []], [[], []], [[]],
        #               [[]], [[], []], [[], []], [[], []], [[]], [[]], [[]], [[22], []], [[22], [22], [22], [22], [22], [22], [22], [22], [22]],
        #               [[22], [22, 5], [22], [22], [22], [22], [22], [22]], [[22], [22], [22], [22], [22, 1], [22], [22]], [], [[], [], []],
        #               [[22], [22]], [[5], [], [], [], []], [[], [], []], [[22], [22]], [[22]], [[22], [22]], [[22], [22, 41], [22, 41]],
        #               [[22]], [[22]], [[22]], [[22]], [[22]], [[], []], [[]], [[], [1], [], []], [[], [], [], []], [[]], [[], []], [[], [], []],
        #               [[], []], [[], [0], [0, 4], [5], []], [], [[], []], [], [], [], [], [], [], [[], []], [], [[], []], [[], []], [[], [], []],
        #               [[], []], [[], [], []], [[], [], [5]], [], [], [[], []], [[5], []], [[], []], [[], []], [], [],

        #               [[23, 0], [23, 1]], [[23, 0], [23, 0], [23, 0, 5]], [[23, 0, 5], [23, 0], [23, 42, 0], [23, 0], [23, 0, 3, -1, 0, 5], [23, 0]],
        #               [[23, 0], [23, 0], [23, 0], [23, 0]], [[23, 0], [23, 0], [23, 0]], [[23, 0], [23, 0]], [[23, 0, 3], [23, 0, 3]], [[23, 0]],
        #               [[23, 0, 5], [23, 0, 3], [23, 0], [23, 0], [23, 0, 3]], [[23, 0, 3], [23, 0, 3], [23, 0, 3], [23, 0, 3], [23, 0], [23, 0, 3]],
        #               [[23, 0]], [], [[23, 0, 5], [23, 0], [23, 0, 3]], [], [[23, 0, 3], [23, 0, 4], [23, 0]],
        #               [[23, 0], [23, 0, 4]], [[23, 0, 4], [23, 0, 4], [23, 0, 4, 5], [23, 0, 4, 5]],
        #               [[23, 0], [23, 0, 3], [23, 0, 3], [23, 0, 42], [23, 0], [23, 0], [23, 0, 3], [23, 0, 3], [23, 0]],
        #               [[23, 0], [23, 0, 3, -1, 23, 0, 5], [23, 0], [23, 0, 4, -1, 23, 0, 5], [23, 0, 4]], [[23, 0, 3], [23, 0]], [[23, 0, 4]],
        #               [[23, 0, 5], [23, 0], [23, 0], [23, 0, 5], [23, 0]], [[23, 0, 3], [23, 0]], [[23, 0], [23, 0]], [[23, 0, 3], [23, 0]],
        #               [[23, 0, 3], [23, 0, 3]], [[23, 0]], [[23, 0, 5]],

        #               [[], [], [], [], [], []], [], [[], []], [[], []], [[15], [15], [], [15], [15]], [[]], [[]], [[], []], [[], [], [], [], [], []],
        #               [[]], [[]], [[]], [[]], [[], [5]], [], [[14]], [], [[14], [14]], [[14], [14]], [[14], [14]], [[14], [14]], [[], []], [[]], [[], []], [[]],
        #               [], [], [[]], [], [], [], [], [[], [6, 7, 8, 12, 13], []], [[], [], [], []], [[], []], [[], []], [[]], [[], []], [[], []], [[]],
        #               [[6, 7, 8, 12, 13], [6, 7, 8, 12, 13]], [], [[], []], [[], []], [[]], [[], [], [], [5]], [[], []], [[], []], [[], [], []],
        #               [[], []], [[], []], [[]], [[]], [[], [], []], [[], []], [[], []], [[0], [], []], [[], []], [[], [], [], [], [], []], [[], [], []],
        #               [[], [], []], [[], []], [[], []], [[], []], [[], []], [[], [], [], []], [[], []], [[], []], [[], [9]], [[], [9]], [], [], [], [],
        #               [], [], [], [], [], [], [[], [], []], [[], []], [[], []], [[], []], [[], [], []], [], [[], [], []]]

        #To be utilized: dream world rooms attached to their overworld room, with info of what exits can access it. The first entry is always the entrance
        #(if a room has multiple dream worlds, it's stored with the first byte being which dream world, and the last 3 being the room)
        #dream_access = [[0x001, [0x02C], [[0], [1], [2], [3], [5], [6]]], [0x003, [0x030], [0]], [0x004, [0x19A, 0x09D], [3]], [0x008, [0x199, 0x032], [[0, 0, 4, 5]]],
        #                [0x00B, [0x01E, 0x01F, 0x020, 0x021, 0x022, 0x023, 0x024, 0x025, 0x026, 0x027, 0x028, 0x029, 0x02A, 0x02B, 0x02D, 0x02E, 0x02F], [[0], [1, 40]]],
        #                [0x012, [0x0B1, 0x13C, 0x13D, 0x13E], [[0], [1]]], [0x013, [0x0EE], [[0], [1], [2], [3]]], [0x0019, [0x0B5], [[1], [2]]], [0x1019, [0x0EC], [[1], [2]]],
        #                [0x035, [0x12E, 0x12F], [[0, 2], [1, 2, 5], [4, 2], [5, 2], [7, 2]]], [0x036, [0x130], [[0], [1, 5], [2, 5], [3, 5], [4], [5, 5], [6, 5]]],
        #                [0x038, [0x17E], [[0, 5], [2, 5]]], [0x039, [0x12D], [[0, 0], [1, 0]]],
        #                [0x003A, [0x0D2, 0x0D3, 0x0D4, 0x0D5, 0x0D6, 0x161, 0x162, 0x163, 0x164, 0x165, 0x166, 0x167, 0x168, 0x169, 0x16A, 0x16B, 0x16C, 0x16D, 0x16E,
        #                          0x16F, 0x170, 0x171, 0x172, 0x1C9, 0x1CA], [[0, 5], [1], [2, 0, 3], [3], [4, 0]]], [0x103A, [0x17F, 0x180, 0x181], [[4]]],
        #                [0x03B, [0x173, 0x174, 0x175, 0x176, 0x177], [[0], [1], [2]]], [0x048, [0x182], [[0, 3, 5]]],
        #                [0x04C, [0x17B, 0x17C, 0x17D], [[0, 0, 4], [1]]], [0x04F, [0x178, 0x179, 0x17A], [[0, 0, 4], [1]]],
        #                [0x05D, [0x0EB], [[0, 5], [1, 5], [2]]], [0x060, [0x0ED], [[0], [1]]], [0x061, [0x292, 0x0EF], [[0, 5], [1]]],

        #                [0x067, [0x208], [[0, 5], [1, 5], [2, 5]]], [0x0068, [0x13F, 0x1E7], [[0], [1, 5], [2, 5], [3, 5], [4, 5], [5, 5]]],
        #                [0x1068, [0x1E8], [[0, 5], [1, 3, -1, 5], [2, 3, -1, 5], [3, 3, -1, 5], [4], [5, 3, -1, 5]]],
        #                [0x006A, [0x208], [[0], [1], [2]]], [0x106A, [0x20E], [0], [1], [2]], [0x06D, [0x208], [[0, 3, -1, 5]]],
        #                [0x06E, [0x209, 0x20A], [[0, 5], [1, 3, 5], [4, 3, 5]]], [0x070, [0x208], [[0]]], [0x072, [0x20C, 0x20D], [[0, 3, 5], [1, 3], [2, 3]]],
        #                [0x076, [0x250, 0x290], [[0, 4], [1, 4], [2, 4, 5], [3, 4, 5]]], [0x0077, [0x1E9, 0x1EA, 0x1EB], [[0], [3], [5]]],
        #                [0x1077, [0x1EC, 0x1ED], [[0], [3], [5]]], [0x07F, [0x1EE, 0x1EF, 0x1F0, 0x1F1, 0x1F2, 0x1F3, 0x1F4, 0x1F5, 0x1F6, 0x1F7, 0x1F8, 0x1F9, 0x1FA,
        #                                                                    0x1FB, 0x1FC, 0x1FD, 0x1FE, 0x1FF, 0x200, 0x201, 0x202, 0x204], [[0, 3, -1, 5], [1, 3, -1, 5]]],

        #                [0x097, [0x0A2, 0x0A3, 0x0A4, 0x0A5, 0x0A6, 0x0A7, 0x0A8, 0x0A9, 0x0AA, 0x0F4, 0x0F5, 0x0F6, 0x0F7, 0x0F8, 0x0F9, 0x0FA], [[0], [1]]]]

        #To be utilized: a blacklist of what triggers can't be accessed if another is activated
        # -1: "Don't go from this trigger if you're in this room, and it hasn't been activated"
        # -2: "Only disable if glitches aren't enabled"
        # -3: "Finish connecting until nothing can connect, then add the specified key item or make the condition possible*"
        # Conditions:
        #  40: Rocks have been cleared in Mushrise Park
        #  41: All Ultibed parts have been collected
        #  42: Required Pi'illo Folk have been saved
        #*If the condition requires key items that aren't in the pool, change the entrance
        exit_blacklist = [[0x001, -1, [[4, 7], [4, 7], [4, 7], [4, 7], [0, 1, 2, 3, 5, 6], [4, 7], [4, 7], [0, 1, 2, 3, 5, 6]]],
                          [0x004, -1, [[2, 3], [2, 3], [3], [0, 1, 2]]], [0x006, -3, [[2], [2], [0, 1, 3], [2]], 16],
                          [0x007, -1, [[2], [2], [], [2], [2], [2], [2]]], [0x009, -1, [[3], [3], [3], [], [3]]],
                          [0x00B, -3, [[1], [0]], 40], [0x011, -1, [[], [0]]], [0x012, -3, [[1], [0]], 17],
                          [0x034, -1, [[1, 3, 4, 6, 7, 8], [0, 2, 5], [1, 3, 4, 6, 7, 8], [0, 2, 5], [0, 2, 5], [1, 3, 4, 6, 7, 8], [0, 2, 5], [0, 2, 5], [0, 2, 5]]],
                          [0x035, -1, [[2, 3, 6], [2, 3, 6], [0, 1, 4, 5, 6, 7], [0, 1, 4, 5, 6, 7], [2, 3, 6], [2, 3, 6], [0, 1, 2, 3, 4, 5, 7], [2, 3, 6]]],
                          [0x036, -1, [[1, 2, 3, 4, 5, 6], [0, 4], [0, 4], [0, 4], [1, 2, 3, 5, 6], [0, 4], [0, 4]]], [0x038, -1, [[1], [0, 2], [1]]],
                          [0x03A, -1, [[2, 4], [2, 4], [0, 1, 3, 4], [2, 4], [0, 1, 2, 3]]], [0x03C, -1, [[1], [0]]], [0x03F, -1, [[1, 2], [0, 2], [0, 1]]],
                          [0x047, -1, [[1, 2, 3], [0, 2, 3], [0, 1], [0, 1]]], [0x048, -1, [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]],
                          [0x04B, -1, [[1, 2], [0], [0]]], [0x04C, -1, [[1], [0]]], [0x04D, -1, [[1, 2, 3], [0, 2, 3, 4], [0, 1, 3, 4], [1, 2], [1, 2]]],
                          [0x05A, -3, [[1], [0, 2], [1]], 15],

                          [0x06E, -1, [[2, 3], [2, 3], [0, 1, 4], [0, 1, 4], [2, 3]]], [0x06F, -1, [[3, 5], [3, 5], [3, 5], [], [3, 5], []]],
                          [0x077, -1, [[1, 2, 3, 6, 7, 8], [0, 2, 3, 4, 5, 7, 8], [0, 1, 3, 4, 5, 6, 8], [0, 1, 2, 4, 5, 6, 7], [1, 2, 3, 6, 7, 8],
                                       [1, 2, 3, 6, 7, 8], [0, 2, 3, 4, 5, 7, 8], [0, 1, 3, 4, 5, 6, 8], [0, 1, 2, 4, 5, 6, 7]]],
                          [0x078, -1, [[1, 2, 3, 4], [0], [0], [0], [0]]], [0x079, -1, [[], [0]]], [0x07B, -1, [2], [2], [0, 1, 3, 4], [2], [2]], [0x07C, -1, [[], [0]]],

                          [0x0A3, -1, [[2, 3], [2, 3], [0, 1], [0, 1]]], [0x0AF, -3, [[1], [0, 2, 3], [1], [1]], 18], [0x0B7, -1, [[1], [0, 2], [1]]],
                          [0x0BC, -1, [[1, 3, 4, 5], [0, 2], [1, 3, 4, 5], [0, 2], [0, 2], [0, 2]]], [0x0BE, -1, [[1], [0, 2], [1]]]]

        #How I'm going to do entrance randomization:
        #1) Sort the entrances into 2 arrays: One for entrances that are accessible, and ones that aren't
        #   - The arrays are 2D arrays, with the first axis being sorted by what type of exit it is
        #   - The second array in the accessible array contains the entrance ID (Explained how it's stored below),
        #   and the second an array containing both the entrance ID and the logic
        #   - The entrance IDs are stored as a 4-digit hex number, with the first digit being the entrance ID and the last 3 being the room ID
        #
        #2) Connect every possible entrance until either a stop command is triggered or 20-30 entrances have been done
        #   - Connections can only be made as follows: 0-1, 2-3/5, 3-2/4, 4-3/5, 5-2/4, 6-6, 7-8, 9-10, 11-12, 13-13
        #   - If there are no entrances left, it replaces a random room it's connected with with the least entrances an exit it can connect to with a new one that has multiple exits
        #
        #3) Connect remaining entrances in their rooms to eachother until none remain if it's a "stop" command, or only 1 if it timed out
        #   - If it can't reach either number, it calls in a new room based on the connections that are needed
        #
        #4) Either temporarily add the key item to the item pool if it's a "stop" command, or add a random key item if it timed out
        #
        #5) Add any room that's now available into the room pool
        #
        #6) Update the logic for every subsequent room to require the key items currently in the pool
        #
        #7) Repeat steps 2-6 until every entrance has been selected

        #for item in range(len(item_logic)):
        #    if item_locals[item][6] == item_logic[item][0][0]:
        #        print(item_locals[item][6])

        #Creates an item pool for the key items
        key_item_pool = [[0xE002 - settings[3][0], 0], [0xE002 - settings[3][0], 1], [0xE002 - settings[3][0], 2], [0xE004, 3], [0xE004, 4],
                         [0xE005, 5], [0xE00A, 6], [0xE00D, 7], [0xE00F, 8], [0xE00E, 9], [0xE010, 10], [0xE011, 11], [0xE012, 12], [0xE013, 13], [0xE075, 14], [0xC369, 15],
                         [0xCABF, 16], [0xE0A0, 17], [0xC343, 18], [0xC344, 19], [0xC345, 20], [0xC346, 21], [0xC960, 22], [0xC3B9, 23],
                         [0xB0F7, 24], [0xB0F7, 25], [0xB0F7, 26], [0xC47E, 27]]
        #print(key_item_pool[0][0])

        #Checked array for the key items
        key_item_check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        #Creates an item pool with the attack pieces
        attack_piece_pool = [[[0x01, 0xB030], [0x02, 0xB030], [0x04, 0xB030], [0x08, 0xB030], [0x10, 0xB030],
                              [0x01, 0xB031], [0x02, 0xB031], [0x04, 0xB031], [0x08, 0xB031], [0x10, 0xB031]],
                             [[0x01, 0xB059], [0x02, 0xB059], [0x04, 0xB059], [0x08, 0xB059], [0x10, 0xB059],
                              [0x01, 0xB05A], [0x02, 0xB05A], [0x04, 0xB05A], [0x08, 0xB05A], [0x10, 0xB05A]],
                             [[0x01, 0xB037], [0x02, 0xB037], [0x04, 0xB037], [0x08, 0xB037], [0x10, 0xB037],
                              [0x01, 0xB038], [0x02, 0xB038], [0x04, 0xB038], [0x08, 0xB038], [0x10, 0xB038]],
                             [[0x01, 0xB03B], [0x02, 0xB03B], [0x04, 0xB03B], [0x08, 0xB03B], [0x10, 0xB03B],
                              [0x01, 0xB03C], [0x02, 0xB03C], [0x04, 0xB03C], [0x08, 0xB03C], [0x10, 0xB03C]],
                             [[0x01, 0xB032], [0x02, 0xB032], [0x04, 0xB032], [0x08, 0xB032], [0x10, 0xB032],
                              [0x01, 0xB033], [0x02, 0xB033], [0x04, 0xB033], [0x08, 0xB033], [0x10, 0xB033]],
                             [[0x01, 0xB041], [0x02, 0xB041], [0x04, 0xB041], [0x08, 0xB041], [0x10, 0xB041],
                              [0x01, 0xB042], [0x02, 0xB042], [0x04, 0xB042], [0x08, 0xB042], [0x10, 0xB042]],
                             [[0x01, 0xB03D], [0x02, 0xB03D], [0x04, 0xB03D], [0x08, 0xB03D], [0x10, 0xB03D],
                              [0x01, 0xB03E], [0x02, 0xB03E], [0x04, 0xB03E], [0x08, 0xB03E], [0x10, 0xB03E]],
                             [[0x01, 0xB045], [0x02, 0xB045], [0x04, 0xB045], [0x08, 0xB045], [0x10, 0xB045],
                              [0x01, 0xB046], [0x02, 0xB046], [0x04, 0xB046], [0x08, 0xB046], [0x10, 0xB046]],
                             [[0x01, 0xB039], [0x02, 0xB039], [0x04, 0xB039], [0x08, 0xB039], [0x10, 0xB039],
                              [0x01, 0xB03A], [0x02, 0xB03A], [0x04, 0xB03A], [0x08, 0xB03A], [0x10, 0xB03A]],
                             [[0x01, 0xB047], [0x02, 0xB047], [0x04, 0xB047], [0x08, 0xB047], [0x10, 0xB047],
                              [0x01, 0xB048], [0x02, 0xB048], [0x04, 0xB048], [0x08, 0xB048], [0x10, 0xB048]],
                             [[0x01, 0xB05B], [0x02, 0xB05B], [0x04, 0xB05B], [0x08, 0xB05B], [0x10, 0xB05B],
                              [0x01, 0xB05C], [0x02, 0xB05C], [0x04, 0xB05C], [0x08, 0xB05C], [0x10, 0xB05C]],
                             [[0x01, 0xB043], [0x02, 0xB043], [0x04, 0xB043], [0x08, 0xB043], [0x10, 0xB043],
                              [0x01, 0xB044], [0x02, 0xB044], [0x04, 0xB044], [0x08, 0xB044], [0x10, 0xB044]],
                             [[0x01, 0xB049], [0x02, 0xB049], [0x04, 0xB049], [0x08, 0xB049], [0x10, 0xB049],
                              [0x01, 0xB04A], [0x02, 0xB04A], [0x04, 0xB04A], [0x08, 0xB04A], [0x10, 0xB04A]],
                             [[0x01, 0xB03F], [0x02, 0xB03F], [0x04, 0xB03F], [0x08, 0xB03F], [0x10, 0xB03F],
                              [0x01, 0xB040], [0x02, 0xB040], [0x04, 0xB040], [0x08, 0xB040], [0x10, 0xB040]],
                             [[0x01, 0xB04B], [0x02, 0xB04B], [0x04, 0xB04B], [0x08, 0xB04B], [0x10, 0xB04B],
                              [0x01, 0xB04C], [0x02, 0xB04C], [0x04, 0xB04C], [0x08, 0xB04C], [0x10, 0xB04C]],]

        #Logic for the key items, so they only spawn when others are already in the pool
        logic_logic = [[0, 15], [1, 0 + (settings[3][0]*2)], [2, 1 - settings[3][0]], [3, 15, -1, 1], [4, 15, 16, 3, -1, 23, 1, 3, -1, 1, 3, 5], [5, 14, -1, 15], [6, 15], [7, 6], [8, 6], [9, 6],
                       [10, 15, 3, 6, -1, 23, 1, 3, 6], [11, 10], [12, 7], [13, 7], [14], [15], [16, 15], [17, 15, 16], [18, 17], [19, 17], [20, 17], [21, 17],
                       [22, 15], [23, 1], [24, 15, 16, 1, 3, 6], [25, 24], [26, 25], [27, 15, 1]]

        #Replaces parts of key item logic with logic more suited to the settings
        if settings[1][0] == 1:
            logic_logic[3] = [3, 15, -1, 0, 23]
            logic_logic[4] = [4, 15, 16, 3, -1, 23, 0, 3]
            logic_logic[10] = [10, 15, 3, 6, -1, 23, 0, 3, 6]
            logic_logic[23] = [23, 0]
            logic_logic[24] = [24, 15, 16, 0, 3, 6]
            logic_logic[27] = [27, 15]

        pbar.update(2)

        #Removes items from the key item pool depending on the settings
        l = 0
        s = 0
        while l < len(settings[0]):
            if settings[0][l] == 1.0:
                key_item_check[key_item_pool[s][1]] += 1
                del key_item_pool[s]
                del logic_logic[s]
                s -= 1
            l += 1
            s += 1
        #print(key_item_pool)
        #print(key_item_check)

    with tqdm(total=len(item_pool)+len(key_item_pool)+(len(attack_piece_pool[0])*len(attack_piece_pool)), desc="Randomizing...") as rbar:
        new_item_locals = []
        new_item_logic = []

        #[Trigger type, Room ID, X Pos, Y Pos, Z Pos, Collectible/Cutscene ID, Ability/Item/Key Item/Attack(, Attack Piece ID/Coin Amount/Item Cutscene/Hammer or Spin Cutscene, Coin Cutscene)]
        repack_data = []
        key_data = []
        i = 0
        j = 0
        itemcut = 0
        attackcut = 0
        key_item_pool_checked = []
        new_enemy_stats = []
        enemy_added = []
        attack = random.randint(0, len(attack_piece_pool) - 1)
        while attack == 4 or attack == 8 or attack == 9 or attack == 11 or attack == 13 or attack == 14:
            attack = random.randint(0, len(attack_piece_pool) - 1)
        prevattack = attack
        offset = 0
        prev_offset = 0
        key_order = []
        add_level = 0

        while len(item_pool) + len(key_item_pool) + len(attack_piece_pool) > 0:
            prevlen = len(item_pool) + len(key_item_pool) + len(attack_piece_pool)
            while i < len(item_logic):
                if len(item_logic[i]) > 0 and is_available(area_logic[i], key_item_check, settings):
                    while j < len(item_logic[i]):
                        #print(item_logic[i][j])
                        spot_is_available = is_available(item_logic[i][j], key_item_check, settings)
                        if spot_is_available:
                            rand_array = random.randint(0, 3)
                            if rand_array < 3 and len(item_pool) > 0:
                                #Code for randomizing blocks and bean spots with just eachother
                                nitem = random.randint(0, len(item_pool) - 1)
                                spot_type = item_locals[i][j][2]
                                spot_type &= 0xE30E
                                spot_type += item_pool[nitem][0] & 0x1CF0
                                if spot_type % 0x10 == 2:
                                    spot_type &= 0xFF0F
                                    spot_type += 0x10
                                #print(hex(spot_type))
                                if item_pool[nitem][1] // 0x1000 == 0:
                                    if item_pool[nitem][0] // 0x10 % 0x10 <= 0x1:
                                        max_values[item_pool[nitem][1] % 0x1000 // 2] += 1
                                    else:
                                        max_values[(item_pool[nitem][1] % 0x1000 // 2) + 5] += 1
                                elif item_pool[nitem][1] // 0x1000 == 2:
                                    max_values[(item_pool[nitem][1] % 0x1000 // 2) + 10] += 1
                                elif item_pool[nitem][1] // 0x1000 == 6:
                                    max_values[(item_pool[nitem][1] % 0x1000 // 2) + 45] += 1
                                narray = [item_locals[i][j][0], item_locals[i][j][1], spot_type, item_pool[nitem][1] + (item_locals[i][j][2] // 0x10000),
                                            item_locals[i][j][3], item_locals[i][j][4], item_locals[i][j][5], item_locals[i][j][6]]
                                new_item_locals.append(narray)
                                new_item_logic.append(item_logic[i][j])
                                del item_pool[nitem]
                                del item_locals[i][j]
                                del item_logic[i][j]
                                #print(i)
                                #print(len(item_logic[i]) == 0)
                            elif len(attack_piece_pool) > 0:
                                #Code for putting attacks in blocks and bean spots
                                if len(attack_piece_pool) > 0:
                                    nitem = 0
                                    if len(attack_piece_pool[attack]) > 1:
                                        nitem = random.randint(0, len(attack_piece_pool[attack]) - 1)
                                    narray = [item_locals[i][j][0], item_locals[i][j][1], item_locals[i][j][2] & 0x0012, 0,
                                            item_locals[i][j][3], item_locals[i][j][4], item_locals[i][j][5], item_locals[i][j][6]]
                                    new_item_locals.append(narray)
                                    new_item_logic.append(item_logic[i][j])
                                    spottype = get_spot_type(item_locals[i][j])
                                    if item_locals[i][j][2] % 0x10 == 2:
                                        repack_data.append([spottype, item_locals[i][j][0], item_locals[i][j][3], item_locals[i][j][4], item_locals[i][j][5], item_locals[i][j][6] + 0xD000,
                                                            attack_piece_pool[attack][nitem][1], attack_piece_pool[attack][nitem][0], 0xCD20 + attackcut])
                                        attackcut += 1
                                    else:
                                        repack_data.append([spottype, item_locals[i][j][0], item_locals[i][j][3], item_locals[i][j][4], item_locals[i][j][5], item_locals[i][j][6] + 0xD000,
                                                            attack_piece_pool[attack][nitem][1], attack_piece_pool[attack][nitem][0]])
                                    del attack_piece_pool[attack][nitem]
                                    del item_locals[i][j]
                                    del item_logic[i][j]
                                    #print(i)
                                    #print(len(item_logic[i]) == 0)
                                if len(attack_piece_pool[attack]) == 0:
                                    del attack_piece_pool[attack]
                                    if attack == -1 and len(attack_piece_pool) > 0:
                                        if len(attack_piece_pool) > 1:
                                            if len(attack_piece_pool[-2]) == 1:
                                                attack = -1
                                            elif prevattack < len(attack_piece_pool):
                                                attack = prevattack
                                            else:
                                                attack = random.randint(0, len(attack_piece_pool) - 1)
                                        else:
                                            attack = 0
                                    elif len(attack_piece_pool) > 0:
                                        attack = random.randint(0, len(attack_piece_pool) - 1)
                            j -= 1
                            rbar.update(1)
                        j += 1
                    j = 0
                i += 1
            #Checks if more items can be randomized
            if prevlen <= len(item_pool) + len(key_item_pool) + len(attack_piece_pool) and len(key_item_pool) > 0 and len(new_item_locals) > 0:
                if len(key_item_pool) > 0:
                    if offset == len(new_item_locals):
                        #print(offset)
                        offset = prev_offset
                        #print(offset)
                    can_key = False
                    for i in range(len(new_item_locals) - offset):
                        if find_index_in_2d_list(key_data, new_item_locals[i+offset][7] + 0xD000) is None:
                            can_key = True
                    if can_key:
                        #print(len(new_item_locals))
                        old_spot = random.randint(offset, len(new_item_locals) - 1)
                        while find_index_in_2d_list(key_data, new_item_locals[old_spot][7] + 0xD000) is not None:
                            old_spot = random.randint(offset, len(new_item_locals) - 1)
                        #print(old_spot)

                        item_locals.append([new_item_locals[old_spot][0],
                                            new_item_locals[old_spot][1], new_item_locals[old_spot][2], new_item_locals[old_spot][4],
                                            new_item_locals[old_spot][5], new_item_locals[old_spot][6], new_item_locals[old_spot][7]])
                        item_pool.append([new_item_locals[old_spot][2], new_item_locals[old_spot][3]])
                        repack_index = find_index_in_2d_list(repack_data, new_item_locals[old_spot][7] + 0xD000)
                        if repack_index is not None:
                            if repack_data[repack_index[0]][6] // 0x1000 == 0xB:
                                attack_piece_pool.append([[repack_data[repack_index[0]][7], repack_data[repack_index[0]][6]]])
                                if attack != -1:
                                    prevattack = attack
                                attack = -1
                                #print(attack_piece_pool[attack])
                                del repack_data[repack_index[0]]
                        else:
                            if new_item_locals[old_spot][3] // 0x1000 == 0:
                                if new_item_locals[old_spot][2] // 0x10 % 0x10 <= 0x1:
                                    max_values[new_item_locals[old_spot][3] % 0x1000 // 2] -= 1
                                else:
                                    max_values[(new_item_locals[old_spot][3] % 0x1000 // 2) + 5] -= 1
                            elif new_item_locals[old_spot][3] // 0x1000 == 2:
                                max_values[(new_item_locals[old_spot][3] % 0x1000 // 2) + 10] -= 1
                            elif new_item_locals[old_spot][3] // 0x1000 == 6:
                                max_values[(new_item_locals[old_spot][3] % 0x1000 // 2) + 45] -= 1
                        i = -1

                        # Code for putting key items in blocks and bean spots
                        nitem = random.randint(0, len(key_item_pool) - 1)
                        while not is_available(logic_logic[nitem], key_item_check, settings):
                            nitem = random.randint(0, len(key_item_pool) - 1)
                        #print(nitem)
                        #print(len(key_item_pool))
                        #print(key_item_check)
                        spottype = get_spot_type(item_locals[i])
                        if (key_item_pool[nitem][0] < 0xE000 or key_item_pool[nitem][0] > 0xE004) and key_item_pool[nitem][0] != 0xB0F7:
                            key_data.append(
                                [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                                 item_locals[i][6] + 0xD000, key_item_pool[nitem][0]])
                        elif key_item_pool[nitem][0] != 0xE000:
                            key_data.append(
                                [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                                 item_locals[i][6] + 0xD000, key_item_pool[nitem][0], 0xCDC0 + itemcut])
                            itemcut += 1
                        else:
                            key_data.append(
                                [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                                 item_locals[i][6] + 0xD000, key_item_pool[nitem][0] + key_item_pool[nitem][1],
                                 0xCDC0 + itemcut])
                            itemcut += 1
                        key_item_check[key_item_pool[nitem][1]] += 1
                        key_item_pool_checked.append(key_item_pool[nitem])
                        key_order.append(key_item_pool[nitem][1])
                        del key_item_pool[nitem]
                        del logic_logic[nitem]
                        del item_locals[i]
                        #del item_logic[i]
                        #del new_item_locals[old_spot]
                        prev_offset = offset
                        offset = len(new_item_locals)
                        #print("Previous offset:" + str(prev_offset))
                        #print("Current offset: " + str(offset))
                    else:
                        #If it can't find an item to turn into a key item, it searches a bit farther back
                        prev_offset -= 10
                        offset = len(new_item_locals)
            i = 0
            j = 0

            #Randomizes enemy stats
            while i < len(enemy_logic):
                if len(enemy_logic) > 0 and is_available(area_logic[i], key_item_check, settings):
                    while j < len(enemy_logic[i]):
                        if is_available(enemy_logic[i][j], key_item_check, settings):
                            try:
                                enemy_added.index(enemy_logic[i][j][0])
                            except ValueError:
                                #print(enemy_logic[i][j][0])
                                enemy_added.append(enemy_logic[i][j][0])
                                new_enemy_stats.append([enemy_logic[i][j][0], int(init_enemy_stats[1]), int(init_enemy_stats[2]), int(init_enemy_stats[3]),
                                                        int(init_enemy_stats[4]), int(init_enemy_stats[5]), int(init_enemy_stats[6]), 0, 0, 0, 0, 0,
                                                        int(init_enemy_stats[0])])
                                #Increase level by 1 every 3 enemies
                                #Increase HP by 1.5 every enemy
                                #Increase POW by 2 every enemy
                                #Increase DEF by 1.5 every enemy
                                #Increase SPEED by 1 every enemy
                                #Increase EXP by 2.5 every enemy
                                #Increase COINS by 0.75 every enemy
                                add_level += 1
                                if add_level == 3:
                                    init_enemy_stats[0] += 1
                                    add_level = 1
                                init_enemy_stats[1] += 3
                                init_enemy_stats[2] += 2.5 * stat_mult[0]
                                init_enemy_stats[3] += 3
                                init_enemy_stats[4] += 1.5
                                init_enemy_stats[5] += 2.5 * stat_mult[1]
                                init_enemy_stats[6] += 0.5

                                for stat in range(len(new_enemy_stats[-1])):
                                    if new_enemy_stats[-1][stat] < 1:
                                        new_enemy_stats[-1][stat] = 1
                                    elif new_enemy_stats[-1][stat] > 0xFFFF:
                                        new_enemy_stats[-1][stat] = 0xFFFF
                                #print(init_enemy_stats)
                                #print(new_enemy_stats[-1])

                                if new_enemy_stats[-1][0] == 87:
                                    new_enemy_stats[-1][5] //= 4
                                    new_enemy_stats[-1][6] //= 4
                                    new_enemy_stats.append([88, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([89, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                elif (new_enemy_stats[-1][0] == 19 or new_enemy_stats[-1][0] == 33 or new_enemy_stats[-1][0] == 45 or new_enemy_stats[-1][0] == 47 or
                                new_enemy_stats[-1][0] == 49 or new_enemy_stats[-1][0] == 64 or new_enemy_stats[-1][0] == 72 or new_enemy_stats[-1][0] == 78 or
                                new_enemy_stats[-1][0] == 99 or new_enemy_stats[-1][0] == 112 or new_enemy_stats[-1][0] == 121 or new_enemy_stats[-1][0] == 123 or
                                new_enemy_stats[-1][0] == 124):
                                    new_enemy_stats[-1][1] //= 3
                                    new_enemy_stats[-1][5] //= 5
                                    new_enemy_stats[-1][6] //= 5
                                    if new_enemy_stats[-1][0] == 33:
                                        new_enemy_stats[-1][1] //= 2
                                        new_enemy_stats[-1][5] //= 2
                                    #print(new_enemy_stats[-1])

                            #del enemy_stats_rand[i]
                            del enemy_logic[i][j]
                            j -= 1
                        j += 1
                j = 0
                i += 1
            i = 0
            while i < len(boss_logic):
                if len(boss_logic) > 0 and is_available(area_logic[i], key_item_check, settings):
                    while j < len(boss_logic[i]):
                        if is_available(boss_logic[i][j], key_item_check, settings):
                            try:
                                enemy_added.index(boss_logic[i][j][0])
                            except ValueError:
                                #print(enemy_logic[i][j][0])
                                enemy_added.append(boss_logic[i][j][0])
                                new_enemy_stats.append([boss_logic[i][j][0], int(init_boss_stats[1] + (len(new_enemy_stats) * 24)), int(init_boss_stats[2] + (len(new_enemy_stats) * 4 * stat_mult[0])),
                                                        int(init_boss_stats[3] + (len(new_enemy_stats) * 3)), int(init_boss_stats[4] + (len(new_enemy_stats) // 1.5)), int((init_boss_stats[5] + (len(new_enemy_stats) * 75 * stat_mult[1])) / 2),
                                                        int(init_boss_stats[6] + (len(new_enemy_stats))), 0, 0, 0, 0, 0, int(init_boss_stats[0] + ((len(new_enemy_stats) // 2.5) + 1))])

                                for stat in range(len(new_enemy_stats[-1])):
                                    if new_enemy_stats[-1][stat] < 1:
                                        new_enemy_stats[-1][stat] = 1
                                    elif new_enemy_stats[-1][stat] > 0xFFFF:
                                        new_enemy_stats[-1][stat] = 0xFFFF
                                #print(new_enemy_stats[-1])

                                if new_enemy_stats[-1][0] == 107:
                                    for m in range(5):
                                        new_enemy_stats[-1][m+1] //= 2
                                    new_enemy_stats.append([108, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                elif new_enemy_stats[-1][0] == 17 or new_enemy_stats[-1][0] == 128:
                                    new_enemy_stats[-1][1] //= 4
                                    new_enemy_stats[-1][5] //= 4
                                    new_enemy_stats[-1][6] //= 4
                                    if new_enemy_stats[-1][0] == 128:
                                        new_enemy_stats.append([129, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                                new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                                new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                                new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                        new_enemy_stats.append([130, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                                new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                                new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                                new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                        new_enemy_stats.append([131, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                                new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                                new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                                new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                elif new_enemy_stats[-1][0] == 145:
                                    new_enemy_stats[-1][5] = 0
                                    new_enemy_stats[-1][6] = 0
                                    new_enemy_stats.append([146, new_enemy_stats[-1][1] // 8, new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([147, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([148, new_enemy_stats[-1][1] // 2, new_enemy_stats[-1][2] // 4, new_enemy_stats[-1][3] // 3,
                                                            new_enemy_stats[-1][4] + 10, new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([149, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([150, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([151, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([152, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                elif new_enemy_stats[-1][0] == 79:
                                    new_enemy_stats.append([80, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                                    new_enemy_stats.append([81, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                            new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                            new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                            new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])

                            del boss_logic[i][j]
                            j -= 1
                        j += 1
                j = 0
                i += 1
            i = 0

            #Swaps a coin with whatever is left in the item pool
            if (len(item_pool) > 0 or len(attack_piece_pool) > 0) and len(key_item_pool) == 0:
                item = 0
                while new_item_locals[item][3] != 0 or find_index_in_2d_list(repack_data, new_item_locals[item][7] + 0xD000) is not None:
                    item += 1
                    if item == len(new_item_locals):
                        item -= 1
                        break
                item_locals[get_zone_id(new_item_locals[item][0], new_item_locals[item][7])].append([new_item_locals[item][0], new_item_locals[item][1], new_item_locals[item][2], new_item_locals[item][4], new_item_locals[item][5], new_item_locals[item][6], new_item_locals[item][7]])
                item_logic[get_zone_id(new_item_locals[item][0], new_item_locals[item][7])].append([0])
                del new_item_locals[item]

    #hammer_local = find_index_in_2d_list(repack_data, 0xC369)
    #print(repack_data[hammer_local[0]])

    for k in key_data:
        repack_data.append(k)

    #print(key_item_pool_checked)
    #print(max_values)
    with tqdm(total=len(new_item_locals)*2, desc="Generating Spoiler Log...") as sbar:
        #Names for all the locations
        item_local_names = ["Entrance", "Hammer Room", "West of Hammer Room", "River Rocks",
                            "Upper Attack Piece Room", "Lower Attack Piece Room", "Gate Room",
                            "Fountain Room", "Lower Ultibed Rock Room", "Right of Hammer Room", "Right Ultibed Rock Room", "Maintenance Hut", "Many Enemy Room",
                            "Early Hammer Room", "Outside", "Mushrise Treeboard Room", "Western Track Room",
                            "Drill Machine Tutorial Room", "Mini/Mole Mario Tutorial Room", "Middle Track Room",
                            "Upper Track Room", "Early First Track Room", "Early Main Track Room", "Mini Mario Room",
                            "Underground", "Southeastern Track Room", "East of Dreamstone", "West of Pi'illo Castle",
                            "In Front of Pi'illo Castle", "Test Room", "Eldream Room 1",
                            "Eldream Room 2", "Eldream Room 3", "Eldream Room 4",
                            "Eldream Room 5", "Eldream Item Detour Room", "Eldream Fountain Room",
                            "Eldream Room 7", "Eldream Bouncy Flower Room", "Eldream Pipe to Sewers",
                            "Eldream Sewers", "Eldream Throw Boss Brickle", "Eldream Buildup to Final Attack Piece", "Eldream Final Attack Piece",
                            "Pi'illo to Hammers", "Eldream Clouds 1", "Eldream Clouds 2", "Eldream Confront Bunny", "Pi'illo in River Room",
                            "Pi'illo Room 2", "Ultibed Pi'illo Room 2", "Buildup 2", "Entrance", "Tour Center Location", "Shopping District", "Early Room 3",
                            "Outside Rose Broquet", "Southern Panel Room", "Dream Egg Dreampoint Room", "Crab Minigame", "Entrance Right Room", "Entrance Middle Room",
                            "Entrance Left Room", "Bedsmith Room First Floor", "Kylie Koopa's Photo Booth", "Tour Center", "Item Shop", "Badge Shop", "Gear Shop",
                            "Rose Broquet Shop", "Broque Madame's Spot", "Ultibed Cave Entrance", "Ultibed Cave Middle Room", "Driftwood Jelly Sheets Resting Spot",
                            "Entrance", "Guard Room", "Seabelle Dreampoint Room", "Middle Warp Pipe Room", "Unused Room", "Seabury Dreampoint Room",
                            "Glitched Room 1", "Wakeport?", "Glitched Room 2", "Glitched Room 3", "Glitched Room 4", "Glitched Room 5",
                            "Toad Crash Room", "Removed Second Check-X Quiz Room", "Second Toad Crash Room", "Gromba Battle Arena", "Bridge Room",
                            "East of Pi'illo Castle", "Behind Pi'illo Castle", "Badge Room", "Mushrise Park Minimap", "Weak Trembling Fortress",
                            "East Track Room", "Ultibed Cliff", "Desert Entrance", "Check-X Quiz", "Starting Room", "Test Room 2", "Entrance", "Rock Room",
                            "First Mega Pi'illo Room", "Weird Lift Thingy Room", "2 Pi'illos in Rocks Room", "Weird Lift Thingy Second Room",
                            "Spin Jump Tutorial Room", "Southeast Deviation", "Southwest Spin Jump Gaps", "Spin Jump Whirlwind Tutorial Room", "West Deviation",
                            "Removed Room", "Peak Before Big Jump", "Big Fall", "Pajamaja Base Warp Pipe Room", "Side Drill Tutorial Room", "Large Room Before Snow",
                            "Second Mega Pi'illo Room", "Path to Right Massif Ice Room", "Right Massif Ice Room", "Bros Wear Room", "Path to Left Massif Ice Room", "Left Massif Ice Room",
                            "Mammoshka Arena", "Peak", "Frozen Dream World", "Peak Pipe", "Ball Hop Cave", "Lobby", "Early Minimap", "Golden Pipe Room", "Bedroom Entrance",
                            "Platform Area", "Staff Break Room", "Shop", "Hotel Entrance", "Hotel Lobby", "Hotel Left Room", "Hotel Topleft Room", "Hotel Top Room", "Hotel Topright Room",
                            "Ball Hop Room Entrance", "Ride to Underground", "Underground Entrance", "Removed Minigame", "Gromba Circle", "Smoldergeist Arena",
                            "Stairs to Smoldergeist", "Underground Save Room", "Collection Room", "Battle Ring", "Restaurant District", "Hotel Balcony", "North Balcony", "Minimap 1",
                            "Camera Block Pi'illo Room 2", "Black Screen Crash", "Early Mushrise Minimap 2", "Sick Map Warper", "Swimming", "Dreambert Entrance", "Dreambert Door Tutorial Room",
                            "Dreambert Many Door Room", "Dreambert First Dreamy Enemy Room", "Dreambert Broque Shop", "Dreambert Many Enemy Room", "Dreambert Dreamy Mario Arena",
                            "Dreambert Revival Room", "Entrance to Dream's Deep", "Unused", "First Fling Pi'illo Entrance", "First Fling Pi'illo Room 2", "First Fling Pi'illo Room 3",
                            "Britta's Meeting Room", "Eldream Topright Detour", "First Dozite Room 1", "First Track Dozite Room 1", "First Track Dozite Room 2", "First Track Dozite Room 3",
                            "Second Track Dozite", "Third Track Dozite", "Final Track Dozite Room 1", "Final Track Dozite Room 2", "Final Track Dozite Room 3", "Dream Stone Entrance",
                            "Dream Stone First Drill Room", "Dream Stone Main Room", "Dream Stone Big Drill Room", "Dream Stone After Big Drill Room", "Dream Stone First Luiginary Room",
                            "Dream Stone Switch Puzzle Room 1", "Dream Stone After Switch Puzzle 1", "Dream Stone Many Enemy Room", "Dream Stone Britta Shop", "Dream Stone After 2nd Spirit Talk",
                            "Dream Stone Spinning Room", "Dream Stone Ground Pound Room", "Dream Stone Before Last Attack Pieces", "Beta Room 1", "Beta Room 2",
                            "Unused Northwest Bedroom 1", "Unused Northwest Bedroom 2", "Unused Northeast Bedroom", "Early Underground Gromba Circle", "Early Smoldergeist",
                            "Beta Room 3", "Beta Room 4", "Beta Room 5", "Dream Egg Dream Entrance", "Dream Egg Dream First Egg Departure", "Dream Egg Dream First Egg Entrance",
                            "Dream Egg Dream First Egg Room 1", "Dream Egg Dream First Egg Room 2", "Glitched Room", "Second Throw Pi'illo Room 1", "Second Throw Pi'illo Room 2",
                            "Second Throw Pi'illo Room 3", "First Pi'illo Room 1", "First Pi'illo Room 2", "First Pi'illo Room 3", "First Pi'illo Room 4", "Unused 1", "Unused 2",
                            "Unused 3", "Unused 4", "Unused 5", "Dream Stone Dream Last Attack Pieces", "Dream Stone Dream After Last Attack Pieces", "Dream Stone Dream Zigzag",
                            "Mattress Dream Entrance", "Mattress Dream Bottom Room", "Mattress Dream Top Room", "Mattress Dream Right Room", "Badge Room Pi'illo",
                            "Southeast Track Room Pi'illo", "Eastern Track Room Pi'illo", "Main Track Room Pi'illo", "First Ultibed Pi'illo Room 2", "Second Ultibed Pi'illo Room 2",
                            "Dream's Deep Entrance", "Dream's Deep Hallway Warps", "Bowser and Antasma Arena", "Dream's Deep Entrance", "Learn Luiginary Ball Room",
                            "Learn Luiginary Hookshot Room", "Dream's Deep Room 4", "Dream's Deep Room 5", "Dream's Deep Room 6", "Learn Luiginary Throw Room",
                            "Zeekeeper Cloud Ride", "Zeekeeper Before Boss", "Zeekeeper Arena", "Glitched 00 Room 1", "Glitched 00 Room 2", "Summit Ball Hop Gate", "End of Track Room",
                            "Dreamstone Room", "Mattress Underground 1", "Mattress Underground 2", "Dreamy Dozing Sands Unused", "Massif Entrance", "Glitched 00 Room 3",
                            "Buildup 1", "Wiggler and Popple Arena", "Bedsmith Basement", "Rock Frame Room", "Ball Hop Tutorial Room", "Massif Lobby", "Massif Hooraw Main Room",
                            "Massif Topright of Main", "Massif Clock Tutorial", "Massif After Clock Tutorial", "Massif Heavy Zest Room 1", "Massif Heavy Zest Room 2", "Massif Heavy Zest Room 3",
                            "Massif Heavy Zest Arena", "Massif Thunder Sass Room 1", "Massif Thunder Sass Room 2", "Massif Thunder Sass Room 3", "Massif Thunder Sass Arena",
                            "Massif Topleft of Main Room 2", "Massif Topleft of Main Room 1", "Massif Sorrow Fist Room 1", "Massif Sorrow Fist Room 2", "Massif Sorrow Fist Room 3",
                            "Massif Sorrow Fist Arena", "Massif Beef Cloud Before Arena", "Massif Beef Cloud Arena", "Massif Window Room", "Bedsmith Entrance", "Bedsmith Room 2", "Bedsmith Room 3",
                            "Bedsmith Room 3 Detour", "Bedsmith Room 4", "Bedsmith Room 4 Detour", "Bedsmith Room 5", "Bedsmith Room 6", "Bedsmith Upper Umbrella Puzzle", "Bedsmith Earthwake Arena",
                            "South Room Pi'illo", "After Puzzle Pi'illo Room 1", "After Puzzle Pi'illo Room 2", "Eastern Pi'illo", "Left of Wiggler Pi'illo Entrance", "Left of Wiggler Pi'illo Main Room",
                            "Right of Wiggler Pi'illo Entrance", "Right of Wiggler Pi'illo Main Room", "Disco Blocks", "Ball Hop Room", "Jump Tutorial", "Path to Ultibed Room 2",
                            "Under Blimport Bridge Falling Point", "Under Blimport Bridge First Pi'illo Room", "Under Blimport Bridge Second Fling Pi'illo Room", "First Dozite Wall of Enemies",
                            "First Dozite Learn Luiginary Stack", "First Dozite Final Puzzle", "Base Right Mega Pi'illo Entrance", "Entrance Before Castle Falls", "Entrance", "Pipe Room", "Kamek 1 Left Room",
                            "Kamek 1 Lobby", "Kamek 1 Right Room", "Kamek 1 Top Left", "Kamek 1 North of Lobby", "Kamek 1 Top Right", "First Elevator Lower Room", "First Elevator Upper Room",
                            "First Bomb Room", "Kamek 2 Left Room", "Kamek 2 Lobby", "Kamek 2 Right Room", "Above Kamek 2", "West of Kamek 3 Lobby", "Kamek 3 Lobby", "Kamek 3 Right Room",
                            "Kamek 3 Western Bomb Room", "Kamek 3 Middle Bomb Room", "Kamek 3 Eastern Bomb Room", "Elevator to Final Puzzle", "Final Puzzle Lobby", "Left Balcony", "Right Balcony",
                            "Bottom Left of Final Puzzle Room", "Bottom Right of Final Puzzle Room", "Front Balcony", "Bowser's Dream Room", "Antasma Battle Arena", "Spiral to Final Boss", "Finall Bowser Arena",
                            "Dream Egg Dream First Egg Room 3", "Dream Egg Dream First Egg Puzzle Room", "Dream Egg Dream Second Egg Lobby", "Dream Egg Dream Second Egg Room 1", "Dream Egg Dream Second Egg Room 2 Side Room",
                            "Dream Egg Dream Second Egg Room 4", "Dream Egg Dream Second Egg Room 5", "Dream Egg Dream Second Egg Puzzle Room", "Dream Egg Dream Third Egg Lobby", "Dream Egg Dream Third Egg Room 1",
                            "Dream Egg Dream Third Egg Room 3", "Dream Egg Dream First Egg Room 2 Side Room", "Dream Egg Dream Third Egg Puzzle Room", "Dream Egg Dream Third Egg Room 2", "Dream Egg Dream Shop Area",
                            "Dream Egg Dream Second Egg Entrance", "Dream Egg Dream Third Egg Entrance", "Dream Egg Dream Elite Trio Arena", "Seatoon Entrance", "Seatoon Inner Tube Intro",
                            "Seatoon Room 3", "Seatoon Room 4", "Seatoon Cutscene", "Seabury Entrance", "Seabury Puzzle", "Seabury Cutscene", "Seabelle Entrance", "Seabelle Puzzle", "Seabelle Cutscene",
                            "Rose Broquet Pi'illo", "Under Dream Egg Dream Pi'illo Path Room", "Under Dream Egg Dream Pi'illo Left Room", "Under Dream Egg Dream Pi'illo Right Room", "Ultibed Path Pi'illo",
                            "Entrance", "Woods Entrance", "Bedsmith Room", "Poison Water Puzzle 1", "Poison Water Puzzle 2", "Poison Water Side Drill Junction", "First Pi'illo Master Room", "Lower Elevator Room",
                            "Main Puzzle Tracks Area", "Bottom Right Track Room", "Bottom Right Pi'illo Master Room", "Middle Right Track Room", "Top Right Track Room", "Bottom Left Track Room",
                            "Middle Left Track Room", "Top Left Track Room Entrance", "Top Left Track Room Pi'illo", "Top Left Track Room Cave", "Room Before Pi'illodium", "Pi'illodium Arena",
                            "Collapsing Antasma Cutscene", "Crash", "Ultibed Pi'illo Entrance", "Left of Camera Block Pi'illo Entrance", "Entrance Pi'illo Entrance", "Dreamy Dozing Minimap", "Dreamy Dozing Minimap",
                            "Dreamy Dozing Minimap", "Dreamy Dozing Minimap", "Dreamy Dozing Minimap", "Dreamy Dozing Minimap", "Crash", "Crash", "Dreamy Dozing Minimap", "Dreamy Dozing Minimap", "Dreamy Dozing Minimap",
                            "Dreamy Dozing Minimap", "Dreamy Dozing Minimap", "Dreamy Dozing Minimap", "Crash", "Dreamy Wakeport Minimap", "Dreamy Wakeport Minimap", "Dreamy Wakeport Minimap", "Dreamy Wakeport Minimap",
                            "Dreamy Wakeport Minimap", "Dreamy Wakeport Minimap", "Crash", "Crash", "Crash", "Crash", "Dreamy Driftwood Shore Minimap", "Dreamy Driftwood Shore Minimap", "Dreamy Driftwood Shore Minimap",
                            "Dream's Deep?", "Crash", "Dreamy Mount Pajamaja", "Crash", "Crash", "Crash", "Crash", "Crash", "Crash", "Crash", "Crash", "Minimap 1", "Minimap 2", "Minimap 3", "Minimap 4", "Minimap 5",
                            "Path to Somnom Woods and Neo Bowser Castle", "Dream Egg Dream Second Egg Room 2", "Dream Egg Dream Second Egg Room 3", "Torkscrew Minigame", "Dreamy Driftwood Background",
                            "Hallway of Luigis", "Long Drop", "Bedsmith Earthwake Arena After Fight", "Blimport", "Blimport", "Blimport", "Dreamy Mushrise Park Minimap", "Unused Dreamy Wakeport Room",
                            "Dreamy Mushrise Park Minimap", "Dozite 2 Final Room", "Broken Snoozemore Projection Video", "Deep Pi'illo Castle Block Room", "Snoozemore Projection Video",
                            "Dreambert Explains Island History", "Dreambert Introduces Antasma", "Left End of Track Room", "Bowser's Introduction", "Save Tutorial", "Fountain Breaks 3DS Screen",
                            "Glitched 00 Room", "Bedsmith Umbrella Puzzle Basement", "Blimport Minimap", "Dreamy Room", "WHAT THE-", "Dreamy Room", "Kylie Koopa Puzzle Menu", "Base Right Mega Pi'illo Room 2",
                            "Base Left Mega Pi'illo", "Peak Left Mega Pi'illo Entrance", "Peak Left Mega Pi'illo Room 2", "Peak Left Mega Pi'illo Room 3", "Peak Right Mega Pi'illo Entrance", "Peak Right Mega Pi'illo Main",
                            "Summit Dream Portal Room", "Summit Massif Shop", "Summit Room 4", "Summit Room 5", "Summit Room 6", "Summit Room 7", "Summit Room 8", "Summit Room 8 Detour", "Summit Room 9", "Summit Room 9 Detour",
                            "Summit Cone Tornado Tutorial Room", "Summit Fountain Room", "Summit Between Fountain and Shop", "Summit After Healing 1", "Summit First Tornado Block Room",
                            "Summit After Healing 3", "Summit After Healing 3 Side Room", "Summit After Healing 4", "Summit Snowstorm Room", "Summit Before Arena", "Summit Mount Pajamaja Arena",
                            "Early Dreamy Pajamaja Minimap", "Summit Room 3", "Pajamaja Rock Frame Room 1", "Pajamaja Rock Frame Room 2", "Pajamaja Rock Frame Room 3", "Multi-Access Dream World",
                            "Base Southwest Ball Hop Pi'illo Entrance", "Base Southwest Ball Hop Pi'illo", "Unused Dreamy Pajamaja", "Peak Before Jump Pi'illo Entrance", "Peak Before Jump Pi'illo Main", "Right Branching Path Pi'illo",
                            "Crash", "Crash", "Crash", "Crash", "Crash", "Minimap", "Crash", "Crash", "Crash", "Annoying Quadruple Bomb Room", "Pi'illo Master 1", "Pi'illo Master 2 Room 1",
                            "Pi'illo Master 2 Room 2", "Pi'illo Master 2 Room 3", "Southeast Pi'illo Master Room 1", "Southeast Pi'illo Master Room 2", "Southwest Pi'illo Master Room 1", "Southwest Pi'illo Master Room 2",
                            "West Pi'illo Master Room 1", "West Pi'illo Master Room 2", "Northwest Pi'illo Master", "Zeekeeper Entrance", "Zeekeeper Tower", "Zeekeeper Coin Labyrinth", "Zeekeeper Wrong Path",
                            "Zeekeeper Monster Path", "Zeekeeper Correct Path", "Zeekeeper After Correct Path", "Zeekeeper Many Pipe Room", "Zeekeeper First Windy Room", "Zeekeeper Vertical Windy Room",
                            "Zeekeeper First Luiginary Work Room", "Zeekeeper Large Sneeze Room", "Zeekeeper Large Luiginary Work Room", "Zeekeeper Right Moustache Room", "Zeekeeper Left Moustache Room",
                            "Zeekeeper Underground 1-2 Reference", "Lower Elevator Pi'illo", "Other Pi'illo in First Pi'illo Master Room", "Upper Double Pi'illo", "Lower Double Pi'illo", "Poison Water Pi'illo",
                            "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap",
                            "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Minimap", "Giant Room Fling Pi'illo Entrance", "Minimap", "Kamek 1 Entrance", "Kamek 1 Main Room", "Kamek 1 Antigravity Intro",
                            "Kamek 1 Red Coin Room", "Kamek 1 Swimming Kick Tutorial", "Kamek 1 Enemy Room", "Kamek 1 Spike Maze", "Kamek 1 Arena", "Kamek 2 Entrance", "Kamek 2 Door", "Kamek 2 Rising Lava",
                            "Kamek 2 Before Arena", "Kamek 2 Arena", "Kamek 3 Entrance", "Kamek 3 Room 2", "Kamek 3 Room 3", "Kamek 3 Room 4", "Kamek 3 Arena", "Left Flame Room 1", "Left Flame Room 2", "Left Flame Room 3",
                            "Left Flame Room 4", "Bottom Right Flame Room 1", "Bottom Right Flame Room 2", "Bottom Right Flame Room 3", "Top Right Flame Room 1", "Top Right Flame Room 2", "Top Right Flame Room 3",
                            "Bowser's Dream Entrance", "Bowser's Dream First Bowser Encounter", "Bowser's Dream Path Back 1", "Bowser's Dream Path Back 2", "Bowser's Dream Path Back 3", "Bowser's Dream Path Back 4",
                            "Bowser's Dream Path Back 5", "Bowser's Dream Path Back 6", "Bowser's Dream Path Back 7", "Bowser's Dream Shop", "Bowser's Dream Giant Cannon", "Bowser's Dream More Giant Cannons",
                            "Bowser's Dream Arena", "Bowser's Dream Arena After Boss", "Crash", "Crash", "Crash", "Crash", "Crash", "Crash", "Crash", "Dreamy Mount Pajamaja", "Dreamy Neo Bowser Castle",
                            "Dreamy Somnom Woods", "Dreamy Driftwood Shore", "Boss Brickle Runs Off", "Bottom Left", "Ring Game", "Main Track Room Entrance", "Final Boss Room Copy", "Intro",
                            "Glitched Mushrise Minimap", "Glitched Mushrise Minimap", "Top Right Flame Room 4", "Big Fling Pi'illo Room 2"]
        #for n in range(len(item_local_names)):
        #    print(hex(n) + " " + item_local_names[n])

        #Names for items
        item_names = [["Coin", "5 Coins", "10 Coins", "50 Coins", "100 Coins"],

                      ["Mushroom", "Super Mushroom", "Ultra Mushroom", "Max Mushroom", "Nut", "Super Nut", "Ultra Nut", "Max Nut", "Syrup Jar", "Supersyrup Jar", "Ultrasyrup Jar", "Max Syrup Jar",
                       "Candy", "Super Candy", "Ultra Candy", "Max Candy", "1-Up Mushroom", "1-Up Deluxe", "Refreshing Herb", "Heart Bean", "Bros. Bean", "Power Bean", "Defense Bean", "Speed Bean",
                       "Stache Bean", "Taunt Ball", "Shock Bomb", "Boo Biscuit", "Secret Box", "Heart Bean DX", "Bros Bean DX", "Power Bean DX", "Defense Bean DX", "Speed Bean DX", "Stache Bean DX"],

                      ["Starter Badge", "Master Badge", "Expert Badge", "Bronze Badge", "Silver Badge", "Gold Badge", "Mush Badge", "Strike Badge", "Guard Badge", "Virus Badge", "Risk Badge", "Miracle Badge"],

                      ["Run-Down Boots", "Discount Boots", "So-So Boots", "Sandwich Boots", "Bare Boots", "Iron-Ball Boots", "Trusty Boots", "Snare Boots", "Coin Boots", "Super Boots", "EXP Boots",
                       "Knockout Boots", "Heart Boots", "Elite Boots", "Anti-air Boots", "Action Boots", "Bros. Boots", "Singular Boots", "Glass Boots", "Coin Boots DX", "Iron-Ball Boots DX", "VIP Boots",
                       "EXP Boots DX", "Anti-air Boots DX", "Bare Boots DX", "Star Boots", "Dark Boots", "Crystal Boots", "Wellington Boots", "Pro Boots", "Supreme Boots", "Challenge Boots", "Hiking Boots",
                       "DoB Boots", "MINI Boots", "Run-Down Hammer", "Discount Hammer", "So-So Hammer", "Picnic Hammer", "Bare Hammer", "Iron-Ball Hammer", "Steady Hammer", "Fighter Hammer", "Sap Hammer",
                       "Super Hammer", "Soft Hammer", "Knockout Hammer", "Flame Hammer", "Elite Hammer", "Blunt Hammer", "Action Hammer", "Spin Hammer", "Singular Hammer", "Glass Hammer", "Sap Hammer DX",
                       "Iron-Ball Hammer DX", "VIP Hammer", "Flame Hammer DX", "Blunt Hammer DX", "Bare Hammer DX", "Star Hammer", "Dark Hammer", "Crystal Hammer", "Soft Hammer DX", "Pro Hammer", "Supreme Hammer",
                       "Challenge Hammer", "Golden Hammer", "DoB Hammer", "MINI Hammer", "Thin Wear", "Picnic Wear", "Cozy Wear", "So-So Wear", "Retribution Wear", "Singular Wear", "Rally Wear", "Filler Wear",
                       "Super Wear", "Fighter Wear", "Koopa Troopa Wear", "VIP Wear", "Counter Wear", "Safety Wear", "Fancy Wear", "Hero Wear", "Bros. Wear", "Metal Wear", "Snare Wear", "Heart Wear", "Boost Wear",
                       "Star Wear", "Ironclad Wear", "King Wear", "Angel Wear", "Pro Wear", "Legendary Wear", "Challenge Wear", "Golden Wear", "DoB Wear", "Thick Gloves", "Shell Gloves", "Metal Gloves", "HP Gloves",
                       "HP Gloves DX", "BP Gloves", "BP Gloves DX", "POW Gloves", "POW Gloves DX", "Speed Gloves", "Stache Gloves", "Lucky Gloves", "Lucky Gloves DX", "Gift Gloves", "Gift Gloves DX", "Filler Gloves",
                       "Filler Gloves DX", "Strike Gloves", "Mushroom Gloves", "1-Up Gloves", "Pro Gloves", "Rookie Gloves", "Perfect POW Gloves", "Perfect Bro Gloves", "Coin Bro Gloves", "Coin Bro Gloves DX", "EXP Bro Gloves",
                       "EXP Bro Gloves DX", "Bottomless Gloves", "MINI Gloves", "HP Scarf", "HP Scarf DX", "BP Scarf", "BP Scarf DX", "POW Scarf", "POW Scarf DX", "Speed Scarf", "Stache Scarf", "Bros. Ring", "HP Bangle",
                       "HP Bangle DX", "BP Bangle", "BP Bangle DX", "Angel Bangle", "HP Knockout Bangle", "BP Knockout Bangle", "Healthy Ring", "Guard Shell", "Guard Shell DX", "Rally Belt", "Counter Belt", "POW Mush Jam",
                       "DEF Mush Jam", "Duplex Crown", " -- ", "Mushroom Amulet", "DoB Ring", "Mini Ring", "Silver Statue", "Gold Statue"]]

        #Names for key items
        key_item_names = ["Progressive Hammers 1", "Progressive Hammers " + str(settings[3][0] + 2), "Progressive Hammers " + str(3 - settings[3][0]), "Progressive Spin 1", "Progressive Spin 2", "Ball Hop", "Luiginary Works", "Luiginary Ball", "Luiginary Stack Spring Jump",
                          "Luiginary Stack Ground Pound", "Luiginary Cone Jump", "Luiginary Cone Storm", "Luiginary Ball Hookshot", "Luiginary Ball Throw", "Pi'illo Castle Key", "Blimport Bridge", "Mushrise Park Gate",
                          "First Dozite", "Dozite 1", "Dozite 2", "Dozite 3", "Dozite 4", "Access to Wakeport", "Access to Mount Pajamaja", "Dream Egg 1", "Dream Egg 2", "Dream Egg 3", "Access to Neo Bowser Castle"]

        #Names for attack pieces
        attack_piece_names = ["Mushrise Park", "Dreamy Mushrise Park", "Dozing Sands", "Dreamy Dozing Sands", "Wakeport", "Mount Pajamaja", "Dreamy Mount Pajamaja", "Driftwood Shore", "Dreamy Driftwood Shore",
                              "Mount Pajamaja Summit", "Dreamy Wakeport", "Somnom Woods", "Dreamy Somnom Woods", "Mushrise Park Caves", "Neo Bowser Castle"]

        #Names for the different kinds of checks
        check_names = ["Block", "Block", "Rotated Block", "Rotated Block", "Rotated Block", "Bean Spot", "Sneeze Block", "Attack Piece Block", "Rotated Block", "Rotated Block"]

        #Sorts the new item locals array in order of room ID and spot ID
        new_item_locals = sorted(new_item_locals, key=lambda local: local[0])
        repack_data = sorted(repack_data, key=lambda key: key[1])
        rooms = []
        areas = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        temp = []
        for i in range(len(new_item_locals)):
            if i > 0:
                if new_item_locals[i][0] == new_item_locals[i-1][0]:
                    rooms.append(new_item_locals[i])
                else:
                    rooms = sorted(rooms, key=lambda local: local[7])

                    #Sorts the room into a specific spot
                    if get_room(rooms[-1][0]) == "Mushrise Park":
                        room = 3
                    elif get_room(rooms[-1][0]) == "Dozing Sands":
                        room = 5
                    elif get_room(rooms[-1][0]) == "Blimport":
                        room = 0
                    elif get_room(rooms[-1][0]) == "Dreamy Mushrise Park":
                        room = 4
                    elif get_room(rooms[-1][0]) == "Wakeport":
                        room = 7
                    elif get_room(rooms[-1][0]) == "Driftwood Shore":
                        room = 11
                    elif get_room(rooms[-1][0]) == "Mount Pajamaja":
                        room = 9
                    elif get_room(rooms[-1][0]) == "Pi'illo Castle":
                        room = 1
                    elif get_room(rooms[-1][0]) == "Dreamy Pi'illo Castle":
                        room = 2
                    elif get_room(rooms[-1][0]) == "Dreamy Dozing Sands":
                        room = 6
                    elif get_room(rooms[-1][0]) == "Dreamy Driftwood Shore":
                        room = 12
                    elif get_room(rooms[-1][0]) == "Dreamy Wakeport":
                        room = 8
                    elif get_room(rooms[-1][0]) == "Neo Bowser Castle":
                        room = 15
                    elif get_room(rooms[-1][0]) == "Somnom Woods":
                        room = 13
                    elif get_room(rooms[-1][0]) == "Dreamy Mount Pajamaja":
                        room = 10
                    elif get_room(rooms[-1][0]) == "Dreamy Somnom Woods":
                        room = 14
                    elif get_room(rooms[-1][0]) == "Dreamy Neo Bowser Castle":
                        room = 16
                    else:
                        room = 17
                    if len(areas[room]) > 1:
                        spot = 1
                        while areas[room][spot-1][0] < areas[room][spot][0]:
                            spot += 1
                            if spot == len(areas[room]):
                                break
                        areas[room].insert(spot, rooms)
                    else:
                        if len(areas[room]) == 0:
                            areas[room].append(rooms)
                        else:
                            if areas[room][0][0] <= areas[room][-1][0]:
                                areas[room].append(rooms)
                            else:
                                areas[room].insert(0, rooms)
                    rooms = [new_item_locals[i]]
            else:
                rooms.append(new_item_locals[i])
            sbar.update(1)

        rooms = sorted(rooms, key=lambda local: local[7])
        if get_room(rooms[-1][0]) == "Mushrise Park":
            room = 3
        elif get_room(rooms[-1][0]) == "Dozing Sands":
            room = 5
        elif get_room(rooms[-1][0]) == "Blimport":
            room = 0
        elif get_room(rooms[-1][0]) == "Dreamy Mushrise Park":
            room = 4
        elif get_room(rooms[-1][0]) == "Wakeport":
            room = 7
        elif get_room(rooms[-1][0]) == "Driftwood Shore":
            room = 11
        elif get_room(rooms[-1][0]) == "Mount Pajamaja":
            room = 9
        elif get_room(rooms[-1][0]) == "Pi'illo Castle":
            room = 1
        elif get_room(rooms[-1][0]) == "Dreamy Pi'illo Castle":
            room = 2
        elif get_room(rooms[-1][0]) == "Dreamy Dozing Sands":
            room = 6
        elif get_room(rooms[-1][0]) == "Dreamy Driftwood Shore":
            room = 12
        elif get_room(rooms[-1][0]) == "Dreamy Wakeport":
            room = 8
        elif get_room(rooms[-1][0]) == "Neo Bowser Castle":
            room = 15
        elif get_room(rooms[-1][0]) == "Somnom Woods":
            room = 13
        elif get_room(rooms[-1][0]) == "Dreamy Mount Pajamaja":
            room = 10
        elif get_room(rooms[-1][0]) == "Dreamy Somnom Woods":
            room = 14
        elif get_room(rooms[-1][0]) == "Dreamy Neo Bowser Castle":
            room = 16
        else:
            room = 17
        if len(areas[room]) > 1:
            spot = 1
            while areas[room][spot - 1][0] < areas[room][spot][0]:
                spot += 1
                if spot == len(areas[room]):
                    break
            areas[room].insert(spot, rooms)
        else:
            if len(areas[room]) == 0:
                areas[room].append(rooms)
            else:
                if areas[room][0][0] <= areas[room][-1][0]:
                    areas[room].append(rooms)
                else:
                    areas[room].insert(0, rooms)
        rooms = []
        for r in range(len(areas)):
            for p in range(len(areas[r])):
                for i in range(len(areas[r][p])):
                    temp.append(areas[r][p][i])
        new_item_locals = temp

        #Creates a spoiler log
        spoiler_log = open(input_folder + "/Spoiler Log.txt", "w")
        spoiler_log.write("Seed: " + hex(seed) + "\nReduced Mini Mario Requirements: ")
        if settings[1][0] == 1:
            spoiler_log.write("On\nReduced Ball Hop Skips: ")
        else:
            spoiler_log.write("Off\nReduced Ball Hop Skips: ")
        if settings[1][1] == 1:
            spoiler_log.write("On\nSecond Progressive Hammers: ")
        else:
            spoiler_log.write("Off\nSecond Progressive Hammers: ")
        if settings[3][0] == 1:
            spoiler_log.write("Mole Mario\n\n")
        else:
            spoiler_log.write("Mini Mario\n\n")
        room_check = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        hammer_num = 1
        spin_num = 1
        for s in range(len(new_item_locals)):
            if s > 0:
                #if new_item_locals[s][0] != new_item_locals[s-1][0] and new_item_locals[s][0] < len(item_local_names):
                #    print(hex(new_item_locals[s][0]) + " " + item_local_names[new_item_locals[s][0]])
                if get_room(new_item_locals[s][0]) != get_room(new_item_locals[s-1][0]):
                    spoiler_log.write("\n--" + get_room(new_item_locals[s][0]) + "--\n\n")
            else:
                spoiler_log.write("--Blimport--\n\n")
            check_type = ""
            if len(room_check) < new_item_locals[s][0] + 1:
                while len(room_check) < new_item_locals[s][0] + 1:
                    room_check.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            room_check[new_item_locals[s][0]][get_spot_type(new_item_locals[s])] += 1
            k = find_index_in_2d_list(repack_data, new_item_locals[s][7] + 0xD000)
            if k is None:
                item = item_names[new_item_locals[s][3] // 0x2000][int(new_item_locals[s][3] / 2) % 0x100]
                check_type = check_names[get_spot_type(new_item_locals[s])]
            else:
                check_type = check_names[repack_data[k[0]][0]]
                ab = find_index_in_2d_list(key_item_pool_checked, repack_data[k[0]][6])
                if ab is None:
                    if repack_data[k[0]][6] < 0xB037:
                        item = attack_piece_names[int((repack_data[k[0]][6] - 0xB030) / 2)]
                        offset = 0
                    elif repack_data[k[0]][6] < 0xB059:
                        item = attack_piece_names[int((repack_data[k[0]][6] - 0xB037) / 2) + 2]
                        offset = 1
                    else:
                        item = attack_piece_names[int((repack_data[k[0]][6] - 0xB059) / 2) + 13]
                        offset = 1
                    item += " Attack Piece " + str(int(math.log2(repack_data[k[0]][7]) + 1) + (((repack_data[k[0]][6] + offset) % 2) * 5))
                else:
                    item = key_item_names[key_item_pool_checked[ab[0]][1]]
            if new_item_locals[s][0] < len(item_local_names):
                room_name = item_local_names[new_item_locals[s][0]]
            else:
                room_name = hex(new_item_locals[s][0])
            spoiler_log.write(room_name + " " + check_type + " " + hex(new_item_locals[s][7]) + " - " + item + "\n")
            sbar.update(1)
        spoiler_log.write("\nKey Item Order:")
        for k in key_order:
            spoiler_log.write("\n" + key_item_names[k])

        #Creates Tracker.dat
        tracker_dat = open(input_folder + "/Tracker.dat", "wb")
        for l in range(len(new_item_locals)):
            tracker_dat.write(new_item_locals[l][-1].to_bytes(2, 'big'))
            if find_index_in_2d_list(repack_data, new_item_locals[l][-1] + 0xD000) is not None:
                k = find_index_in_2d_list(repack_data, new_item_locals[l][-1] + 0xD000)
                to_write = repack_data[k[0]][6]
                if repack_data[k[0]][6] // 0x1000 == 0xB and to_write != 0xB0F7:
                    to_write += int(math.log2(repack_data[k[0]][7]) + 1) * 0x100
                tracker_dat.write(to_write.to_bytes(2, 'big'))
            else:
                to_write = new_item_locals[l][3]
                if new_item_locals[l][2] // 0x10 % 0x10 > 1:
                    to_write += 0xA000
                tracker_dat.write(to_write.to_bytes(2, 'big'))
        #print(len(new_item_locals) - (len(new_item_locals)//16)*16)
        tracker_dat.write(b'\x00'*((len(new_item_locals) - (len(new_item_locals)//16)*16)*2))
        tracker_dat.write(b'\x00'*(16 * 20))
        tracker_dat.write(bytes(max_values))

    with tqdm(total=len(new_enemy_stats), desc="Repacking Enemy Stats...") as ebar:
        #Repackages randomized enemy stats
        enemy_stats = load_enemy_stats(code_bin=code_bin_path)
        for enemy in range(len(new_enemy_stats)):
            #print(new_enemy_stats[enemy])
            #print(new_enemy_stats[enemy][0])
            enemy_stats[new_enemy_stats[enemy][0]].hp = new_enemy_stats[enemy][1]
            enemy_stats[new_enemy_stats[enemy][0]].power = new_enemy_stats[enemy][2]
            enemy_stats[new_enemy_stats[enemy][0]].defense = new_enemy_stats[enemy][3]
            enemy_stats[new_enemy_stats[enemy][0]].speed = new_enemy_stats[enemy][4]
            enemy_stats[new_enemy_stats[enemy][0]].exp = new_enemy_stats[enemy][5]
            enemy_stats[new_enemy_stats[enemy][0]].coins = new_enemy_stats[enemy][6]
            if new_enemy_stats[enemy][9] > 1:
                enemy_stats[new_enemy_stats[enemy][0]].item_chance = new_enemy_stats[enemy][8]
                enemy_stats[new_enemy_stats[enemy][0]].item_type = new_enemy_stats[enemy][9]
                enemy_stats[new_enemy_stats[enemy][0]].rare_item_chance = new_enemy_stats[enemy][10]
                enemy_stats[new_enemy_stats[enemy][0]].rare_item_type = new_enemy_stats[enemy][11]
            enemy_stats[new_enemy_stats[enemy][0]].level = new_enemy_stats[enemy][12]
            if new_enemy_stats[enemy][0] == 113:
                enemy_stats[114].power = new_enemy_stats[enemy][2]
                enemy_stats[114].speed = new_enemy_stats[enemy][4]
                enemy_stats[114].level = new_enemy_stats[enemy][12]
            ebar.update(1)
            #print(new_enemy_stats[enemy])
        #Packs enemy stats
        save_enemy_stats(enemy_stats, code_bin=code_bin_path)

    with tqdm(total=len(new_item_locals)+len(parsed_fmapdat), desc="Repacking FMap...") as fbar:
        newlen = 0
        check_spot = []
        for b in range(len(new_item_locals)):
            if b > 0:
                if new_item_locals[b-1][0] != new_item_locals[b][0]:
                    parsed_fmapdat[new_item_locals[b][0]][7].clear()
            else:
                parsed_fmapdat[new_item_locals[b][0]][7].clear()
                    #if newlen > 0:
                    #    for j in range(newlen):
                    #        i = 0
                    #        while parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+10:i*12+12] != check_spot[j][0].to_bytes(2, 'little') and i < len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7])/12:
                    #            i += 1
                    #        #print(int.from_bytes(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+10:i*12+12], "little"))
                    #        #print(len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][0:i*12] + parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+12:len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7])])/12)
                    #        parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7] = parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][0:i*12] + parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+12:len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7])]
                    #    newlen = 0
                    #    check_spot = []
            #x = 0
            #while x < len(repack_data):
            #    if repack_data[x][5] == new_item_locals[b][-1] + 0xD000 and (repack_data[x][0] == 0 or repack_data[x][0] == 1):
            #        newlen += 1
            #        check_spot.append([new_item_locals[b][7], b])
            #        break
            #    x += 1

            #i = 0
            #while parsed_fmapdat[new_item_locals[b][0]][7][i*12+10:i*12+12] != new_item_locals[b][7].to_bytes(2, 'little'):
            #    i += 1
            availability = True
            x = 0
            while x < len(repack_data):
                if repack_data[x][5] == new_item_locals[b][-1] + 0xD000 and repack_data[x][0] != 5:
                    availability = False
                x += 1
            if availability:
                #print(hex(new_item_locals[b][7]))
                #Sets the last block of the room to True if it's the last block
                if b < len(new_item_locals) - 1:
                    if new_item_locals[b][0] != new_item_locals[b+1][0]:
                        new_item_locals[b][2] += 1
                    #print("Block type: " + hex(new_item_locals[b][2]) + " Block ID: " + hex(new_item_locals[b][7]))
                else:
                    new_item_locals[b][2] += 1
                try:
                    parsed_fmapdat[new_item_locals[b][0]][7].extend(struct.pack('<HHHHHH', *new_item_locals[b][2:8]))
                except struct.error:
                    print(hex(new_item_locals[b][2]))
            elif b < len(new_item_locals) - 1:
                #Fixes the last block in FMap if the actual last block is in FEvent
                if new_item_locals[b][0] != new_item_locals[b+1][0] and len(parsed_fmapdat[new_item_locals[b][0]][7]) > 1:
                    new_end = b
                    isnt_key = False
                    while not isnt_key:
                        isnt_key = True
                        new_end -= 1
                        c = 0
                        while c < len(repack_data):
                            if repack_data[c][5] == new_item_locals[new_end][-1] + 0xD000 and repack_data[c][0] != 5:
                                isnt_key = False
                                #print(repack_data[c][0])
                            c += 1
                    if new_item_locals[new_end][0] == new_item_locals[b][0]:
                        new_item_locals[new_end][2] += 1
                        parsed_fmapdat[new_item_locals[new_end][0]][7] = parsed_fmapdat[new_item_locals[new_end][0]][7][0:-12]
                        try:
                            parsed_fmapdat[new_item_locals[new_end][0]][7].extend(struct.pack('<HHHHHH', *new_item_locals[new_end][2:8]))
                        except struct.error:
                            print(hex(new_item_locals[new_end][2]))
                        #print(hex(new_item_locals[new_end][-1]))
                        #print(hex(new_item_locals[new_end][0]) + ": " + parsed_fmapdat[new_item_locals[new_end][0]][7].hex())
            fbar.update(1)

            #if new_item_locals[b][2] % 2 == 1:
            #    print(len(parsed_fmapdat[new_item_locals[b][0]][7]) % 12)

        with (
            code_bin_path.open('r+b') as code_bin,
            fs_std_romfs_path(FMAPDAT_PATH, data_dir=input_folder).open('wb') as fmapdat,
        ):
            version_pair = determine_version_from_code_bin(code_bin)
            fmapdat_offset_table = bytearray()
            for fmapdat_chunk_index, fmapdat_chunk in enumerate(parsed_fmapdat):
                fmapdat_chunk_offset = fmapdat.tell()
                if fmapdat_chunk_index < NUMBER_OF_ROOMS:
                    inside_chunk_offset = 13 * 4 * 2
                    for section_index, section in enumerate(fmapdat_chunk):
                        if section_index == 12:
                            # CGFX data needs to be aligned to 128 bytes
                            cgfx_padding = (-inside_chunk_offset) % 128
                            inside_chunk_offset += cgfx_padding
                        section_length = len(section)
                        fmapdat.write(struct.pack('<II', inside_chunk_offset, section_length))
                        inside_chunk_offset += section_length
                    for section_index, section in enumerate(fmapdat_chunk):
                        if section_index == 12:
                            # CGFX data needs to be aligned to 128 bytes
                            fmapdat.write(b'\x00' * cgfx_padding)
                        fmapdat.write(section)
                else:
                    # CGFX data needs to be aligned to 128 bytes
                    fmapdat_chunk_offset += fmapdat.write(b'\x00' * ((-fmapdat_chunk_offset) % 128))
                    inside_chunk_offset = fmapdat.write(fmapdat_chunk)
                # FMapDat chunks have to be aligned to 4 bytes
                inside_chunk_offset += fmapdat.write(b'\x00' * ((-inside_chunk_offset) % 4))
                fmapdat_offset_table.extend(struct.pack('<II', fmapdat_chunk_offset, inside_chunk_offset))
                fbar.update(1)
            code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16)
            code_bin.write(fmapdat_offset_table)
            code_bin.seek(FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16)
            code_bin.write(fmapdat_offset_table)

    randomize_repack.pack(input_folder, repack_data, settings, new_item_locals, new_item_logic, key_item_pool_checked)

#randomize_data(input_folder, stat_mult)
