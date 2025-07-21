import itertools
import math
import struct
import random
import os
from tqdm import tqdm
from mldtr import randomize_repack
from mnllib.n3ds import fs_std_code_bin_path, fs_std_romfs_path
from mnllib.dt import FMAPDAT_OFFSET_TABLE_LENGTH_ADDRESS, FMAPDAT_PATH, NUMBER_OF_ROOMS, \
    determine_version_from_code_bin, load_enemy_stats, save_enemy_stats, FEventScriptManager, \
    FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS, FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS

#input_folder = 'C:/Users/Dimit/AppData/Roaming/Azahar/load/mods/00040000000D5A00'
#stat_mult = [5, 5]

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

def get_spot_type(spot):
    if spot[2] == 0x0012 or spot[2] == 0x0013:
        return 5
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
        if key[logic[d+1]] < 1:
            available = False
        #If it's an or statement, it resets the generation for the next statement
        #while setting wasTrue depending on whether the chunk was true or not
        if logic[d+1] < 0:
            if not available:
                available = True
            else:
                was_true = True
    if was_true:
        available = True
    return available

def randomize_data(input_folder, stat_mult, settings, seed):
    with tqdm(total=2085, desc="Initializing...") as pbar:
        #Sets the seed to what it was in main
        random.seed = seed
        pbar.update(1)

        # Opens code.bin for enemy stat randomization
        code_bin_path = fs_std_code_bin_path(data_dir=input_folder)
        enemy_stats = load_enemy_stats(code_bin=code_bin_path)
        enemy_stats_rand = []
        dream_enemy_stats_rand = []
        boss_stats_rand = []
        dream_boss_stats_rand = []
        filler_stats_rand = []
        for enemy in range(len(enemy_stats)):
            pbar.update(1)
            if stat_mult[0] > -1:
                enemy_stats[enemy].power *= stat_mult[0]
                if enemy_stats[enemy].power > 0xFFFF:
                    enemy_stats[enemy].power = 0xFFFF
            else:
                enemy_stats[enemy].power = 0xFFFF
            if enemy == 87:
                enemy_stats[enemy].exp *= 4
            if stat_mult[1] > 0:
                enemy_stats[enemy].exp *= stat_mult[1]
                if enemy_stats[enemy].exp > 0xFFFF:
                    enemy_stats[enemy].exp = 0xFFFF
            if enemy == 17:
                enemy_stats[enemy].hp *= 4
                enemy_stats[enemy].power *= 4
                enemy_stats[enemy].defense *= 4
                enemy_stats[enemy].speed *= 4
                enemy_stats[enemy].exp *= 4
            elif enemy == 107:
                enemy_stats[enemy].hp *= 2
                enemy_stats[enemy].power *= 2
                enemy_stats[enemy].defense *= 2
                enemy_stats[enemy].speed *= 2
                enemy_stats[enemy].exp *= 2
            if (enemy > 12 and not(14 <= enemy <= 16) and enemy != 20 and
                    enemy != 22 and enemy != 24 and enemy != 26 and
                    enemy != 28 and enemy != 32 and enemy != 34 and
                    enemy != 40 and enemy != 43 and enemy != 44 and
                    enemy != 48 and enemy != 51 and not(53 <= enemy <= 56) and
                    enemy != 63 and enemy != 83 and enemy != 88 and enemy != 89 and enemy != 97 and
                    enemy != 103 and enemy != 105 and enemy != 108 and enemy != 114 and
                    enemy != 132 and not(134 <= enemy <= 136) and enemy < 139):
                #Appends data to enemy array if it's an enemy
                if (enemy == 13 or enemy == 18 or enemy == 25 or
                        enemy == 27 or enemy == 29 or enemy == 38 or
                        enemy == 39 or enemy == 41 or (58 <= enemy <= 61) or
                        (68 <= enemy <= 71) or (85 <= enemy <= 94) or
                        (100 <= enemy <= 102) or enemy == 104 or enemy == 106 or
                        enemy == 113 or (115 <= enemy <= 120)):
                    enemy_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                             enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                             enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
                #Appends data to boss array if it's a boss
                elif (enemy == 17 or enemy == 30 or enemy == 42 or
                      enemy == 62 or enemy == 95 or enemy == 96 or
                      enemy == 107 or enemy == 108):
                    boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                             enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                             enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
                #Appends data to dream enemy array if it's a dream enemy
                elif (enemy == 19 or enemy == 21 or enemy == 31 or
                      enemy == 33 or enemy == 35 or enemy == 45 or
                      enemy == 46 or enemy == 47 or enemy == 49 or
                      enemy == 50 or (64 <= enemy <= 67) or (72 <= enemy <= 78) or
                      enemy == 84 or enemy == 98 or enemy == 99 or
                      (110 <= enemy <= 112) or (121 <= enemy <= 125) or enemy == 133):
                    dream_enemy_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                             enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                             enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
                #Appends data to dream boss array if it's a dream boss
                elif (enemy == 23 or enemy == 36 or enemy == 52 or
                      (79 <= enemy <= 81) or (126 <= enemy <= 131) or enemy == 137):
                    dream_boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                             enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                             enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
                #Appends data to filler array if it's a "filler" enemy (one used in bosses that only exists for spectacle)
                else:
                    filler_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                             enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                             enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])

        #Logic for real world enemies
        enemy_logic = [[13], [18, 15, 5, -1, 15, 6], [25, 15, 0], [27, 15, 0], [29, 15, 0],
                           [38, 15, 16], [39, 15, 16], [41, 15, 16, 5, -1, 15, 16, 17, 2],
                           [58, 1], [59, 1], [60, 23, 1, -1, 1, 5], [61, 23, 1, 4, 6, -1, 1, 5],
                           [68, 15, 16, 1, -1, 15, 16, 5], [69, 15, 16, 1, -1, 15, 16, 5], [70, 15, 16, 1, -1, 15, 16, 5],
                           [71, 15, 16, 1, -1, 15, 16, 5], [85, 15, -1, 1, 4, 5], [86, 15, -1, 1, 4, 5], [87, 15, -1, 1, 4, 5],
                           [90, 1, 4, 5], [91, 15, 16, 2, 4], [92, 15], [93, 15],
                           [94, 15, 16, 5], [100, 15, 1, 3, 5], [101, 15, 1, 5], [102, 15, 1, 5], [104, 15, 1, 5],
                           [106, 15, 1, 5], [113, 15, 27, 1, 5], [115, 15, 27, 1, 5],
                           [116, 15, 27, 1, 5], [117, 15, 27, 1, 4, 5], [118, 15, 27, 1, 4, 5], [119, 15, 27, 1, 4, 5], [120, 15, 27, 1, 4, 5],]

        #Logic for dream world enemies
        if settings[1][0] == 0 and settings[1][1] == 0:
            dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6, -1, 15, 16, 5, 6],
                                 [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 1, 6, -1, 1, 5, 6], [65, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10],
                                 [66, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10], [67, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10],
                                 [72, 15, 16, 1, 6, -1, 15, 16, 5, 6], [73, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                                 [74, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6], [75, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6],
                                 [76, 15, 16, 24, 25, 1, 6, -1, 15, 16, 24, 25, 5, 6], [77, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                                 [78, 15, 16, 1, 6, -1, 15, 16, 5, 6], [84, 6], [98, 22, 1, 2, 4, 5, 6], [99, 22, 1, 2, 4, 5, 6],
                                 [110, 15, 1, 3, 5, 6], [111, 15, 1, 3, 5, 6], [112, 15, 1, 2, 3, 5, 6],  [121, 15, 27, 1, 5, 6],
                                 [122, 15, 27, 1, 4, 5, 6], [123, 15, 27, 1, 4, 5, 6], [124, 15, 27, 1, 5, 6], [125, 15, 27, 1, 5, 6], [133, 15, 27, 1, 4, 5, 6],]
        elif settings[1][0] == 1 and settings[1][1] == 1:
            dream_enemy_logic = [[19], [21, 15, 6], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6],
                                 [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 3, 6, -1, 23, 5, 6], [65, 23, 4, 6, 10],
                                 [66, 23, 4, 6, 10], [67, 23, 4, 6, 10],
                                 [72, 15, 16, 6], [73, 15, 16, 6],
                                 [74, 15, 16, 24, 6], [75, 15, 16, 24, 6],
                                 [76, 15, 16, 24, 25, 6], [77, 15, 16, 6],
                                 [78, 15, 16, 6], [84, 6], [98, 22, 2, 4, 5, 6], [99, 22, 2, 4, 5, 6],
                                 [110, 15, 3, 5, 6], [111, 15, 3, 5, 6], [112, 15, 2, 3, 5, 6],  [121, 15, 27, 5, 6],
                                 [122, 15, 27, 4, 5, 6], [123, 15, 27, 4, 5, 6], [124, 15, 27, 5, 6], [125, 15, 27, 5, 6], [133, 15, 27, 4, 5, 6],]
        elif settings[1][0] == 1:
            dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6, -1, 15, 16, 5, 6],
                                 [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 6, -1, 5, 6], [65, 23, 4, 6, 10, -1, 3, 5, 6, 10],
                                 [66, 23, 4, 6, 10, -1, 3, 5, 6, 10], [67, 23, 4, 6, 10, -1, 3, 5, 6, 10],
                                 [72, 15, 16, 6], [73, 15, 16, 6],
                                 [74, 15, 16, 24, 6], [75, 15, 16, 24, 6],
                                 [76, 15, 16, 24, 25, 6], [77, 15, 16, 6],
                                 [78, 15, 16, 6], [84, 6], [98, 22, 2, 4, 5, 6], [99, 22, 2, 4, 5, 6],
                                 [110, 15, 3, 5, 6], [111, 15, 3, 5, 6], [112, 15, 2, 3, 5, 6],  [121, 15, 27, 5, 6],
                                 [122, 15, 27, 4, 5, 6], [123, 15, 27, 4, 5, 6], [124, 15, 27, 5, 6], [125, 15, 27, 5, 6], [133, 15, 27, 4, 5, 6],]
        else:
            dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6, -1, 15, 16, 5, 6],
                                 [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 1, 6], [65, 23, 1, 4, 6, 10],
                                 [66, 23, 1, 4, 6, 10], [67, 23, 1, 4, 6, 10],
                                 [72, 15, 16, 1, 6, -1, 15, 16, 5, 6], [73, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                                 [74, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6], [75, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6],
                                 [76, 15, 16, 24, 25, 1, 6, -1, 15, 16, 24, 25, 5, 6], [77, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                                 [78, 15, 16, 1, 6, -1, 15, 16, 5, 6], [84, 6], [98, 22, 1, 2, 4, 5, 6], [99, 22, 1, 2, 4, 5, 6],
                                 [110, 15, 1, 3, 5, 6], [111, 15, 1, 3, 5, 6], [112, 15, 1, 2, 3, 5, 6],  [121, 15, 27, 1, 5, 6],
                                 [122, 15, 27, 1, 4, 5, 6], [123, 15, 27, 1, 4, 5, 6], [124, 15, 27, 1, 5, 6], [125, 15, 27, 1, 5, 6], [133, 15, 27, 1, 4, 5, 6],]

        #Logic for bosses
        boss_logic = [[17, 14], [30, 15], [42, 15, 16, 17, 18, 19, 20, 21], [62, 23, 1, 4, 6, 8, 10, -1, 1, 5],
                      [95, 15, 16, 22, 1, 2, 4, 5, 6], [96, 15, 16, 22, 1, 2, 4, 5, 6], [107, 15, 1, 2, 4, 5, 6],]

        #Logic for dream world bosses
        dream_boss_logic = [[23], [36, 15, 6], [52, 15, 22, 6], [79, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                            [80, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6], [81, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                            [126, 15, 27, 1, 5, 6], [127, 15, 27, 1, 4, 5, 6], [128, 15, 27, 1, 4, 5, 6], [129, 15, 27, 1, 4, 5, 6], [130, 15, 27, 1, 4, 5, 6],
                            [131, 15, 27, 1, 4, 5, 6], [137, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],]

        #Logic for "filler" enemies
        filler_logic = [[37, 15, 6], [57, 15, 22, 6], [82, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                        [109, 15, 1, 2, 3, 5, 6], [138, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],]
        pbar.update(6)

        #Replaces logic where needed
        if settings[1][0] == 1 or settings[1][1] == 1:
            if settings[1][0] == 1 and settings[1][1] == 1:
                replace_enemy = [[41, 15, 16, 17, 2], [58, 23], [59, 23], [60, 23, 4, 6], [68, 15, 16], [69, 15, 16], [70, 15, 16], [71, 15, 16],
                                 [85, 15, -1, 23, 4, 5], [86, 15, -1, 23, 4, 5], [87, 15, -1, 23, 4, 5], [90, 23, 4, 5], [94, 15, 16, 17, 18, 19, 20, 21, 5],
                                 [100, 15, 3, 5], [101, 15, 5], [102, 15, 5], [104, 15, 5], [106, 15, 5], [113, 15, 27, 5], [115, 15, 27, 5], [116, 15, 27, 5],
                                 [117, 15, 27, 4, 5], [118, 15, 27, 4, 5], [119, 15, 27, 4, 5], [120, 15, 27, 4, 5]]

                replace_boss = [[62, 23, 4, 6, 8, 10], [95, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6, 8, 10], [96, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6, 8, 10]]

                replace_dream_boss = []
            elif settings[1][0] == 1:
                replace_enemy = [[41, 15, 16, 5, -1, 15, 16, 17, 2], [58], [59, 23, -1, 5], [60, 23, 4, 6, -1, 5], [68, 15, 16], [69, 15, 16],
                                 [70, 15, 16], [71, 15, 16], [85, 15, -1, 4, 5], [86, 15, -1, 4, 5], [87, 15, -1, 4, 5], [90, 4, 5],
                                 [101, 15, 5], [102, 15, 5], [104, 15, 5], [106, 15, 5], [113, 15, 27, 5], [115, 15, 27, 5], [116, 15, 27, 5],
                                 [117, 15, 27, 4, 5], [118, 15, 27, 4, 5], [119, 15, 27, 4, 5], [120, 15, 27, 4, 5]]

                replace_boss = [[62, 23, 4, 6, 8, 10, -1, 5]]

                replace_dream_boss = []
            else:
                replace_enemy = [[41, 15, 16, 17, 2], [58, 1], [59, 23, 1], [60, 23, 1, 4, 6], [85, 15, -1, 23, 1, 4, 5], [86, 15, -1, 23, 1, 4, 5],
                                 [87, 15, -1, 23, 1, 4, 5], [90, 23, 1, 4, 5], [94, 15, 16, 17, 18, 19, 20, 21, 5],]

                replace_boss = [[62, 23, 1, 4, 6, 8, 10], [95, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6, 8, 10], [96, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6, 8, 10]]

                replace_dream_boss = []
            for e in replace_enemy:
                el = 0
                while enemy_logic[el][0] != e[0]:
                    el += 1
                enemy_logic[el] = e
            for b in replace_boss:
                bl = 0
                while boss_logic[bl][0] != b[0]:
                    bl += 1
                boss_logic[bl] = b
        #Loads in FMap as a 3D array
        parsed_fmapdat = []
        with (
            code_bin_path.open('rb') as code_bin,
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

        #Initializes the item pool
        item_pool = []

        # Creates an item_data array with all the blocks and bean spots
        item_locals = []
        with (
            code_bin_path.open('rb+') as code_bin,
            fs_std_romfs_path(FMAPDAT_PATH, data_dir=input_folder).open('rb+') as fmapdat,
        ):
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
                #with open("Dozing Edit.bin", 'rb') as new_model:
                #    fmapdat.seek(0)
                #    temp = bytearray(fmapdat.read())
                #    test = bytearray(new_model.read())
                #    temp[0x281C898:0x281C898+0x72A7B] = (test[:0x72A7B])
                #    temp[0x281C898+0x72A7B:0x281C898+0x72A7B] = test[0x72A7C:]
                #    fmapdat.seek(0)
                #    fmapdat.write(temp)
                #    fix_offsets(fmapdat, code_bin, 0x5D, len(test), 12)
                #del temp
                #del test
                fmapdat.seek(0)
            version_pair = determine_version_from_code_bin(code_bin)
            block_id = 2500
            rooms_to_init = [0x001, 0x004, 0x005, 0x010, 0x011, 0x012, 0x013, 0x014, 0x017, 0x019, 0x01F, 0x020, 0x021, 0x022, 0x027, 0x028, 0x02A,
                             0x034, 0x035, 0x036, 0x038, 0x039, 0x03A, 0x03B, 0x03D, 0x040, 0x04B, 0x04C, 0x04D, 0x04F, 0x062, 0x069, 0x06A, 0x06C,
                             0x06D, 0x06F, 0x070, 0x072, 0x075, 0x076, 0x079, 0x07C, 0x0BB, 0x0BD, 0x0BE, 0x0C4, 0x0C5, 0x0C6, 0x0D2, 0x0D6, 0x0E4,
                             0x0F5, 0x0F6, 0x0FA, 0x10C, 0x124, 0x125, 0x126, 0x127, 0x128, 0x129, 0x12A, 0x13D, 0x144, 0x145, 0x146, 0x147, 0x148,
                             0x14B, 0x14C, 0x14E, 0x14F, 0x161, 0x164, 0x165, 0x167, 0x168, 0x16C, 0x177, 0x17A, 0x17D, 0x187, 0x188, 0x189, 0x18A,
                             0x18B, 0x18F, 0x190, 0x192, 0x194, 0x1E7, 0x1F0, 0x1F1, 0x1F2, 0x1F4, 0x1F6, 0x1F7, 0x1F8, 0x1F9, 0x1FA, 0x204, 0x22A,
                             0x22B, 0x22C, 0x22D, 0x22E, 0x22F, 0x231, 0x232, 0x233, 0x295,]
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
                                     int(((script.header.triggers[trigger][0] // 0x10000) + (script.header.triggers[trigger][1] // 0x10000)) / 2), block_id]
                        block_id += 1
                        temp.append(new_block)
                    for a in range(len(script.header.actors)):
                        if (script.header.actors[a][5] // 0x1000) % 0x1000 == 0x748 and script.header.actors[a][5] % 0x100 == 0x43:
                            new_block = [0x10, 0x0, script.header.actors[a][0] % 0x10000, script.header.actors[a][0] // 0x10000,
                                         script.header.actors[a][1] % 0x10000, block_id]
                            block_id += 1
                            temp.append(new_block)
                    for b in range(len(temp)):
                        for d in range(len(temp[b])):
                            parsed_fmapdat[room][7][b*12+d*2:b*12+d*2] = bytearray(struct.pack('<H', temp[b][d]))
                except ValueError:
                    pass
                for treasure_index in range(math.floor(len(parsed_fmapdat[room][7])/12)):
                    treasure_type, item_id, x, y, z, treasure_id = struct.unpack('<HHHHHH', parsed_fmapdat[room][7][treasure_index*12:treasure_index*12+12])
                    if (room != 0x00D and room != 0x015 and room != 0x016 and room != 0x01D and room != 0x037 and room != 0x04E and room != 0x052 and
                            room != 0x054 and room != 0x1D2 and room != 0x2A8 and room != 0x2A9 and treasure_type % 0x100 != 0x16 and
                            treasure_type % 0x100 != 0x17):
                        pbar.update(1)
                        item_locals.append([room, treasure_index * 12, treasure_type, x, y, z, treasure_id])
                        item_pool.append([treasure_type, item_id])

        #for item in item_locals:
        #   print(str(item) + "\n")

        item_logic_chunk = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        #Logic for every single block and bean spot (The numbers after the ID point to their spots in the ability info)
        item_logic_chunk[0] = [[52, 15, 5], [53, 15, 5], [2500, 15], [54, 15], [55, 15, 0, -1, 15, 5], [56, 15, 0], [57, 15, 0], [58, 15], [59, 15, 2], [60, 15, 2],
                      [61, 15, 0, 2], [2388, 15, 2], [62, 15, 0], [63, 15, 0], [64, 15, 0], [65, 15, 0], [2501, 15, 0], [2502, 15, 0], [2503, 15, 0], [2504, 15, 0],
                      [66, 15, 0], [67, 15, 2, 3, -1, 15, 2, 5], [2505, 15, 0], [2506, 15, 0], [2507, 15, 0], [2508, 15, 0], [68, 15, 0], [69, 15, 0], [70, 15, 0],
                      [71, 15, 0], [72, 15], [73, 15], [74, 15, 16, 1], [75, 15, 16, 2], [76, 15, 2], [77, 15, 2],
                      [78, 15, 0], [79, 15], [80, 15], [81, 15], [82, 15, 2], [83, 15, 2], [84, 15, 2], [85, 15, 2, 3, 0, 15, 2, 5], [86, 15, 4],
                      [87, 15], [88, 15], [89, 15, 4], [90, 15, 2], [91, 15, 0], [92, 15, 1, 5], [2389, 15, 0, 4, 5], [94, 15, 0, 4, 5],
                      [95, 15, 0, 4, 5], [96, 15, 0, 4, 5], [97, 15, 0, 4, 5], [98, 15, 0, 4, 5], [99, 15, 0, 2, 4, 5], [100, 15, 0, 2, 4, 5],
                      [101, 15, 0, 2, 4, 5], [102, 15, 0, 2, 4, 5], [103, 15], [104, 15], [107, 15], [2390, 15, 0], [2391, 15, 0],
                      [108, 15, 0, 2], [109, 15, 0, 2], [110, 15, 0, 2], [111, 15, 0, 2], [112, 15, 0], [113, 15, 0], [114, 15, 0]]
        if settings[1][1] != 1:
            item_logic_chunk[1] = [[253, 15, 16, 2], [2509, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2510, 15, 16, 1, 5], [271, 15, 16, 17, 2, -1, 15, 16, 2, 5], [272, 15, 16, 17, 2, -1, 15, 16, 2, 5], [273, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [274, 15, 16, 17, 2, -1, 15, 16, 2, 5], [275, 15, 16, 17, 2, -1, 15, 16, 2, 5], [2511, 15, 16, 17, 1, -1, 15, 16, 1, 5], [276, 15, 16, 17, 2, -1, 15, 16, 2, 5], [969, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [277, 15, 16, 17, -1, 15, 16, 5], [278, 15, 16, 17, -1, 15, 16, 5], [2512, 15, 16], [2513, 15, 16, 2], [2514, 15, 16, 2], [2515, 15, 16, 2], [279, 15, 16, 2], [281, 15, 16, 2],
                      [282, 15, 16, 1], [283, 15, 16, 17, -1, 15, 16, 5], [284, 15, 16, 2], [2516, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2517, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [285, 15, 16, 17, 2, -1, 15, 16, 2, 5], [286, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [287, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [288, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [289, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [290, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [291, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2518, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2519, 15, 16, 17, 1, -1, 15, 16, 1, 5], [292, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [293, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [294, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [295, 15, 16, 17, 2, -1, 15, 16, 2, 5], [296, 15, 16, 17, 2, -1, 15, 16, 2, 5], [2373, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [2520, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2521, 15, 16, 17, 1, -1, 15, 16, 1, 5], [303, 15, 16, 17, 1, -1, 15, 16, 1, 5], [304, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [305, 15, 16, 17, 1, -1, 15, 16, 1, 5], [306, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [115, 15, 0], [116, 15, 0, 5], [2522, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2523, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [2524, 15, 16, 17, 1, -1, 15, 16, 1, 5], [307, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [308, 15, 16, 1, 5, -1, 15, 16, 2, 5], [309, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [310, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [311, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                      [312, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2374, 15, 16, 1, 5, -1, 15, 16, 2, 5],
                      [313, 15, 16, 3, 5], [314, 15, 16, 3, 5], [15], [16, 2]]
        else:
            item_logic_chunk[1] = [[253, 15, 16, 2], [2509, 15, 16, 17, 1], [2510, 15, 16, 17, 1, 5], [271, 15, 16, 17, 2], [272, 15, 16, 17, 2], [273, 15, 16, 17, 2],
                          [274, 15, 16, 17, 2], [275, 15, 16, 17, 2], [2511, 15, 16, 17, 1], [276, 15, 16, 17, 2], [969, 15, 16, 17, 2],
                          [277, 15, 16, 17], [278, 15, 16, 17], [2512, 15, 16], [2513, 15, 16, 2], [2514, 15, 16, 2], [2515, 15, 16, 2],
                          [279, 15, 16, 2], [281, 15, 16, 2], [282, 15, 16, 1], [283, 15, 16, 17], [284, 15, 16, 2], [2516, 15, 16, 17, 1], [2517, 15, 16, 17, 1],
                          [285, 15, 16, 17, 2], [286, 15, 16, 17, 2], [287, 15, 16, 17, 1], [288, 15, 16, 17, 1],
                          [289, 15, 16, 17, 1], [290, 15, 16, 17, 1], [291, 15, 16, 17, 1], [2518, 15, 16, 17, 1], [2519, 15, 16, 17, 1], [292, 15, 16, 17, 2],
                          [293, 15, 16, 17, 1], [294, 15, 16, 17, 2], [295, 15, 16, 17, 2], [296, 15, 16, 17, 2], [2373, 15, 16, 17, 1], [2520, 15, 16, 17, 1], [2521, 15, 16, 17, 1],
                          [303, 15, 16, 17, 1], [304, 15, 16, 17, 1], [305, 15, 16, 17, 1], [306, 15, 16, 17, 1],
                          [115, 15, 0], [116, 15, 0, 5], [2522, 15, 16, 17, 1], [2523, 15, 16, 17, 1], [2524, 15, 16, 17, 1], [307, 15, 16, 17, 2],
                          [308, 15, 16, 17, 1, 5, -1, 15, 16, 17, 2, 5], [309, 15, 16, 17, 2],
                          [310, 15, 16, 17, 2, -1, 15, 16, 17, 1], [311, 15, 16, 17, 2, -1, 15, 16, 17, 1],
                          [312, 15, 16, 17, 1], [2374, 15, 16, 17, 1, 5, -1, 15, 16, 17, 2, 5], [313, 15, 16, 17, 3, 5], [314, 15, 16, 17, 3, 5], [15], [16, 2]]

        item_logic_chunk[2] = [[2525, 15, 6], [2526, 15, 6], [119, 15, 6], [121, 15, 6], [123, 15, 6], [125, 15, 6], [2527, 15, 6], [127, 15, 6], [129, 15, 6], [2528, 15, 6], [131, 15, 6], [132, 15, 6], [2392, 15, 6],
                      [141, 15, 6], [142, 15, 6], [2529, 15, 6], [2530, 15, 6], [2531, 15, 6], [2393, 15, 6], [144, 15, 6], [145, 15, 6], [2532, 15, 6], [146, 15, 6], [147, 15, 6], [152, 15, 6], [2394, 15, 6], [2395, 15, 6], [151, 15, 6]]

        if settings[1][0] != 1:
            item_logic_chunk[3] = [[1511, 15, 3], [1512, 15, 2, 3], [1513, 15, 2, 3], [2532, 15, 22], [1514, 15, 22], [1515, 15, 22, 2], [2533, 15, 22], [2534, 15, 22],
                      [1516, 15, 22, 2, 5], [1517, 15, 22, 2], [1518, 15, 22, 2], [1519, 15, 22], [2536, 15, 22, 1], [2535, 15, 22, 1], [1520, 15, 22, 2], [1521, 15, 22, 2], [1522, 15, 22, 1], [1523, 15, 22],
                      [1524, 15, 22, 1], [1525, 15, 22, 2], [2538, 15, 16], [1549, 15, 16, 1], [1550, 15, 16, 1], [1551, 15, 16, 1], [1552, 15, 16, 2], [2537, 15, 22], [1527, 15, 22],
                      [1528, 15, 22], [1529, 15, 22], [1530, 15, 22], [1531, 15, 22], [1532, 15, 22], [2540, 15, 16, 1], [2541, 15, 16, 1, 4], [2542, 15, 16, 1, 3, -1, 15, 16, 1, 5], [1553, 15, 16, 1], [1554, 15, 16, 1, 3],
                      [2331, 15, 16, 1, 3], [2332, 15, 16, 1, 3], [2543, 15, 16, 1, 3], [1562, 15, 16, 1, 3], [1539, 15, 22, 3], [2538, 15, 22], [1540, 15, 22],
                      [1541, 15, 22], [1542, 15, 22], [2539, 15, 22], [2540, 15, 22], [1566, 15, 16, 1, 3,], [1567, 15, 16, 1, 3], [1568, 15, 16, 1, 3],
                      [1569, 15, 16, 1, 3], [1570, 15, 16, 1, 3, 5], [1571, 15, 16, 1, 2, 3],
                      [1572, 15, 16, 1, 2, 3], [1543, 15, 16, 1], [1544, 15, 16, 1], [1545, 15, 16, 1], [2398, 15, 16, 1], [2547, 15, 16, 1, 4, -1, 15, 16, 1, 5], [2399, 15, 16],
                      [1547, 15, 16], [1548, 15, 16, 2], [2548, 15, 16, 1, 4], [1555, 15, 16, 1, 4], [1556, 15, 16, 1, 4], [1557, 15, 16, 1, 2, 4],
                      [2400, 15, 16, 1, 2, 4], [1558, 15, 16, 1, 3], [2549, 15, 16, 1], [2550, 15, 16, 1], [2551, 15, 16, 1, 4], [1559, 15, 16, 1, 3], [1560, 15, 16, 1, 2, 3],
                      [1561, 15, 16, 1, 2, 3], [2401, 15, 16, 1, 2, 3], [2552, 15, 16, 1, 4], [1563, 15, 16, 1, 4, -1, 15, 16, 3, 5],
                      [1564, 15, 16, 1, 4, -1, 15, 16, 3, 5,], [1565, 15, 16, 1, 2, 4, -1, 15, 16, 2, 4, 5],
                      [988, 15, 16, 1, 2, 4, -1, 15, 16, 2, 3, 5]]
        else:
            item_logic_chunk[3] = [[1511, 15, 3], [1512, 15, 2, 3], [1513, 15, 2, 3], [2532, 15, 22], [1514, 15, 22], [1515, 15, 22, 2],
                          [2533, 15, 22], [2534, 15, 22], [1516, 15, 22, 2, 5],
                          [1517, 15, 22, 2], [1518, 15, 22, 2], [1519, 15, 22], [2535, 15, 22, 1], [2536, 15, 22, 1], [1520, 15, 22, 2], [1521, 15, 22, 2],
                          [1522, 15, 22, 1], [1523, 15, 22],
                          [1524, 15, 22, 1], [1525, 15, 22, 2], [2538, 15, 16], [1549, 15, 16, 1], [1550, 15, 16], [1551, 15, 16],
                          [1552, 15, 16, 2], [2537, 15, 22], [1527, 15, 22],
                          [1528, 15, 22], [1529, 15, 22], [1530, 15, 22], [1531, 15, 22], [1532, 15, 22], [2540, 15, 16], [2541, 15, 16, 4], [2542, 15, 16, 3, -1, 15, 16, 5], [1553, 15, 16],
                          [1554, 15, 16, 3],
                          [2331, 15, 16, 3], [2332, 15, 16, 3], [2543, 15, 16, 3], [1562, 15, 16, 3], [1539, 15, 22, 3], [2538, 15, 22], [1540, 15, 22],
                          [1541, 15, 22], [1542, 15, 22], [2539, 15, 22], [2540, 15, 22], [1566, 15, 16, 3, ], [1567, 15, 16, 3], [1568, 15, 16, 3],
                          [1569, 15, 16, 3], [1570, 15, 16, 3, 5], [1571, 15, 16, 2, 3],
                          [1572, 15, 16, 2, 3], [1543, 15, 16, 1], [1544, 15, 16, 1], [1545, 15, 16, 1], [2398, 15, 16, 1],
                          [2547, 15, 16, 4, -1, 15, 16, 5], [2399, 15, 16],
                          [1547, 15, 16], [1548, 15, 16, 2], [2548, 15, 16, 4], [1555, 15, 16, 4], [1556, 15, 16, 4], [1557, 15, 16, 2, 4],
                          [2400, 15, 16, 2, 4], [1558, 15, 16, 3], [2549, 15, 16], [2550, 15, 16], [2551, 15, 16, 4], [1559, 15, 16, 3], [1560, 15, 16, 2, 3],
                          [1561, 15, 16, 2, 3], [2401, 15, 16, 2, 3], [2552, 15, 16, 1, 4], [1563, 15, 16, 4, -1, 15, 16, 3, 5],
                          [1564, 15, 16, 4, -1, 15, 16, 3, 5, ], [1565, 15, 16, 2, 4, -1, 15, 16, 2, 4, 5],
                          [988, 15, 16, 2, 4, -1, 15, 16, 2, 3, 5]]

        item_logic_chunk[4] = [[7], [8], [9], [10], [11], [12], [13], [14], [17], [18, 2], [19], [20, 2], [21, 2], [22, 2], [23, 2]]

        if settings[1][1] != 1:
            item_logic_chunk[5] = [[254, 15, 16, 2], [255, 15, 16, 17, 18, 19, 20, 21, 1, 2, -1, 15, 16, 5], [256, 15, 16], [257, 15, 16], [258, 15, 16],
                      [259, 15, 16, 17, 2, -1, 15, 16, 2, 5], [260, 15, 16, 17, -1, 15, 16, 5], [261, 15, 16, 5], [262, 15, 16, 5],
                      [263, 15, 16, 2, 5], [264, 15, 16, 2, 5], [2541, 15, 16], [268, 15, 16, 2], [269, 15, 16], [270, 15, 16],]
        else:
            item_logic_chunk[5] = [[254, 15, 16, 2], [255, 15, 16, 17, 18, 19, 20, 21, 1], [256, 15, 16], [257, 15, 16], [258, 15, 16],
                          [259, 15, 16, 17, 2], [260, 15, 16, 17], [261, 15, 16, 5], [262, 15, 16, 5],
                          [263, 15, 16, 2, 5], [264, 15, 16, 2, 5], [2541, 15, 16], [268, 15, 16, 2], [269, 15, 16], [270, 15, 16],]

        if settings[1][0] != 1 and settings[1][1] != 1:
            item_logic_chunk[6] = [[1573, 1], [1574, 1], [1575, 1], [1576, 23, 1, -1, 1, 5], [1577, 23, 1, -1, 1, 5], [2554, 23, 1, 3, -1, 1, 3, 5], [1578, 23, 1, 3, -1, 1, 5], [1579, 23, 1, 2, 3, -1, 1, 2, 3, 5],
                          [1580, 23, 1, 2, 3, -1, 1, 2, 3, 5], [2555, 23, 1, -1, 1, 5], [1581, 23, 1, -1, 1, 5], [1582, 23, 1, -1, 1, 5], [1583, 23, 1, 2, 4, -1, 1, 2, 4, 5], [2402, 23, 1, 2, 4, -1, 1, 2, 4, 5],
                          [2542, 23, 1, -1, 1, 5], [2543, 23, 1, 3, -1, 1, 3, 5], [1584, 23, 1, -1, 1, 5], [1585, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1586, 23, 1, 3, -1, 1, 5], [2558, 23, 1, -1, 1, 5], [1587, 23, 1, 3, -1, 1, 3, 5], [1588, 23, 1, -1, 1, 5],
                          [1589, 23, 1, -1, 1, 5], [1590, 23, 1, -1, 1, 5], [1591, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1592, 23, 1, 3, -1, 1, 3, 5], [2403, 23, 1, 3, -1, 1, 5], [2559, 23, 1, 3, -1, 1, 3, 5],
                          [1593, 23, 1, 2, 3, -1, 1, 2, 3, 5], [2560, 23, 1, 3, -1, 1, 3, 5], [1594, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1595, 23, 1, 3, 6, -1, 1, 3, 5, 6], [1596, 23, 1, 3, -1, 1, 3, 5],
                          [1597, 23, 1, 3, -1, 1, 3, 5], [2561, 23, 1, 3, -1, 1, 3, 5], [2562, 23, 1, 3, -1, 1, 3, 5], [1598, 1, 3, 5], [1599, 1, 3, 5], [2333, 23, 1, 3, -1, 1, 3, 5], [1546, 23, 1, 3, -1, 1, 3, 5], [2219, 23, 1, 3, -1, 1, 3, 5],
                          [1600, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1601, 23, 1, 2, 3, -1, 1, 2, 3, 5], [2334, 23, 1, 2, 3, -1, 1, 2, 3, 5], [2563, 23, 1, 3, 6, 8, -1, 1, 3, 5, 6, 8], [1602, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [2564, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5],
                          [1603, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1604, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5, 6], [1605, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1606, 23, 1, 4, 6, 8, 10, -1, 1, 5],
                          [1607, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 5], [1608, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [2565, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1609, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1610, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5],
                          [2359, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2360, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2375, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1611, 1, 4, 5],
                          [1612, 1, 4, 5], [1613, 1, 2, 4, 5], [1614, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1615, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [2566, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1616, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5],
                          [1617, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1618, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2361, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2362, 1, 3, 5],
                          [1619, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 3, 5], [1620, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 3, 5], [1621, 1, 3, 5], [2296, 1, 2, 3, 5], [1623, 1, 3, 5],]
        elif settings[1][0] == 1 and settings[1][1] == 1:
            item_logic_chunk[6] = [[1573, 1], [1574], [1575], [1576, 23], [1577, 23], [2554, 23, 3], [1578, 23, 3, -1, 23, 5], [1579, 23, 2, 3],
                          [1580, 23, 2, 3], [2555, 23, 1], [1581, 23], [1582, 23], [1583, 23, 2, 4], [2402, 23, 2, 4],
                          [2542, 23], [2543, 23, 3], [1584, 23], [1585, 23, 2, 3], [1586, 23, 3], [2558, 23], [1587, 23, 3], [1588, 23],
                          [1589, 23], [1590, 23], [1591, 23, 2, 3], [1592, 23, 3], [2403, 23, 3, -1, 23, 5], [2559, 23, 3],
                          [1593, 23, 2, 3], [2560, 23, 0, 3], [1594, 23, 2, 3], [1595, 23, 3, 6], [1596, 23, 3],
                          [1597, 23, 3], [2561, 23, 3], [2562, 23, 3], [1598, 23, 3, 5], [1599, 23, 3, 5], [2333, 23, 3], [1546, 23, 3], [2219, 23, 3],
                          [1600, 23, 2, 3], [1601, 23, 2, 3], [2334, 23, 2, 3], [2544, 23, 3, 6, 8], [1602, 23, 4, 6, 8, 10], [2564, 23, 4, 6, 8, 10],
                          [1603, 23, 4, 6, 8, 10], [1604, 23, 4, 6, 8, 10], [1605, 23, 4, 6, 8, 10], [1606, 23, 4, 6, 8, 10],
                          [1607, 23, 2, 4, 6, 8, 10], [1608, 23, 4, 6, 8, 10], [2565, 23, 4, 6, 8, 10], [1609, 23, 4, 6, 8, 10], [1610, 23, 4, 6, 8, 10],
                          [2359, 23, 2, 4, 6, 8, 10], [2360, 23, 2, 4, 6, 8, 10], [2375, 23, 4, 6, 8, 10], [1611, 4, 5],
                          [1612, 23, 4, 5], [1613, 23, 2, 4, 5], [1614, 23, 4, 6, 8, 10], [1615, 23, 4, 6, 8, 10], [2566, 23, 4, 6, 8, 10], [1616, 23, 4, 6, 8, 10],
                          [1617, 23, 4, 6, 8, 10], [1618, 23, 2, 4, 6, 8, 10], [2361, 23, 2, 4, 6, 8, 10], [2362, 23, 3, 5],
                          [1619, 23, 2, 4, 6, 8, 10], [1620, 23, 2, 4, 6, 8, 10], [1621, 23, 3, 5], [2296, 23, 2, 3, 5], [1623, 23, 3, 5],]
        elif settings[1][1] == 1:
            item_logic_chunk[6] = [[1573, 1], [1574, 1], [1575, 1], [1576, 23, 1], [1577, 23, 1], [2554, 23, 1, 3], [1578, 23, 1, 3, -1, 1, 23, 5], [1579, 23, 1, 2, 3],
                          [1580, 23, 1, 2, 3], [2555, 23, 1], [1581, 23, 1], [1582, 23, 1], [1583, 23, 1, 2, 4], [2402, 23, 1, 2, 4],
                          [2542, 23, 1], [2543, 23, 1, 3], [1584, 23, 1], [1585, 23, 1, 2, 3], [1586, 23, 1, 3], [2558, 23, 1], [1587, 23, 1, 3], [1588, 23, 1],
                          [1589, 23, 1], [1590, 23, 1], [1591, 23, 1, 2, 3], [1592, 23, 1, 3], [2403, 23, 1, 3], [2559, 23, 1, 3],
                          [1593, 23, 1, 2, 3], [2560, 23, 1, 3], [1594, 23, 1, 2, 3], [1595, 23, 1, 3, 6], [1596, 23, 1, 3],
                          [1597, 23, 1, 3], [2561, 23, 1, 3], [2562, 23, 1, 3], [1598, 23, 1, 3, 5], [1599, 23, 1, 3, 5], [2333, 23, 1, 3], [1546, 23, 1, 3], [2219, 23, 1, 3],
                          [1600, 23, 1, 2, 3], [1601, 23, 1, 2, 3], [2334, 23, 1, 2, 3], [2544, 23, 1, 3, 6, 8], [1602, 23, 1, 4, 6, 8, 10], [2564, 23, 1, 4, 6, 8, 10],
                          [1603, 23, 1, 4, 6, 8, 10], [1604, 23, 1, 4, 6, 8, 10], [1605, 23, 1, 4, 6, 8, 10], [1606, 23, 1, 4, 6, 8, 10],
                          [1607, 23, 1, 2, 4, 6, 8, 10], [1608, 23, 1, 4, 6, 8, 10], [2565, 1, 4, 6, 8, 10], [1609, 23, 1, 4, 6, 8, 10], [1610, 23, 1, 4, 6, 8, 10],
                          [2359, 23, 1, 2, 4, 6, 8, 10], [2360, 23, 1, 2, 4, 6, 8, 10], [2375, 23, 1, 4, 6, 8, 10], [1611, 23, 1, 4, 5],
                          [1612, 23, 1, 4, 5], [1613, 23, 1, 2, 4, 5], [1614, 23, 1, 4, 6, 8, 10], [1615, 23, 1, 4, 6, 8, 10], [2566, 23, 1, 4, 6, 8, 10], [1616, 23, 1, 4, 6, 8, 10],
                          [1617, 23, 1, 4, 6, 8, 10], [1618, 23, 1, 2, 4, 6, 8], [2361, 23, 1, 2, 4, 6, 8, 10], [2362, 23, 1, 3, 5],
                          [1619, 23, 1, 2, 4, 6, 8, 10], [1620, 23, 1, 2, 4, 6, 8, 10], [1621, 23, 1, 3, 5], [2296, 23, 1, 2, 3, 5], [1623, 23, 1, 3, 5],]
        else:
            item_logic_chunk[6] = [[1573, 1], [1574], [1575], [1576, 23, -1, 5], [1577, 23, -1, 5], [2554, 23, 3, -1, 3, 5], [1578, 23, 3, -1, 5], [1579, 23, 2, 3, -1, 2, 3, 5],
                          [1580, 23, 2, 3, -1, 2, 3, 5], [2555, 23, 1, -1, 1, 5], [1581, 23, -1, 5], [1582, 23, -1, 5], [1583, 23, 2, 4, -1, 2, 4, 5], [2402, 23, 2, 4, -1, 2, 4, 5],
                          [2542, 23, -1, 5], [2543, 23, 3, -1, 3, 5], [1584, 23, -1, 5], [1585, 23, 2, 3, -1, 2, 3, 5], [1586, 23, 3, -1, 5], [2558, 23, -1, 5], [1587, 23, 3, -1, 3, 5], [1588, 23, -1, 5],
                          [1589, 23, -1, 5], [1590, 23, -1, 5], [1591, 23, 2, 3, -1, 2, 3, 5], [1592, 23, 3, -1, 3, 5], [2403, 23, 3, -1, 5], [2559, 23, 3, -1, 3, 5],
                          [1593, 23, 2, 3, -1, 2, 3, 5], [2560, 23, 0, 3, -1, 0, 3, 5], [1594, 23, 2, 3, -1, 2, 3, 5], [1595, 23, 3, 6, -1, 3, 5, 6], [1596, 23, 3, -1, 3, 5],
                          [1597, 23, 3, -1, 3, 5], [2561, 23, 3, -1, 3, 5], [2562, 23, 3, -1, 3, 5], [1598, 3, 5], [1599, 3, 5], [2333, 23, 3, -1, 3, 5], [1546, 23, 3, -1, 3, 5], [2219, 23, 3, -1, 3, 5],
                          [1600, 23, 2, 3, -1, 2, 3, 5], [1601, 23, 2, 3, -1, 2, 3, 5], [2334, 23, 2, 3, -1, 2, 3, 5], [2544, 23, 3, 6, 8, -1, 3, 5, 6, 8], [1602, 23, 4, 6, 8, 10, -1, 4, 5], [2564, 23, 4, 6, 8, 10, -1, 4, 5],
                          [1603, 23, 4, 6, 8, 10, -1, 4, 5], [1604, 23, 4, 6, 8, 10, -1, 4, 5, 6], [1605, 23, 4, 6, 8, 10, -1, 4, 5], [1606, 23, 4, 6, 8, 10, -1, 5],
                          [1607, 23, 2, 4, 6, 8, 10, -1, 2, 5], [1608, 23, 4, 6, 8, 10, -1, 4, 5], [2545, 23, 4, 6, 8, 10, -1, 4, 5], [1609, 23, 4, 6, 8, 10, -1, 4, 5], [1610, 23, 4, 6, 8, 10, -1, 4, 5],
                          [2359, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2360, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2375, 23, 4, 6, 8, 10, -1, 4, 5], [1611, 4, 5],
                          [1612, 4, 5], [1613, 2, 4, 5], [1614, 23, 4, 6, 8, 10, -1, 4, 5], [1615, 23, 4, 6, 8, 10, -1, 4, 5], [2566, 23, 4, 6, 8, 10, -1, 4, 5], [1616, 23, 4, 6, 8, 10, -1, 4, 5],
                          [1617, 23, 4, 6, 8, 10, -1, 4, 5], [1618, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2361, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2362, 3, 5],
                          [1619, 23, 2, 4, 6, 8, 10, -1, 2, 3, 5], [1620, 23, 2, 4, 6, 8, 10, -1, 2, 3, 5], [1621, 3, 5], [2296, 2, 3, 5], [1623, 3, 5],]

        item_logic_chunk[7] = [[24], [25], [26], [27, 3, -1, 5], [28], [29], [30], [31, 15], [32, 15], [33], [34, 15], [35, 15], [157], [158], [159], [161], [162], [163], [164], [165], [167, 6],
        [168, 6], [169, 6], [171, 6], [173, 6], [175, 6], [177, 6], [1643, 6], [265, 16, 17, 2, -1, 2, 5], [266, 16, 17, 2, -1, 2, 5], [267, 16, 17, -1, 5], [148, 15, 6],]

        if settings[1][1] == 0:
            item_logic_chunk[8] = [[413, 16, 2, 6], [414, 16, 2, 6], [452, 16, 17, 1, 6, -1, 16, 1, 5, 6], [461, 16, 17, 1, 6, -1, 16, 1, 5, 6], [462, 16, 17, 1, 6, -1, 16, 1, 5, 6], [463, 16, 17, 1, 6, -1, 16, 1, 5, 6],
            [464, 16, 17, 2, 6, -1, 16, 2, 5, 6], [450, 16, 17, 2, 6, -1, 16, 2, 5, 6], [486, 16, 17, 2, 6, -1, 16, 2, 5, 6], [2567, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6], [2568, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6],
            [2569, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6], [2570, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6], [2571, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6],
            [512, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [513, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [523, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [529, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [2572, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6],
            [545, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [546, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [2573, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6], [2574, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6],
            [2575, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6], [2545, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6],]
        else:
            item_logic_chunk[8] = [[413, 16, 2, 6], [414, 16, 2, 6], [452, 16, 17, 1, 6], [461, 16, 17, 1, 6], [462, 16, 17, 1, 6], [463, 16, 17, 1, 6],
            [464, 16, 17, 2, 6], [450, 16, 17, 2, 6], [486, 16, 17, 2, 6], [2567, 16, 17, 18, 19, 20, 21, 6], [2568, 15, 16, 17, 18, 19, 20, 21, 6], [2569, 15, 16, 17, 18, 19, 20, 21, 6],
            [2570, 15, 16, 17, 18, 19, 20, 21, 6], [2571, 15, 16, 17, 18, 19, 20, 21], [512, 16, 17, 18, 19, 20, 21, 6], [513, 16, 17, 18, 19, 20, 21, 6],
            [523, 16, 17, 18, 19, 20, 21, 6], [529, 16, 17, 18, 19, 20, 21, 6], [2572, 15, 16, 17, 18, 19, 20, 21, 6], [545, 16, 17, 18, 19, 20, 21, 6, 9], [546, 16, 17, 18, 19, 20, 21, 6, 9],
            [2573, 15, 16, 17, 18, 19, 20, 21, 6], [2574, 15, 16, 17, 18, 19, 20, 21, 6], [2575, 15, 16, 17, 18, 19, 20, 21, 6], [2545, 16, 17, 18, 19, 20, 21, 6, 9],]

        if settings[1][0] == 0:
            item_logic_chunk[9] = [[2576, 15, 16, 1, 3, 6], [1243, 15, 16, 24, 1, 3, 6], [1250, 15, 16, 24, 1, 3, 6], [1251, 16, 24, 1, 3, 6], [1252, 16, 24, 1, 3, 6], [184, 15, 6], [185, 15, 6], [186, 15, 6], [187, 15, 6], [188, 15, 6], [189, 15, 6], [191, 15, 6],
            [193, 15, 6], [195, 15, 6], [197, 15, 6], [199, 15, 6], [201, 15, 6], [203, 15, 6], [205, 15, 6], [207, 15, 6], [209, 15, 6], [211, 15, 6], [213, 15, 6], [215, 15, 6], [217, 15, 6], [219, 15, 6],
            [221, 15, 6], [223, 15, 6], [225, 15, 6], [227, 15, 6], [229, 15, 6], [231, 15, 6], [233, 15, 6], [235, 15, 6], [236, 15, 6], [237, 15, 6], [238, 15, 6], [245, 15, 6], [246, 15, 6],]
        else:
            item_logic_chunk[9] = [[2576, 15, 16, 3, 6], [1243, 16, 24, 3, 6], [1250, 16, 24, 3, 6], [1251, 16, 24, 3, 6], [1252, 16, 24, 3, 6], [184, 15, 6], [185, 15, 6], [186, 15, 6], [187, 15, 6], [188, 15, 6], [189, 15, 6], [191, 15, 6],
            [193, 15, 6], [195, 15, 6], [197, 15, 6], [199, 15, 6], [201, 15, 6], [203, 15, 6], [205, 15, 6], [207, 15, 6], [209, 15, 6], [211, 15, 6], [213, 15, 6], [215, 15, 6], [217, 15, 6], [219, 15, 6],
            [221, 15, 6], [223, 15, 6], [225, 15, 6], [227, 15, 6], [229, 15, 6], [231, 15, 6], [233, 15, 6], [235, 15, 6], [236, 15, 6], [237, 15, 6], [238, 15, 6], [245, 15, 6], [246, 15, 6],]

        if settings[1][1] == 0:
            item_logic_chunk[10] = [[2578, 15, 16, 17, 18, 19, 20, 21, 6, 8, 9, -1, 15, 16, 5, 6, 8, 9], [2579, 15, 16, 17, 18, 19, 20, 21, 6, 8, 9, -1, 15, 16, 5, 6, 8, 9], [568, 16, 17, 18, 19, 20, 21, 6, 9, -1, 16, 5, 6, 9], [569, 16, 17, 18, 19, 20, 21, 6, 9, -1, 16, 5, 6, 9], [577, 16, 4, 5, 6], [578, 16, 4, 5, 6], [579, 16, 4, 5, 6], [580, 16, 4, 5, 6],
            [581, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [582, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [583, 16, 17, 1, 6, -1, 16, 1, 5, 6], [584, 16, 17, 2, 6, -1, 16, 2, 5, 6], [585, 16, 17, 2, 6, -1, 16, 2, 5, 6], [2546, 16, 17, 2, 6, -1, 16, 2, 5, 6], [2547, 6, 7, 12, 13],
            [861, 6, 7, 12, 13], [862, 6, 7, 12, 13], [2548, 6, 7, 12, 13], [2081, 15, 2, 4, 5, 6, 8],]
        else:
            item_logic_chunk[10] = [[2578, 15, 16, 17, 18, 19, 20, 21, 6, 8, 9], [2579, 15, 16, 17, 18, 19, 20, 21, 6, 8, 9], [568, 16, 17, 18, 19, 20, 21, 6, 9], [569, 16, 17, 18, 19, 20, 21, 6, 9], [577, 16, 4, 5, 6], [578, 16, 4, 5, 6], [579, 16, 4, 5, 6], [580, 16, 4, 5, 6],
            [581, 16, 17, 18, 19, 20, 21, 6], [582, 16, 17, 18, 19, 20, 21, 6], [583, 16, 17, 1, 6], [584, 16, 17, 2, 6], [585, 16, 17, 2, 6], [2546, 16, 17, 2, 6], [2547, 6, 7, 12, 13],
            [861, 6, 7, 12, 13], [862, 6, 7, 12, 13], [2548, 6, 7, 12, 13], [2081, 15, 2, 4, 5, 6, 8],]

        if settings[1][0] == 0 and settings[1][1] == 0:
            item_logic_chunk[11] = [[1624, 1, 4, 5], [2404, 1, 4, 5], [315, 16, 17, 2, -1, 16, 2, 5], [316, 16, 17, 2, -1, 16, 2, 5], [317, 16, 17, 18, 19, 20, 21, 2, -1, 16, 2, 5], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
            [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
            [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
            [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [2549, 2, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]
        elif settings[1][0] != 0 and settings[1][1] != 0:
            item_logic_chunk[11] = [[1624, 4, 5], [2404, 4, 5], [315, 16, 17, 2], [316, 16, 17, 2], [317, 16, 17, 18, 19, 20, 21, 2], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
            [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
            [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
            [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [2549, 2, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]
        elif settings[1][0] == 1:
            item_logic_chunk[11] = [[1624, 4, 5], [2404, 4, 5], [315, 16, 17, 2, -1, 16, 2, 5], [316, 16, 17, 2, -1, 16, 2, 5], [317, 16, 17, 18, 19, 20, 21, 2, -1, 16, 2, 5], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
            [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
            [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
            [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [2549, 2, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]
        else:
            item_logic_chunk[11] = [[1624, 1, 4, 5], [2404, 1, 4, 5], [315, 16, 17, 2], [316, 16, 17, 2], [317, 16, 17, 18, 19, 20, 21, 2], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
            [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
            [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
            [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [2549, 2, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]

        item_logic_chunk[12] = [[607, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [608, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [609, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [610, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6],
                                [611, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [612, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [613, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [614, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6],
                                [615, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [616, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [617, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [618, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6],
                                [619, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [620, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [621, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [622, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6],
                                [623, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [624, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [625, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [626, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6],
                                [627, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [1401, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [1402, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [628, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6],
                                [629, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6], [630, 15, 22, 1, 2, 6, -1, 15, 22, 2, 5, 6]]

        if settings[1][1] == 0:
            item_logic_chunk[13] = [[2582, 15, 16, 22, 1, 2, 4, 5, 6], [2583, 15, 16, 22, 1, 2, 4, 5, 6], [2584, 15, 16, 22, 1, 2, 4, 5, 6], [2585, 15, 16, 22, 1, 2, 4, 5, 6], [2586, 15, 16, 22, 1, 2, 4, 5, 6],
                                    [2587, 15, 16, 22, 1, 2, 4, 5, 6], [2588, 15, 16, 22, 1, 2, 4, 5, 6], [697, 15, 16, 22, 1, 2, 4, 5, 6], [2589, 15, 16, 22, 1, 2, 4, 5, 6], [2590, 15, 16, 22, 1, 2, 4, 5, 6],
                                    [700, 15, 16, 22, 1, 2, 4, 5, 6], [701, 15, 16, 22, 1, 2, 4, 5, 6], [726, 15, 16, 22, 1, 2, 4, 5, 6], [727, 15, 16, 22, 1, 2, 4, 5, 6],
                                    [728, 15, 16, 22, 1, 2, 4, 5, 6], [760, 15, 22, 0, 6], [761, 15, 22, 0, 6], [764, 15, 22, 2, 6], [765, 15, 16, 22, 1, 2, 4, 5, 6]]
        else:
            item_logic_chunk[13] = [[2582, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [2583, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [2584, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6],
                                    [2585, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [2586, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [2587, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6],
                                    [2588, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [697, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [2589, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6],
                                    [2590, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [700, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [701, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6],
                                    [726, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [727, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6], [728, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6],
                                    [760, 15, 22, 0, 6], [761, 15, 22, 0, 6], [764, 15, 22, 2, 6], [765, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 4, 5, 6]]
        if settings[1][1] == 0 and settings[1][0] == 0:
            item_logic_chunk[14] = [[36, 15, 5], [37, 15, 5], [38, 15, 5], [39, 15, 5], [40, 15, 5], [319, 15, 16, 5], [320, 15, 16, 5], [987, 15, 16, 5], [41, 15, 5, -1, 15, 6], [42, 15, 5, -1, 15, 6],
                                    [43, 15, 5, -1, 15, 6], [2383, 15, 5, -1, 15, 6], [45, 15, 5, -1, 15, 6], [46, 15, 5, -1, 15, 6], [47, 15, 5, -1, 15, 6], [2591, 15, 16, 0, 6], [879, 23, 1, 3, 6, -1, 1, 5, 6],
                                    [880, 23, 1, 3, 6, -1, 1, 5, 6]]
        elif settings[1][0] == 1 and settings[1][1] == 1:
            item_logic_chunk[14] = [[36, 15, 5], [37, 15, 5], [38, 15, 5], [39, 15, 5], [40, 15, 5], [319, 15, 16, 17, 18, 19, 20, 21, 1, 5], [320, 15, 16, 17, 18, 19, 20, 21, 1, 5],
                                    [987, 15, 16, 17, 18, 19, 20, 21, 1, 5], [41, 15, 5, -1, 15, 6], [42, 15, 5, -1, 15, 6], [43, 15, 5, -1, 15, 6], [2383, 15, 5, -1, 15, 6], [45, 15, 5, -1, 15, 6],
                                    [46, 15, 5, -1, 15, 6], [47, 15, 5, -1, 15, 6], [2591, 15, 16, 0, 6], [879, 23, 3, 6, -1, 23, 5, 6], [880, 23, 3, 6, -1, 23, 5, 6]]
        elif settings[1][0] == 1:
            item_logic_chunk[14] = [[36, 15, 5], [37, 15, 5], [38, 15, 5], [39, 15, 5], [40, 15, 5], [319, 15, 16, 5], [320, 15, 16, 5], [987, 15, 16, 5], [41, 15, 5, -1, 15, 6], [42, 15, 5, -1, 15, 6],
                                    [43, 15, 5, -1, 15, 6], [2383, 15, 5, -1, 15, 6], [45, 15, 5, -1, 15, 6], [46, 15, 5, -1, 15, 6], [47, 15, 5, -1, 15, 6], [2591, 15, 16, 0, 6], [879, 23, 3, 6, -1, 5, 6],
                                    [880, 23, 3, 6, -1, 5, 6]]
        else:
            item_logic_chunk[14] = [[36, 15, 5], [37, 15, 5], [38, 15, 5], [39, 15, 5], [40, 15, 5], [319, 15, 16, 17, 18, 19, 20, 21, 1, 5], [320, 15, 16, 17, 18, 19, 20, 21, 1, 5],
                                    [987, 15, 16, 17, 18, 19, 20, 21, 1, 5], [41, 15, 5, -1, 15, 6], [42, 15, 5, -1, 15, 6], [43, 15, 5, -1, 15, 6], [2383, 15, 5, -1, 15, 6], [45, 15, 5, -1, 15, 6],
                                    [46, 15, 5, -1, 15, 6], [47, 15, 5, -1, 15, 6], [2591, 15, 16, 0, 6], [879, 23, 3, 6, -1, 23, 5, 6], [880, 23, 3, 6, -1, 23, 5, 6]]
        if settings[1][0] == 0:
            item_logic_chunk[15] = [[1630, 15, 27, 1, 5], [1631, 15, 27, 1, 3, 5], [2592, 15, 27, 1, 3, 5], [2593, 15, 27, 1, 3, 5], [2594, 15, 27, 1, 3, 5], [1632, 15, 27, 1, 5], [1633, 15, 27, 1, 5], [2595, 15, 27, 1, 5], [2596, 15, 27, 1, 5], [1634, 15, 27, 1, 5], [2597, 15, 27, 1, 3, 5], [2598, 15, 27, 1, 5], [1635, 15, 27, 1, 5],
                                    [2599, 15, 27, 1, 3, 5], [2600, 15, 27, 1, 5], [2601, 15, 27, 1, 3, 5, 6], [1636, 15, 27, 1, 3, 5, 6], [1637, 15, 27, 1, 3, 5, 6], [1638, 15, 27, 1, 3, 5, 6], [1639, 15, 27, 1, 2, 3, 5, 6], [280, 15, 27, 1, 3, 5, 6], [322, 15, 27, 1, 3, 5, 6], [1640, 15, 27, 1, 2, 3, 5, 6], [1641, 15, 27, 1, 2, 3, 5, 6],
                                    [1642, 15, 27, 1, 3, 5, 6], [2602, 15, 27, 1, 3, 5, 6], [2603, 15, 27, 1, 3, 5, 6], [2363, 15, 27, 1, 3, 5, 6], [2364, 15, 27, 1, 3, 5, 6], [2365, 15, 27, 1, 3, 5, 6], [2366, 15, 27, 1, 3, 5, 6], [2367, 15, 27, 1, 3, 5, 6], [2604, 15, 27, 1, 3, 5, 6], [2605, 15, 27, 1, 3, 5, 6], [1646, 15, 27, 1, 3, 5, 6], [1647, 15, 27, 1, 3, 5, 6], [1648, 15, 27, 1, 2, 3, 5, 6],
                                    [1649, 15, 27, 1, 3, 5, 6], [2606, 15, 27, 1, 3, 5, 6], [2405, 15, 27, 1, 3, 5, 6], [2406, 15, 27, 1, 3, 5, 6], [2407, 15, 27, 1, 3, 5, 6], [2607, 15, 27, 1, 3, 5, 6], [1651, 15, 27, 1, 3, 5, 6], [1652, 15, 27, 1, 3, 5, 6], [2297, 15, 27, 1, 3, 5, 6], [2298, 15, 27, 1, 3, 5, 6],
                                    [1655, 15, 27, 1, 3, 5, 6], [1656, 15, 27, 1, 3, 5, 6], [1657, 15, 27, 1, 3, 5, 6], [1658, 15, 27, 1, 3, 5, 6], [1659, 15, 27, 1, 2, 3, 5, 6], [1660, 15, 27, 1, 2, 3, 5, 6], [1661, 15, 27, 1, 2, 3, 5, 6], [1662, 15, 27, 1, 2, 3, 5, 6], [2377, 15, 27, 1, 3, 5, 6], [2378, 15, 27, 1, 3, 5, 6], [2379, 15, 27, 1, 3, 5, 6],
                                    [1663, 15, 27, 1, 3, 5, 6], [1664, 15, 27, 1, 3, 5, 6], [2380, 15, 27, 1, 3, 5, 6], [2381, 15, 27, 1, 3, 5, 6], [1665, 15, 27, 1, 3, 5, 6], [1666, 15, 27, 1, 3, 5, 6], [1667, 15, 27, 1, 3, 5, 6], [2354, 15, 27, 1, 2, 3, 5, 6], [1668, 15, 27, 1, 3, 5, 6], [1669, 15, 27, 1, 2, 3, 5, 6],
                                    [1670, 15, 27, 1, 3, 5, 6], [1671, 15, 27, 1, 2, 3, 5, 6], [1672, 15, 27, 1, 3, 5, 6], [2408, 15, 27, 1, 3, 5, 6], [2409, 15, 27, 1, 2, 3, 5, 6], [1673, 15, 27, 1, 3, 5, 6], [1674, 15, 27, 1, 3, 5, 6], [1675, 15, 27, 1, 3, 5, 6], [1676, 15, 27, 1, 2, 4, 5, 6], [1677, 15, 27, 1, 2, 4, 5, 6], [1678, 15, 27, 1, 3, 5, 6], [1679, 15, 27, 1, 2, 4, 5, 6]]
        else:
            item_logic_chunk[15] = [[1630, 15, 27, 5], [1631, 15, 27, 3, 5], [2592, 15, 27, 3, 5], [2593, 15, 27, 3, 5], [2594, 15, 27, 3, 5], [1632, 15, 27, 5], [1633, 15, 27, 5], [2595, 15, 27, 5], [2596, 15, 27, 5], [1634, 15, 27, 5], [2597, 15, 27, 3, 5], [2598, 15, 27, 5], [1635, 15, 27, 5], [2599, 15, 27, 3, 5], [2600, 15, 27, 5],
                                    [2601, 15, 27, 1, 3, 5, 6], [1636, 15, 27, 1, 3, 5, 6], [1637, 15, 27, 1, 3, 5, 6], [1638, 15, 27, 1, 3, 5, 6], [1639, 15, 27, 2, 3, 5, 6], [280, 15, 27, 3, 5, 6], [322, 15, 27, 3, 5, 6], [1640, 15, 27, 2, 3, 5, 6], [1641, 15, 27, 2, 3, 5, 6], [1642, 15, 27, 3, 5, 6], [2602, 15, 27, 3, 5, 6], [2603, 15, 27, 3, 5, 6],
                                    [2363, 15, 27, 3, 5, 6], [2364, 15, 27, 3, 5, 6], [2365, 15, 27, 3, 5, 6], [2366, 15, 27, 3, 5, 6], [2367, 15, 27, 3, 5, 6], [2604, 15, 27, 3, 5, 6], [2605, 15, 27, 3, 5, 6], [1646, 15, 27, 3, 5, 6], [1647, 15, 27, 3, 5, 6], [1648, 15, 27, 3, 5, 6], [1649, 15, 27, 3, 5, 6], [2606, 15, 27, 3, 5, 6], [2405, 15, 27, 3, 5, 6], [2406, 15, 27, 3, 5, 6],
                                    [2407, 15, 27, 3, 5, 6], [2607, 15, 27, 0, 3, 5, 6], [1651, 15, 27, 0, 3, 5, 6], [1652, 15, 27, 0, 3, 5, 6], [2297, 15, 27, 0, 3, 5, 6], [2298, 15, 27, 0, 3, 5, 6], [1655, 15, 27, 0, 3, 5, 6], [1656, 15, 27, 0, 3, 5, 6], [1657, 15, 27, 0, 3, 5, 6], [1658, 15, 27, 3, 5, 6], [1659, 15, 27, 2, 3, 5, 6],
                                    [1660, 15, 27, 2, 3, 5, 6], [1661, 15, 27, 2, 3, 5, 6], [1662, 15, 27, 2, 3, 5, 6], [2337, 15, 27, 0, 3, 5, 6], [2338, 15, 27, 0, 3, 5, 6], [2339, 15, 27, 0, 3, 5, 6], [1663, 15, 27, 0, 3, 5, 6], [1664, 15, 27, 0, 3, 5, 6], [2380, 15, 27, 0, 3, 5, 6], [2381, 15, 27, 0, 3, 5, 6],
                                    [1665, 15, 27, 0, 3, 5, 6], [1666, 15, 27, 0, 3, 5, 6], [1667, 15, 27, 0, 3, 5, 6], [2354, 15, 27, 2, 3, 5, 6], [1668, 15, 27, 0, 3, 5, 6], [1669, 15, 27, 2, 3, 5, 6], [1670, 15, 27, 0, 3, 5, 6], [1671, 15, 27, 2, 3, 5, 6], [1672, 15, 27, 0, 3, 5, 6], [2408, 15, 27, 2, 3, 5, 6],
                                    [2409, 15, 27, 2, 3, 5, 6], [1673, 15, 27, 1, 3, 5, 6], [1674, 15, 27, 1, 3, 5, 6], [1675, 15, 27, 0, 3, 5, 6], [1676, 15, 27, 2, 3, 5, 6], [1677, 15, 27, 2, 3, 5, 6], [1678, 15, 27, 0, 3, 5, 6], [1679, 15, 27, 2, 3, 5, 6]]

        if settings[1][0] == 0:
            item_logic_chunk[16] = [[2610, 15, 16, 24, 1, 3, 6], [1259, 15, 16, 24, 1, 3, 6], [2611, 15, 16, 24, 25, 1, 3, 6], [2612, 15, 16, 24, 25, 1, 3, 6], [1269, 15, 16, 24, 25, 1, 3, 6], [1270, 15, 16, 24, 25, 1, 3, 6], [1118, 15, 16, 24, 25, 1, 3, 6, 10], [1119, 15, 16, 24, 25, 1, 3, 6, 10],
                                    [2613, 15, 16, 24, 25, 1, 3, 6, 10], [1275, 15, 16, 24, 25, 1, 3, 6, 10], [1276, 15, 16, 24, 25, 1, 3, 6, 10], [1277, 15, 16, 24, 25, 1, 3, 6, 10], [2614, 15, 16, 24, 25, 1, 3, 6, 10], [2615, 15, 16, 24, 25, 1, 3, 6, 10], [1182, 15, 16, 24, 25, 1, 3, 6, 8, 9, 10],
                                    [1281, 15, 16, 24, 25, 1, 3, 6, 8, 9, 10], [2616, 15, 16, 24, 1, 3, 6], [2617, 15, 16, 24, 1, 3, 6], [1285, 15, 16, 24, 1, 3, 6], [1296, 15, 16, 24, 25, 1, 3, 6, 8, 9, 10], [1297, 15, 16, 24, 25, 1, 3, 6, 8, 9, 10], [2618, 15, 16, 1, 3, 6],
                                    [1339, 15, 16, 1, 4, 6, -1, 15, 16, 5, 6], [1340, 15, 16, 1, 4, 6], [1341, 15, 16, 1, 4, 6, -1, 15, 16, 5, 6], [2619, 15, 16, 1, 4, 6, -1, 15, 16, 5, 6], [2620, 15, 16, 1, 4, 6, 10], [1384, 15, 16, 5, 6], [1385, 15, 16, 5, 6],
                                    [1386, 15, 16, 4, 6], [1387, 15, 16, 4, 6], [1388, 15, 16, 4, 6], [1389, 15, 16, 4, 6], [1395, 15, 16, 4, 6], [1396, 15, 16, 1, 3, 5, 6]]
        else:
            item_logic_chunk[16] = [[2610, 15, 16, 24, 0, 3, 6], [1259, 15, 16, 24, 0, 3, 6], [2611, 15, 16, 24, 25, 0, 3, 6], [2612, 15, 16, 24, 25, 0, 3, 6], [1269, 15, 16, 24, 25, 0, 3, 6], [1270, 15, 16, 24, 25, 0, 3, 6], [1118, 15, 16, 24, 25, 0, 3, 6, 10], [1119, 15, 16, 24, 25, 0, 3, 6, 10],
                                    [2613, 15, 16, 24, 25, 0, 3, 6, 10], [1275, 15, 16, 24, 25, 0, 3, 6, 10], [1276, 15, 16, 24, 25, 0, 3, 6, 10], [1277, 15, 16, 24, 25, 0, 3, 6, 10], [2614, 15, 16, 24, 25, 0, 3, 6, 10], [2615, 15, 16, 24, 25, 0, 3, 6, 10], [1182, 15, 16, 24, 25, 0, 3, 6, 8, 9, 10],
                                    [1281, 15, 16, 24, 25, 0, 3, 6, 8, 9, 10], [2616, 15, 16, 24, 3, 6], [2617, 15, 16, 24, 3, 6], [1285, 15, 16, 24, 3, 6], [1296, 15, 16, 24, 25, 0, 3, 6, 8, 9, 10], [1297, 15, 16, 24, 25, 0, 3, 6, 8, 9, 10], [2618, 15, 16, 1, 3, 6], [1339, 15, 16, 4, 6, -1, 15, 16, 5, 6],
                                    [1340, 15, 16, 4, 6], [1341, 15, 16, 4, 6, -1, 15, 16, 5, 6], [2619, 15, 16, 4, 6, -1, 15, 16, 5, 6], [2620, 15, 16, 4, 6, 10], [1384, 15, 16, 5, 6], [1385, 15, 16, 5, 6], [1386, 15, 16, 4, 6], [1387, 15, 16, 4, 6], [1388, 15, 16, 4, 6], [1389, 15, 16, 4, 6],
                                    [1395, 15, 16, 4, 6], [1396, 15, 16, 1, 3, 5, 6]]

        if settings[1][0] == 0:
            item_logic_chunk[17] = [[2092, 15, 1], [2093, 15, 1, 2], [2094, 15, 1, 5], [2095, 15, 1, 5], [2096, 15, 1, 2, 5], [2097, 15, 1, 5], [2098, 15, 1, 5], [2099, 15, 1, 5], [2100, 15, 1, 5], [2101, 15, 1, 2, 5], [2621, 15, 1, 4, 5], [2102, 15, 1, 3, 5], [2103, 15, 1, 3, 5], [2104, 15, 1, 3, 5],
                                    [2622, 15, 1, 4, 5], [2623, 15, 1, 4, 5], [2105, 15, 1, 4, 5], [2106, 15, 1, 2, 3, 5], [2107, 15, 1, 2, 4, 5], [2624, 15, 1, 4, 5], [2108, 15, 1, 4, 5], [2625, 15, 1, 4, 5], [2109, 15, 1, 4, 5], [2626, 15, 1, 2, 4, 5, 6], [2627, 15, 1, 4, 5],
                                    [2110, 15, 1, 4, 5, 6], [2111, 15, 1, 4, 5, 6], [2112, 15, 1, 2, 4, 5, 6], [2113, 15, 1, 4, 5, 6], [2114, 15, 1, 4, 5, 6], [2115, 15, 1, 4, 5, 6], [2116, 15, 1, 4, 5, 6], [2117, 15, 1, 2, 4, 5, 6], [2628, 15, 1, 2, 4, 5, 6], [2118, 15, 1, 2, 4, 5, 6], [2119, 15, 1, 2, 4, 5, 6],
                                    [2629, 15, 1, 4, 5, 6], [2120, 15, 1, 4, 5, 6], [2121, 15, 1, 4, 5, 6], [2630, 15, 1, 2, 4, 5, 6], [2122, 15, 1, 2, 4, 5, 6], [2123, 15, 1, 2, 4, 5, 6], [2124, 15, 1, 2, 4, 5, 6], [2631, 15, 1, 2, 4, 5, 6], [2125, 15, 1, 2, 4, 5, 6], [2126, 15, 1, 2, 4, 5, 6],
                                    [2127, 15, 1, 2, 4, 5, 6], [2410, 15, 1, 2, 4, 5, 6], [2411, 15, 1, 2, 4, 5, 6], [2128, 15, 1, 2, 4, 5, 6], [2129, 15, 1, 2, 4, 5, 6], [2130, 15, 1, 2, 4, 5, 6], [2131, 15, 1, 2, 4, 5, 6], [2132, 15, 1, 2, 4, 5, 6], [2133, 15, 1, 2, 4, 5, 6], [2134, 15, 1, 2, 4, 5, 6], [2135, 15, 1, 2, 4, 5, 6],
                                    [2136, 15, 1, 2, 4, 5, 6], [2137, 15, 1, 2, 4, 5, 6]]
        else:
            item_logic_chunk[17] = [[2092, 15], [2093, 15, 2], [2094, 15, 0, 5], [2095, 15, 0, 5], [2096, 15, 2, 5], [2097, 15, 0, 5], [2098, 15, 0, 5], [2099, 15, 0, 5], [2100, 15, 0, 5], [2101, 15, 2, 5], [2621, 15, 0, 4, 5], [2102, 15, 0, 3, 5], [2103, 15, 0, 3, 5], [2104, 15, 0, 3, 5], [2622, 15, 0, 4, 5],
                                    [2623, 15, 1, 4, 5], [2105, 15, 1, 4, 5], [2106, 15, 1, 2, 3, 5], [2107, 15, 1, 2, 4, 5], [2624, 15, 0, 4, 5], [2108, 15, 0, 4, 5], [2625, 15, 0, 4, 5], [2109, 15, 0, 4, 5], [2626, 15, 2, 4, 5, 6], [2627, 15, 0, 4, 5], [2110, 15, 0, 4, 5, 6],
                                    [2111, 15, 0, 4, 5, 6], [2112, 15, 2, 4, 5, 6], [2113, 15, 1, 4, 5, 6], [2114, 15, 0, 4, 5, 6], [2115, 15, 0, 4, 5, 6], [2116, 15, 0, 4, 5, 6], [2117, 15, 2, 4, 5, 6], [2628, 15, 1, 2, 4, 5, 6], [2118, 15, 2, 4, 5, 6], [2119, 15, 2, 4, 5, 6], [2629, 15, 0, 4, 5, 6],
                                    [2120, 15, 0, 4, 5, 6], [2121, 15, 0, 4, 5, 6], [2630, 15, 2, 4, 5, 6], [2122, 15, 2, 4, 5, 6], [2123, 15, 2, 4, 5, 6], [2124, 15, 2, 4, 5, 6], [2631, 15, 2, 4, 5, 6], [2125, 15, 2, 4, 5, 6], [2126, 15, 2, 4, 5, 6], [2127, 15, 2, 4, 5, 6], [2410, 15, 2, 4, 5, 6], [2411, 15, 2, 4, 5, 6],
                                    [2128, 15, 2, 4, 5, 6], [2129, 15, 2, 4, 5, 6], [2130, 15, 2, 4, 5, 6], [2131, 15, 2, 4, 5, 6], [2132, 15, 2, 4, 5, 6], [2133, 15, 2, 4, 5, 6], [2134, 15, 2, 4, 5, 6], [2135, 15, 2, 4, 5, 6], [2136, 15, 2, 4, 5, 6], [2137, 15, 2, 4, 5, 6]]

        if settings[1][0] == 0 and settings[1][1] == 0:
            item_logic_chunk[18] = [[117, 15, 1], [118, 15, 1, 2, 5], [1298, 15, 16, 24, 25, 1, 3, 6], [1306, 15, 16, 24, 25, 1, 3, 6], [2384, 14], [2385, 14], [2386, 14], [2387, 14], [327, 15, 16, 17, 2, -1, 15, 16, 2, 5], [328, 15, 16, 17, 2, -1, 15, 16, 2, 5], [329, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                                    [330, 15, 16, 17, 2, -1, 15, 16, 2, 5], [331, 15, 16, 17, 2, -1, 15, 16, 2, 5], [332, 15, 16, 17, 2, -1, 15, 16, 2, 5], [333, 15, 16, 17, 2, -1, 15, 16, 2, 5], [334, 15, 16, 17, 2, -1, 15, 16, 2, 5], [335, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                                    [336, 15, 16, 17, 2, -1, 15, 16, 2, 5], [337, 15, 16, 17, 2, -1, 15, 16, 2, 5], [754, 15, 16, 22, 1, 2, 4, 5, 6], [755, 15, 16, 22, 1, 2, 4, 5, 6], [756, 15, 16, 22, 1, 2, 4, 5, 6], [757, 15, 16, 22, 1, 2, 4, 5, 6]]
        elif settings[1][1] == 1:
            item_logic_chunk[18] = [[117, 15, 1], [118, 15, 1, 2, 5], [1298, 15, 16, 24, 25, 1, 3, 6], [1306, 15, 16, 24, 25, 1, 3, 6], [2384, 14], [2385, 14], [2386, 14], [2387, 14], [327, 15, 16, 17, 2], [328, 15, 16, 17, 2], [329, 15, 16, 17, 2],
                                    [330, 15, 16, 17, 2], [331, 15, 16, 17, 2], [332, 15, 16, 17, 2], [333, 15, 16, 17, 2], [334, 15, 16, 17, 2], [335, 15, 16, 17, 2], [336, 15, 16, 17, 2], [337, 15, 16, 17, 2], [754, 15, 16, 22, 1, 2, 4, 5, 6], [755, 15, 16, 22, 1, 2, 4, 5, 6],
                                    [756, 15, 16, 22, 1, 2, 4, 5, 6], [757, 15, 16, 22, 1, 2, 4, 5, 6]]
        else:
            item_logic_chunk[18] = [[117, 15, 1], [118, 15, 2, 5], [1298, 15, 16, 24, 25, 3, 6], [1306, 15, 16, 24, 25, 3, 6], [2384, 14], [2385, 14], [2386, 14], [2387, 14], [327, 15, 16, 17, 2, -1, 15, 16, 2, 5], [328, 15, 16, 17, 2, -1, 15, 16, 2, 5], [329, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                                    [330, 15, 16, 17, 2, -1, 15, 16, 2, 5], [331, 15, 16, 17, 2, -1, 15, 16, 2, 5], [332, 15, 16, 17, 2, -1, 15, 16, 2, 5], [333, 15, 16, 17, 2, -1, 15, 16, 2, 5], [334, 15, 16, 17, 2, -1, 15, 16, 2, 5], [335, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                                    [336, 15, 16, 17, 2, -1, 15, 16, 2, 5], [337, 15, 16, 17, 2, -1, 15, 16, 2, 5], [754, 15, 16, 22, 1, 2, 4, 5, 6], [755, 15, 16, 22, 1, 2, 4, 5, 6], [756, 15, 16, 22, 1, 2, 4, 5, 6], [757, 15, 16, 22, 1, 2, 4, 5, 6]]

        if settings[1][0] == 0 and settings[1][1] == 0:
            item_logic_chunk[19] = [[2632, 23, 1, 3, 6, 8, -1, 1, 5, 6, 8], [912, 23, 1, 3, 6, 8, -1, 1, 5, 6, 8], [913, 23, 1, 3, 6, 8, -1, 1, 5, 6, 8], [914, 23, 1, 3, 6, 8, -1, 1, 5, 6, 8], [915, 23, 1, 3, 6, 8, -1, 1, 5, 6, 8], [916, 23, 1, 3, 6, 8, -1, 1, 5, 6, 8],
                                    [1782, 23, 1, 4, 6, 8, 10, -1, 1, 5, 6, 10], [1756, 23, 1, 4, 6, 8, 10, -1, 1, 5, 6, 10], [917, 23, 1, 4, 6, 8, 10, -1, 1, 5, 6], [918, 23, 1, 4, 6, 8, 10, -1, 1, 5, 6], [919, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [2633, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [921, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [922, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [923, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [924, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [925, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [926, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2634, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [2635, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [927, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [928, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [929, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [2636, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [930, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [931, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [932, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [933, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [1806, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [1807, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2637, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [936, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [937, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [938, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [939, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [940, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2638, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2639, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [941, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [942, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [943, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [944, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2640, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [2641, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [953, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2642, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [954, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [961, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [962, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [965, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [966, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [967, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [968, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2397, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [970, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [971, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [972, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [976, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [977, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [984, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [985, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [1915, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [2643, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11],
                                    [920, 23, 1, 4, 6, 8, 9, 10, 11, -1, 1, 5, 6, 8, 9, 10, 11], [986, 1, 4, 5, 6], [989, 1, 4, 5, 6], [990, 23, 1, 3, -1, 1, 5], [991, 23, 1, 3, -1, 1, 5], [992, 23, 1, 3, -1, 1, 5], [1050, 23, 1, -1, 1, 5], [1051, 23, 1, -1, 1, 5],
                                    [1653, 15, 27, 1, 3, 5, 6], [1654, 15, 27, 1, 3, 5, 6], [2368, 15, 27, 1, 3, 5, 6], [2369, 15, 27, 1, 3, 5, 6], [2376, 15, 27, 1, 3, 5, 6]]
        elif settings[1][0] == 1 and settings[1][1] == 1:
            item_logic_chunk[19] = [[2632, 23, 3, 6, 8, -1, 23, 5, 6, 8], [912, 23, 3, 6, 8, -1, 23, 5, 6, 8], [913, 23, 3, 6, 8, -1, 23, 5, 6, 8], [914, 23, 3, 6, 8, -1, 23, 5, 6, 8], [915, 23, 3, 6, 8, -1, 23, 5, 6, 8], [916, 23, 3, 6, 8, -1, 23, 5, 6, 8],
                                    [1782, 23, 4, 6, 8, 10], [1756, 23, 4, 6, 8, 10], [917, 23, 4, 6, 8, 10], [918, 23, 4, 6, 8, 10], [919, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2633, 23, 0, 4, 5, 6, 8, 9, 10, 11], [921, 23, 0, 4, 5, 6, 8, 9, 10, 11], [922, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [923, 23, 0, 4, 5, 6, 8, 9, 10, 11], [924, 23, 0, 4, 5, 6, 8, 9, 10, 11], [925, 23, 0, 4, 5, 6, 8, 9, 10, 11], [926, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2634, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2635, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [927, 23, 0, 4, 5, 6, 8, 9, 10, 11], [928, 23, 0, 4, 5, 6, 8, 9, 10, 11], [929, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2636, 23, 0, 4, 5, 6, 8, 9, 10, 11], [930, 23, 0, 4, 5, 6, 8, 9, 10, 11], [931, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [932, 23, 0, 4, 5, 6, 8, 9, 10, 11], [933, 23, 0, 4, 5, 6, 8, 9, 10, 11], [1806, 23, 0, 4, 5, 6, 8, 9, 10, 11], [1807, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2637, 23, 0, 4, 5, 6, 8, 9, 10, 11], [936, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [937, 23, 0, 4, 5, 6, 8, 9, 10, 11], [938, 23, 0, 4, 5, 6, 8, 9, 10, 11], [939, 23, 0, 4, 5, 6, 8, 9, 10, 11], [940, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2638, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2639, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [941, 23, 0, 4, 5, 6, 8, 9, 10, 11], [942, 23, 0, 4, 5, 6, 8, 9, 10, 11], [943, 23, 0, 4, 5, 6, 8, 9, 10, 11], [944, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2640, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2641, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [953, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2642, 23, 0, 4, 5, 6, 8, 9, 10, 11], [954, 23, 0, 4, 5, 6, 8, 9, 10, 11], [961, 23, 0, 4, 5, 6, 8, 9, 10, 11], [962, 23, 0, 4, 5, 6, 8, 9, 10, 11], [965, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [966, 23, 0, 4, 5, 6, 8, 9, 10, 11], [967, 23, 0, 4, 5, 6, 8, 9, 10, 11], [968, 23, 0, 4, 5, 6, 8, 9, 10, 11], [2397, 23, 0, 4, 5, 6, 8, 9, 10, 11], [970, 23, 0, 4, 5, 6, 8, 9, 10, 11], [971, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [972, 23, 0, 4, 5, 6, 8, 9, 10, 11], [976, 23, 0, 4, 5, 6, 8, 9, 10, 11], [977, 23, 0, 4, 5, 6, 8, 9, 10, 11], [984, 23, 0, 4, 5, 6, 8, 9, 10, 11], [985, 23, 0, 4, 5, 6, 8, 9, 10, 11], [1915, 23, 0, 4, 5, 6, 8, 9, 10, 11],
                                    [2643, 23, 0, 4, 5, 6, 8, 9, 10, 11], [920, 23, 0, 4, 5, 6, 8, 9, 10, 11], [986, 23, 0, 4, 5, 6], [989, 23, 0, 4, 5, 6], [990, 23, 0, 3, -1, 23, 0, 5], [991, 23, 0, 3, -1, 23, 0, 5], [992, 23, 0, 3, -1, 23, 0, 5],
                                    [1050, 23, 0], [1051, 23, 0], [1653, 15, 27, 0, 3, 5, 6], [1654, 15, 27, 0, 3, 5, 6], [2368, 15, 27, 0, 3, 5, 6], [2369, 15, 27, 0, 3, 5, 6], [2376, 15, 27, 0, 3, 5, 6]]
        elif settings[1][1] == 1:
            item_logic_chunk[19] = [[2632, 23, 1, 3, 6, 8, -1, 23, 5, 6, 8], [912, 23, 1, 3, 6, 8, -1, 23, 5, 6, 8], [913, 23, 1, 3, 6, 8, -1, 23, 5, 6, 8], [914, 23, 1, 3, 6, 8, -1, 23, 5, 6, 8], [915, 23, 1, 3, 6, 8, -1, 23, 5, 6, 8], [916, 23, 1, 3, 6, 8, -1, 23, 5, 6, 8],
                                    [1782, 23, 1, 4, 6, 8, 10], [1756, 23, 1, 4, 6, 8, 10], [917, 23, 1, 4, 6, 8, 10], [918, 23, 1, 4, 6, 8, 10], [919, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2633, 23, 1, 4, 5, 6, 8, 9, 10, 11], [921, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [922, 23, 1, 4, 5, 6, 8, 9, 10, 11], [923, 23, 1, 4, 5, 6, 8, 9, 10, 11], [924, 23, 1, 4, 5, 6, 8, 9, 10, 11], [925, 23, 1, 4, 5, 6, 8, 9, 10, 11], [926, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2634, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [2635, 23, 1, 4, 5, 6, 8, 9, 10, 11], [927, 23, 1, 4, 5, 6, 8, 9, 10, 11], [928, 23, 1, 4, 5, 6, 8, 9, 10, 11], [929, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2636, 23, 1, 4, 5, 6, 8, 9, 10, 11], [930, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [931, 23, 1, 4, 5, 6, 8, 9, 10, 11], [932, 23, 1, 4, 5, 6, 8, 9, 10, 11], [933, 23, 1, 4, 5, 6, 8, 9, 10, 11], [1806, 23, 1, 4, 5, 6, 8, 9, 10, 11], [1807, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2637, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [936, 23, 1, 4, 5, 6, 8, 9, 10, 11], [937, 23, 1, 4, 5, 6, 8, 9, 10, 11], [938, 23, 1, 4, 5, 6, 8, 9, 10, 11], [939, 23, 1, 4, 5, 6, 8, 9, 10, 11], [940, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2638, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [2639, 23, 1, 4, 5, 6, 8, 9, 10, 11], [941, 23, 1, 4, 5, 6, 8, 9, 10, 11], [942, 23, 1, 4, 5, 6, 8, 9, 10, 11], [943, 23, 1, 4, 5, 6, 8, 9, 10, 11], [944, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2640, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [2641, 23, 1, 4, 5, 6, 8, 9, 10, 11], [953, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2642, 23, 1, 4, 5, 6, 8, 9, 10, 11], [954, 23, 1, 4, 5, 6, 8, 9, 10, 11], [961, 23, 1, 4, 5, 6, 8, 9, 10, 11], [962, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [965, 23, 1, 4, 5, 6, 8, 9, 10, 11], [966, 23, 1, 4, 5, 6, 8, 9, 10, 11], [967, 23, 1, 4, 5, 6, 8, 9, 10, 11], [968, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2397, 23, 1, 4, 5, 6, 8, 9, 10, 11], [970, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [971, 23, 1, 4, 5, 6, 8, 9, 10, 11], [972, 23, 1, 4, 5, 6, 8, 9, 10, 11], [976, 23, 1, 4, 5, 6, 8, 9, 10, 11], [977, 23, 1, 4, 5, 6, 8, 9, 10, 11], [984, 23, 1, 4, 5, 6, 8, 9, 10, 11], [985, 23, 1, 4, 5, 6, 8, 9, 10, 11],
                                    [1915, 23, 1, 4, 5, 6, 8, 9, 10, 11], [2643, 23, 1, 4, 5, 6, 8, 9, 10, 11], [920, 23, 1, 4, 5, 6, 8, 9, 10, 11], [986, 23, 1, 4, 5, 6], [989, 23, 1, 4, 5, 6], [990, 23, 1, 3, -1, 23, 1, 5], [991, 23, 1, 3, -1, 23, 1, 5],
                                    [992, 23, 1, 3, -1, 23, 1, 5], [1050, 23, 1], [1051, 23, 1], [1653, 15, 27, 1, 3, 5, 6], [1654, 15, 27, 1, 3, 5, 6], [2368, 15, 27, 1, 3, 5, 6], [2369, 15, 27, 1, 3, 5, 6], [2376, 15, 27, 1, 3, 5, 6]]
        else:
            item_logic_chunk[19] = [[2632, 23, 3, 6, 8, -1, 5, 6, 8], [912, 23, 3, 6, 8, -1, 5, 6, 8], [913, 23, 3, 6, 8, -1, 5, 6, 8], [914, 23, 3, 6, 8, -1, 5, 6, 8], [915, 23, 3, 6, 8, -1, 5, 6, 8], [916, 23, 3, 6, 8, -1, 5, 6, 8], [1782, 23, 4, 6, 8, 10, -1, 5, 6, 10],
                                    [1756, 23, 4, 6, 8, 10, -1, 5, 6, 10], [917, 23, 4, 6, 8, 10, -1, 5, 6], [918, 23, 4, 6, 8, 10, -1, 5, 6], [919, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2633, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [921, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [922, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [923, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [924, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [925, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [926, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2634, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2635, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [927, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [928, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [929, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2636, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [930, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [931, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [932, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [933, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [1806, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [1807, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2637, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [936, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [937, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [938, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [939, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [940, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [2638, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2639, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [941, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [942, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [943, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [944, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2640, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2641, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [953, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2642, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [954, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [961, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [962, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [965, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [966, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [967, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [968, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2397, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [970, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [971, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [972, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [976, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [977, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [984, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [985, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [1915, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [2643, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11], [920, 23, 0, 4, 5, 6, 8, 9, 10, 11, -1, 0, 5, 6, 8, 9, 10, 11],
                                    [986, 0, 4, 5, 6], [989, 0, 4, 5, 6], [990, 23, 0, 3, -1, 0, 5], [991, 23, 0, 3, -1, 0, 5], [992, 23, 0, 3, -1, 0, 5], [1050, 23, 0, -1, 0, 5], [1051, 23, 0, -1, 0, 5], [1653, 15, 27, 0, 3, 5, 6], [1654, 15, 27, 0, 3, 5, 6], [2368, 15, 27, 0, 3, 5, 6],
                                    [2369, 15, 27, 0, 3, 5, 6], [2376, 15, 27, 0, 3, 5, 6]]

        if settings[1][0] == 0:
            item_logic_chunk[20] = [[1968, 15, 1, 4, 5, 6], [1969, 15, 1, 4, 5, 6], [1970, 15, 1, 4, 5, 6], [1971, 15, 1, 4, 5, 6], [1972, 15, 1, 4, 5, 6], [1973, 15, 1, 4, 5, 6], [1974, 15, 1, 4, 5, 6], [2008, 15, 1, 4, 5, 6], [2009, 15, 1, 4, 5, 6], [2010, 15, 1, 4, 5, 6], [2016, 15, 1, 2, 4, 5, 6],
                                    [2017, 15, 1, 2, 4, 5, 6], [2018, 15, 1, 2, 4, 5, 6], [2019, 15, 1, 2, 4, 5, 6], [2020, 15, 1, 2, 4, 5, 6], [2021, 15, 1, 2, 4, 5, 6], [2022, 15, 1, 2, 4, 5, 6], [2023, 15, 1, 2, 4, 5, 6], [2644, 15, 1, 2, 4, 5, 6], [2645, 15, 1, 2, 4, 5, 6], [2646, 15, 1, 2, 4, 5, 6, 8, 9],
                                    [2024, 15, 1, 2, 4, 5, 6], [2025, 15, 1, 2, 4, 5, 6], [2026, 15, 1, 2, 4, 5, 6], [2027, 15, 1, 2, 4, 5, 6], [2028, 15, 1, 2, 4, 5, 6], [2029, 15, 1, 2, 4, 5, 6], [2030, 15, 1, 2, 4, 5, 6, 8, 9], [2031, 15, 1, 2, 4, 5, 6], [2647, 15, 1, 2, 4, 5, 6], [2648, 15, 1, 2, 4, 5, 6, 8, 9],
                                    [2035, 15, 1, 2, 4, 5, 6, 8, 9], [2036, 15, 1, 2, 4, 5, 6, 8, 10], [2649, 15, 1, 2, 4, 5, 6, 8, 9], [2051, 15, 1, 2, 4, 5, 6, 8, 9], [2052, 15, 1, 2, 4, 5, 6], [2053, 15, 1, 2, 4, 5, 6, 8, 9], [2054, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2355, 15, 1, 2, 4, 5, 6, 8, 9], [2650, 15, 1, 2, 4, 5, 6, 8, 9, 10],
                                    [2651, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2058, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2059, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2652, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2060, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2061, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2062, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2063, 15, 1, 2, 4, 5, 6, 8, 9, 10],
                                    [2653, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2066, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2067, 15, 1, 2, 4, 5, 6, 8, 9, 10], [2085, 15, 1, 3, 5, 6], [2086, 15, 1, 3, 5, 6], [2087, 15, 1, 3, 5, 6], [2088, 15, 1, 4, 5, 6], [2089, 15, 1, 2, 4, 5, 6], [2090, 15, 1, 2, 4, 5, 6], [2091, 15, 1, 2, 4, 5, 6],
                                    [2335, 15, 1, 4, 5, 6], [2336, 15, 1, 4, 5, 6]]
        else:
            item_logic_chunk[20] = [[1968, 15, 0, 4, 5, 6], [1969, 15, 0, 4, 5, 6], [1970, 15, 0, 4, 5, 6], [1971, 15, 0, 4, 5, 6], [1972, 15, 0, 4, 5, 6], [1973, 15, 0, 4, 5, 6], [1974, 15, 0, 4, 5, 6], [2008, 15, 0, 4, 5, 6], [2009, 15, 0, 4, 5, 6], [2010, 15, 0, 4, 5, 6], [2016, 15, 2, 4, 5, 6],
                                    [2017, 15, 2, 4, 5, 6], [2018, 15, 2, 4, 5, 6], [2019, 15, 2, 4, 5, 6], [2020, 15, 2, 4, 5, 6], [2021, 15, 2, 4, 5, 6], [2022, 15, 2, 4, 5, 6], [2023, 15, 2, 4, 5, 6], [2644, 15, 2, 4, 5, 6], [2645, 15, 2, 4, 5, 6], [2646, 15, 2, 4, 5, 6, 8, 9], [2024, 15, 2, 4, 5, 6],
                                    [2025, 15, 2, 4, 5, 6], [2026, 15, 2, 4, 5, 6], [2027, 15, 2, 4, 5, 6], [2028, 15, 2, 4, 5, 6], [2029, 15, 2, 4, 5, 6], [2030, 15, 2, 4, 5, 6, 8, 9], [2031, 15, 2, 4, 5, 6], [2647, 15, 2, 4, 5, 6], [2648, 15, 2, 4, 5, 6, 8, 9], [2035, 15, 2, 4, 5, 6, 8, 9], [2036, 15, 2, 4, 5, 6, 8, 10],
                                    [2649, 15, 2, 4, 5, 6, 8, 9], [2051, 15, 2, 4, 5, 6, 8, 9], [2052, 15, 2, 4, 5, 6], [2053, 15, 2, 4, 5, 6, 8, 9], [2054, 2, 4, 5, 6, 8, 9, 10], [2355, 15, 2, 4, 5, 6, 8, 9], [2650, 15, 2, 4, 5, 6, 8, 9, 10], [2651, 15, 2, 4, 5, 6, 8, 9, 10], [2058, 15, 2, 4, 5, 6, 8, 9, 10],
                                    [2059, 15, 2, 4, 5, 6, 8, 9, 10], [2652, 15, 2, 4, 5, 6, 8, 9, 10], [2060, 15, 2, 4, 5, 6, 8, 9, 10], [2061, 15, 2, 4, 5, 6, 8, 9, 10], [2062, 15, 2, 4, 5, 6, 8, 9, 10], [2063, 15, 2, 4, 5, 6, 8, 9, 10], [2653, 15, 2, 4, 5, 6, 8, 9, 10], [2066, 15, 2, 4, 5, 6, 8, 9, 10],
                                    [2067, 15, 2, 4, 5, 6, 8, 9, 10], [2085, 15, 0, 3, 5, 6], [2086, 15, 0, 3, 5, 6], [2087, 15, 0, 3, 5, 6], [2088, 15, 0, 4, 5, 6], [2089, 15, 2, 4, 5, 6], [2090, 15, 2, 4, 5, 6], [2091, 15, 2, 4, 5, 6], [2335, 15, 0, 4, 5, 6], [2336, 15, 0, 4, 5, 6]]

        if settings[1][0] == 0:
            item_logic_chunk[21] = [[2138, 15, 27, 1, 3, 5, 6], [2139, 15, 27, 1, 3, 5, 6], [2140, 15, 27, 1, 3, 5, 6], [2141, 15, 27, 1, 3, 5, 6], [2142, 15, 27, 1, 3, 5, 6], [2143, 15, 27, 1, 3, 5, 6], [2144, 15, 27, 1, 3, 5, 6], [2145, 15, 27, 1, 3, 5, 6], [2146, 15, 27, 1, 3, 5, 6], [2147, 15, 27, 1, 3, 5, 6],
                                    [2203, 15, 27, 1, 3, 5, 6], [2204, 15, 27, 1, 3, 5, 6], [2205, 15, 27, 1, 3, 5, 6], [2206, 15, 27, 1, 3, 5, 6], [2207, 15, 27, 1, 3, 5, 6], [2208, 15, 27, 1, 3, 5, 6], [2209, 15, 27, 1, 3, 5, 6], [2210, 15, 27, 1, 3, 5, 6], [2211, 15, 27, 1, 3, 5, 6], [2356, 15, 27, 1, 3, 5, 6],
                                    [2212, 15, 27, 1, 3, 5, 6], [2215, 15, 27, 1, 3, 5, 6], [2216, 15, 27, 1, 3, 5, 6], [2217, 15, 27, 1, 3, 5, 6], [2218, 15, 27, 1, 3, 5, 6], [2357, 15, 27, 1, 3, 5, 6], [2220, 15, 27, 1, 3, 5, 6], [2230, 15, 27, 1, 3, 5, 6], [2231, 15, 27, 1, 4, 5, 6], [2232, 15, 27, 1, 4, 5, 6],
                                    [2239, 15, 27, 1, 4, 5, 6], [2245, 15, 27, 1, 4, 5, 6], [2246, 15, 27, 1, 4, 5, 6], [2247, 15, 27, 1, 4, 5, 6], [2273, 15, 27, 1, 4, 5, 6, 7, 8, 10, 12, 13], [2274, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2275, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13],
                                    [2276, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2277, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2382, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2293, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2294, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2295, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13]]
        else:
            item_logic_chunk[21] = [[2138, 15, 27, 3, 5, 6], [2139, 15, 27, 3, 5, 6], [2140, 15, 27, 3, 5, 6], [2141, 15, 27, 3, 5, 6], [2142, 15, 27, 3, 5, 6], [2143, 15, 27, 3, 5, 6], [2144, 15, 27, 3, 5, 6], [2145, 15, 27, 3, 5, 6], [2146, 15, 27, 3, 5, 6], [2147, 15, 27, 3, 5, 6], [2203, 15, 27, 3, 5, 6],
                                    [2204, 15, 27, 3, 5, 6], [2205, 15, 27, 3, 5, 6], [2206, 15, 27, 3, 5, 6], [2207, 15, 27, 3, 5, 6], [2208, 15, 27, 3, 5, 6], [2209, 15, 27, 3, 5, 6], [2210, 15, 27, 3, 5, 6], [2211, 15, 27, 3, 5, 6], [2356, 15, 27, 0, 3, 5, 6], [2212, 15, 27, 0, 3, 5, 6], [2215, 15, 27, 0, 3, 5, 6],
                                    [2216, 15, 27, 0, 3, 5, 6], [2217, 15, 27, 0, 3, 5, 6], [2218, 15, 27, 0, 3, 5, 6], [2357, 15, 27, 0, 3, 5, 6], [2220, 15, 27, 0, 3, 5, 6], [2230, 15, 27, 0, 3, 5, 6], [2231, 15, 27, 0, 4, 5, 6], [2232, 15, 27, 0, 4, 5, 6], [2239, 15, 27, 0, 4, 5, 6],
                                    [2245, 15, 27, 0, 4, 5, 6], [2246, 15, 27, 0, 4, 5, 6], [2247, 15, 27, 0, 4, 5, 6], [2273, 15, 27, 0, 4, 5, 6, 7, 8, 10, 12, 13], [2274, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2275, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2276, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13],
                                    [2277, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2382, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2293, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2294, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13], [2295, 15, 27, 0, 4, 5, 6, 7, 8, 9, 10, 12, 13]]

        if settings[1][0] == 0 and settings[1][1] == 0:
            item_logic_chunk[22] = [[1526, 15, 22, 1, -1, 15, 22, 5], [297, 15, 16, 17, 1, -1, 15, 16, 1, 5], [298, 15, 16, 17, 1, -1, 15, 16, 1, 5], [299, 15, 16, 17, 1, -1, 15, 16, 1, 5], [300, 15, 16, 17, 1, -1, 15, 16, 1, 5], [301, 15, 16, 17, 1, -1, 15, 16, 1, 5], [302, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                                    [2654, 15, 22, 1, 4, 5, 6], [758, 15, 22, 1, 4, 5, 6], [759, 15, 22, 1, 4, 5, 6]]
        elif settings[1][0] == 1 and settings[1][1] == 1:
            item_logic_chunk[22] = [[1526, 15, 22, 1, -1, 15, 22, 5], [297, 15, 16, 17, 1], [298, 15, 16, 17, 1], [299, 15, 16, 17, 1], [300, 15, 16, 17, 1], [301, 15, 16, 17, 1], [302, 15, 16, 17, 1], [2654, 15, 22, 1, 4, 5, 6], [758, 15, 22, 1, 4, 5, 6], [759, 15, 22, 1, 4, 5, 6]]
        elif settings[1][1] == 1:
            item_logic_chunk[22] = [[1526, 15, 22, 1, -1, 15, 22, 5], [297, 15, 16, 17, 1], [298, 15, 16, 17, 1], [299, 15, 16, 17, 1], [300, 15, 16, 17, 1], [301, 15, 16, 17, 1], [302, 15, 16, 17, 1], [2654, 15, 22, 1, 4, 5, 6], [758, 15, 22, 1, 4, 5, 6], [759, 15, 22, 1, 4, 5, 6]]
        else:
            item_logic_chunk[22] = [[1526, 15, 22, 1, -1, 15, 22, 5], [297, 15, 16, 17, 1, -1, 15, 16, 1, 5], [298, 15, 16, 17, 1, -1, 15, 16, 1, 5], [299, 15, 16, 17, 1, -1, 15, 16, 1, 5], [300, 15, 16, 17, 1, -1, 15, 16, 1, 5], [301, 15, 16, 17, 1, -1, 15, 16, 1, 5], [302, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                                    [2654, 15, 22, 1, 4, 5, 6], [758, 15, 22, 1, 4, 5, 6], [759, 15, 22, 1, 4, 5, 6]]
        pbar.update(10)

        item_logic = []
        for c in range(len(item_logic_chunk)):
            for l in range(len(item_logic_chunk[c])):
                item_logic.append(item_logic_chunk[c][l])
                pbar.update(1)

        #for item in range(len(item_logic)):
        #    if item_locals[item][6] == item_logic[item][0]:
        #        print(item_locals[item][6])

        #Creates an item pool for the key items
        key_item_pool = [[0xE002, 0], [0xE002, 1], [0xE002, 2], [0xE004, 3], [0xE004, 4], [0xE005, 5], [0xE00A, 6], [0xE00D, 7],
                         [0xE00E, 8], [0xE00F, 9], [0xE010, 10], [0xE011, 11], [0xE012, 12], [0xE013, 13], [0xE075, 14], [0xC369, 15],
                         [0xCABF, 16], [0xE0A0, 17], [0xC343, 18], [0xC344, 19], [0xC345, 20], [0xC346, 21], [0xC960, 22], [0xC3B9, 23],
                         [0xB0F7, 24], [0xB0F7, 25], [0xB0F7, 26], [0xC47E, 27]]

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
        logic_logic = [[0], [1, 0], [2, 1], [3], [4, 15, 16, 3, -1, 23, 1, 3, -1, 1, 3, 5], [5], [6], [7, 6], [8, 6], [9, 6], [10, 15, 3, 6, -1, 23, 1, 3, 6], [11, 10],
                       [12, 7], [13, 7], [14], [15], [16, 15], [17, 15, 16], [18, 15, 16], [19, 15, 16], [20, 15, 16], [21, 15, 16], [22, 15], [23, 1],
                       [24, 1, 3, 6], [25, 24], [26, 25], [27, 15, 1]]
        pbar.update(2)

        #Removes items from the key item pool depending on the settings
        for l in range(len(settings)):
            if settings[0][l] == 1.0:
                s = find_index_in_2d_list(key_item_pool, l)
                key_item_check[s[0]] += 1
                del key_item_pool[s[0]]
                del logic_logic[s[0]]
                pbar.update(1)

    with tqdm(total=len(item_pool)+len(key_item_pool)+(len(attack_piece_pool[0])*len(attack_piece_pool)), desc="Randomizing...") as rbar:
        new_item_locals = []

        #[Trigger type, Room ID, X Pos, Y Pos, Z Pos, Collectible/Cutscene ID, Ability/Item/Key Item/Attack(, Attack Piece ID/Coin Amount/Item Cutscene/Hammer or Spin Cutscene, Coin Cutscene)]
        repack_data = []
        i = 0
        itemcut = 0
        attackcut = 0
        key_item_pool_checked = []
        new_enemy_stats = []
        attack = random.randint(0, len(attack_piece_pool) - 1)

        while len(item_pool) + len(key_item_pool) + len(attack_piece_pool) > 0:
            prevlen = len(item_pool) + len(key_item_pool) + len(attack_piece_pool)
            while i < len(item_logic):
                if len(item_logic) > 0:
                    if is_available(item_logic[i], key_item_check, settings):
                        rand_array = random.randint(0, 3)
                        if rand_array < 3 and len(item_pool) > 0:
                            #Code for randomizing blocks and bean spots with just eachother
                            nitem = random.randint(0, len(item_pool) - 1)
                            narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], item_pool[nitem][1],
                                        item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                            new_item_locals.append(narray)
                            del item_pool[nitem]
                            del item_locals[i]
                            del item_logic[i]
                        elif len(attack_piece_pool) > 0:
                            #Code for putting attacks in blocks and bean spots
                            if len(attack_piece_pool[attack]) == 0:
                                del attack_piece_pool[attack]
                                if len(attack_piece_pool) > 0:
                                    attack = random.randint(0, len(attack_piece_pool) - 1)
                            if len(attack_piece_pool) > 0:
                                nitem = random.randint(0, len(attack_piece_pool[attack]) - 1)
                                narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], 0,
                                        item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                                new_item_locals.append(narray)
                                spottype = get_spot_type(item_locals[i])
                                repack_data.append([spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6] + 0xD000,
                                                    attack_piece_pool[attack][nitem][1], attack_piece_pool[attack][nitem][0], 0xCD20 + attackcut])
                                attackcut += 1
                                del attack_piece_pool[attack][nitem]
                                del item_locals[i]
                                del item_logic[i]
                        i -= 1
                        rbar.update(1)
                    i += 1
            #Checks if more items can be randomized
            if prevlen <= len(item_pool) + len(key_item_pool) + len(attack_piece_pool) and len(key_item_pool) > 0 and len(new_item_locals) > 0:
                if len(key_item_pool) > 0:
                    can_key = False
                    for i in range(len(new_item_locals)):
                        if new_item_locals[i][3] != 0 and find_index_in_2d_list(repack_data, new_item_locals[i][7] + 0xD000) is None:
                            can_key = True
                    if can_key:
                        old_spot = random.randint(0, len(new_item_locals) - 1)
                        while new_item_locals[old_spot][3] == 0:
                            old_spot = random.randint(0, len(new_item_locals) - 1)
                        item_locals.append([new_item_locals[old_spot][0], new_item_locals[old_spot][1],
                                            new_item_locals[old_spot][2], new_item_locals[old_spot][4],
                                            new_item_locals[old_spot][5], new_item_locals[old_spot][6],
                                            new_item_locals[old_spot][7]])
                        item_pool.append([new_item_locals[old_spot][2], new_item_locals[old_spot][3]])
                        i = -1

                        # Code for putting key items in blocks and bean spots
                        nitem = random.randint(0, len(key_item_pool) - 1)
                        while not is_available(logic_logic[key_item_pool[nitem][1]], key_item_check, settings):
                            nitem = random.randint(0, len(key_item_pool) - 1)
                        narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], 0,
                                  item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                        new_item_locals[old_spot] = narray
                        spottype = get_spot_type(item_locals[i])
                        if (key_item_pool[nitem][0] < 0xE000 or key_item_pool[nitem][0] > 0xE004) and key_item_pool[nitem][0] != 0xB0F7:
                            repack_data.append(
                                [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                                 item_locals[i][6] + 0xD000, key_item_pool[nitem][0]])
                        elif key_item_pool[nitem][0] != 0xE000:
                            repack_data.append(
                                [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                                 item_locals[i][6] + 0xD000, key_item_pool[nitem][0], 0xCDC0 + itemcut])
                            itemcut += 1
                        else:
                            repack_data.append(
                                [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                                 item_locals[i][6] + 0xD000, key_item_pool[nitem][0] + key_item_pool[nitem][1],
                                 0xCDC0 + itemcut])
                            itemcut += 1
                        key_item_check[key_item_pool[nitem][1]] += 1
                        key_item_pool_checked.append(key_item_pool[nitem])
                        del key_item_pool[nitem]
                        del item_locals[i]
                    else:
                        attack_spot = find_index_in_2d_list(repack_data, new_item_locals[0][7] + 0xD000)
                        while attack_spot is None:
                            r = random.randint(0, len(new_item_locals)-1)
                            attack_spot = find_index_in_2d_list(repack_data, new_item_locals[r][7] + 0xD000)
                        if attack_spot is not None:
                            if len(repack_data[attack_spot[0]]) > 7 and repack_data[attack_spot[0]][6] < 0xC000:
                                attack_piece_pool.append([repack_data[attack_spot[0]][7], repack_data[attack_spot[0]][6]])
                            else:
                                key_spot = find_index_in_2d_list(key_item_pool_checked, repack_data[attack_spot[0]][6])
                                if key_spot is not None:
                                    key_item_pool.append(key_item_pool_checked[key_spot[0]])
                                    del key_item_pool_checked[key_spot[0]]
                                    key_item_check[key_item_pool[-1][1]] -= 1
                            del repack_data[attack_spot[0]]
                        else:
                            item_pool.append([new_item_locals[0][2], new_item_locals[0][3]])
                        item_locals.append([new_item_locals[0][0], new_item_locals[0][1], new_item_locals[0][2],
                                            new_item_locals[0][4], new_item_locals[0][5], new_item_locals[0][6],
                                            new_item_locals[0][7]])
                        item_logic.append([0])
                        del new_item_locals[0]
            i = 0

            #Randomizes enemy stats
            while i < len(enemy_logic):
                if len(enemy_logic) > 0:
                    if is_available(enemy_logic[i], key_item_check, settings):
                        temp = enemy_stats_rand[i]
                        for n in range(len(enemy_stats_rand[0])-1):
                            enemy_stats_rand[i][n+1] = enemy_stats_rand[0][n+1]
                            for j in range(i-1):
                                enemy_stats_rand[j][n+1] = enemy_stats_rand[j+1][n+1]
                            if i > 0:
                                enemy_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(enemy_stats_rand[i])
                        if new_enemy_stats[-1][0] == 87:
                            new_enemy_stats[-1][5] //= 4
                            new_enemy_stats.append([88, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                    new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                    new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                    new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                            new_enemy_stats.append([89, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                    new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                    new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                    new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])

                        del enemy_stats_rand[i]
                        del enemy_logic[i]
                        i -= 1
                    i += 1
            i = 0
            while i < len(boss_logic):
                if len(boss_logic) > 0:
                    if is_available(boss_logic[i], key_item_check, settings):
                        temp = boss_stats_rand[i]
                        for n in range(len(boss_stats_rand[0])-1):
                            boss_stats_rand[i][n+1] = boss_stats_rand[0][n+1]
                            for j in range(i-1):
                                boss_stats_rand[j][n+1] = boss_stats_rand[j+1][n+1]
                            if i > 0:
                                boss_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(boss_stats_rand[i])
                        if new_enemy_stats[-1][0] == 107:
                            for j in range(5):
                                new_enemy_stats[-1][j+1] //= 2
                            new_enemy_stats.append([108, new_enemy_stats[-1][1], new_enemy_stats[-1][2], new_enemy_stats[-1][3],
                                                    new_enemy_stats[-1][4], new_enemy_stats[-1][5], new_enemy_stats[-1][6],
                                                    new_enemy_stats[-1][7], new_enemy_stats[-1][8], new_enemy_stats[-1][9],
                                                    new_enemy_stats[-1][10], new_enemy_stats[-1][11], new_enemy_stats[-1][12]])
                        elif new_enemy_stats[-1][0] == 17:
                            for j in range(5):
                                new_enemy_stats[-1][j+1] //= 4
                        del boss_stats_rand[i]
                        del boss_logic[i]
                        i -= 1
                    i += 1
            i = 0
            while i < len(dream_enemy_logic):
                if len(dream_enemy_logic) > 0:
                    if is_available(dream_enemy_logic[i], key_item_check, settings):
                        temp = dream_enemy_stats_rand[i]
                        for n in range(len(dream_enemy_stats_rand[0])-1):
                            dream_enemy_stats_rand[i][n+1] = dream_enemy_stats_rand[0][n+1]
                            for j in range(i-1):
                                dream_enemy_stats_rand[j][n+1] = dream_enemy_stats_rand[j+1][n+1]
                            if i > 0:
                                dream_enemy_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(dream_enemy_stats_rand[i])
                        del dream_enemy_stats_rand[i]
                        del dream_enemy_logic[i]
                        i -= 1
                    i += 1
            i = 0
            while i < len(dream_boss_logic):
                if len(dream_boss_logic) > 0:
                    if is_available(dream_boss_logic[i], key_item_check, settings):
                        temp = dream_boss_stats_rand[i]
                        for n in range(len(dream_boss_stats_rand[0])-1):
                            dream_boss_stats_rand[i][n+1] = dream_boss_stats_rand[0][n+1]
                            for j in range(i-1):
                                dream_boss_stats_rand[j][n+1] = dream_boss_stats_rand[j+1][n+1]
                            if i > 0:
                                dream_boss_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(dream_boss_stats_rand[i])
                        del dream_boss_stats_rand[i]
                        del dream_boss_logic[i]
                        i -= 1
                    i += 1
            i = 0
            while i < len(filler_logic):
                if len(filler_logic) > 0:
                    if is_available(filler_logic[i], key_item_check, settings):
                        temp = filler_stats_rand[i]
                        for n in range(len(filler_stats_rand[0])-1):
                            filler_stats_rand[i][n+1] = filler_stats_rand[0][n+1]
                            for j in range(i-1):
                                filler_stats_rand[j][n+1] = filler_stats_rand[j+1][n+1]
                            if i > 0:
                                filler_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(filler_stats_rand[i])
                        del filler_stats_rand[i]
                        del filler_logic[i]
                        i -= 1
                    i += 1
            i = 0

            #Swaps a coin with whatever is left in the item pool
            if (len(item_pool) > 0 or len(attack_piece_pool) > 0) and len(item_logic) == 0:
                item = 0
                while new_item_locals[item][3] != 0 or find_index_in_2d_list(repack_data, new_item_locals[item][7] + 0xD000) is not None:
                    item += 1
                    if item == len(new_item_locals):
                        item -= 1
                        break
                item_locals.append([new_item_locals[item][0], new_item_locals[item][1], new_item_locals[item][2], new_item_locals[item][4], new_item_locals[item][5], new_item_locals[item][6], new_item_locals[item][7]])
                item_logic.append([0])
                del new_item_locals[item]

    #hammer_local = find_index_in_2d_list(repack_data, 0xC369)
    #print(repack_data[hammer_local[0]])

    print("Generating spoiler log...")
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
                        "Buildup 1", "Wiggler and Popple Arena", "Bedsmith Basement", "Rock Frame Room", "Ball Hop Tutorial Room", "Massif Lobby", "Massif Hooraw Main Room"]

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
    key_item_names = ["Progressive Hammers", "Progressive Hammers", "Progressive Hammers", "Progressive Spin", "Progressive Spin", "Ball Hop", "Luiginary Works", "Luiginary Ball", "Luiginary Stack High Jump",
                      "Luiginary Stack Ground Pound", "Luiginary Cone Jump", "Luiginary Cone Storm", "Luiginary Ball Hookshot", "Luiginary Ball Throw", "Deep Pi'illo Castle", "Blimport Bridge", "Mushrise Park Gate",
                      "First Dozite", "Dozite 1", "Dozite 2", "Dozite 3", "Dozite 4", "Access to Wakeport", "Access to Mount Pajamaja", "Dream Egg 1", "Dream Egg 2", "Dream Egg 3", "Access to Neo Bowser Castle"]

    #Names for attack pieces
    attack_piece_names = ["Mushrise Park", "Dreamy Mushrise Park", "Dozing Sands", "Dreamy Dozing Sands", "Wakeport", "Mount Pajamaja", "Dreamy Mount Pajamaja", "Driftwood Shore", "Dreamy Driftwood Shore",
                          "Mount Pajamaja Summit", "Dreamy Wakeport", "Somnom Woods", "Dreamy Somnom Woods", "Mushrise Park Caves", "Neo Bowser Castle"]

    #Names for the different kinds of checks
    check_names = ["Block", "Block", "Rotated Block", "Mini Mario Block", "High Up Block", "Bean Spot", "Key Item Spot", "Attack Piece Block", "Rotated Block", "Rotated Block"]

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
                rooms = []
                rooms.append(new_item_locals[i])
        else:
            rooms.append(new_item_locals[i])

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
    room_check = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
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
        number = str(room_check[new_item_locals[s][0]][get_spot_type(new_item_locals[s])])
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
                item += " Attack Piece " + str(((repack_data[k[0]][7] // 2) + 1) * ((repack_data[k[0]][6] + offset) % 2 + 1))
            else:
                item = key_item_names[key_item_pool_checked[ab[0]][1]]
        if new_item_locals[s][0] < len(item_local_names):
            room_name = item_local_names[new_item_locals[s][0]]
        else:
            room_name = hex(new_item_locals[s][0])
        spoiler_log.write(room_name + " " + check_type + " " + number + " - " + item + "\n")

    print("Repacking enemy stats...")
    #Repackages randomized enemy stats
    for enemy in range(len(new_enemy_stats)):
        enemy_stats[new_enemy_stats[enemy][0]].hp = new_enemy_stats[enemy][1]
        enemy_stats[new_enemy_stats[enemy][0]].power = new_enemy_stats[enemy][2]
        enemy_stats[new_enemy_stats[enemy][0]].defense = new_enemy_stats[enemy][3]
        enemy_stats[new_enemy_stats[enemy][0]].speed = new_enemy_stats[enemy][4]
        enemy_stats[new_enemy_stats[enemy][0]].exp = new_enemy_stats[enemy][5]
        enemy_stats[new_enemy_stats[enemy][0]].coins = new_enemy_stats[enemy][6]
        enemy_stats[new_enemy_stats[enemy][0]].coin_rate = new_enemy_stats[enemy][7]
        enemy_stats[new_enemy_stats[enemy][0]].item_chance = new_enemy_stats[enemy][8]
        enemy_stats[new_enemy_stats[enemy][0]].item_type = new_enemy_stats[enemy][9]
        enemy_stats[new_enemy_stats[enemy][0]].rare_item_chance = new_enemy_stats[enemy][10]
        enemy_stats[new_enemy_stats[enemy][0]].rare_item_type = new_enemy_stats[enemy][11]
        enemy_stats[new_enemy_stats[enemy][0]].level = new_enemy_stats[enemy][12]
        #print(new_enemy_stats[enemy])
    #Packs enemy stats
    save_enemy_stats(enemy_stats, code_bin=code_bin_path)

    print("Repacking FMap...")
    newlen = 0
    check_spot = []
    for b in range(len(new_item_locals)):
        if b > 0:
            if new_item_locals[b-1][0] != new_item_locals[b][0]:
                if newlen > 0:
                    for j in range(newlen):
                        i = 0
                        while parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+10:i*12+12] != check_spot[j][0].to_bytes(2, 'little') and i < len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7])/12:
                            i += 1
                        #print(int.from_bytes(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+10:i*12+12], "little"))
                        #print(len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][0:i*12] + parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+12:len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7])])/12)
                        parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7] = parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][0:i*12] + parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7][i*12+12:len(parsed_fmapdat[new_item_locals[check_spot[j][1]][0]][7])]
                    newlen = 0
                    check_spot = []
        x = 0
        while x < len(repack_data):
            if repack_data[x][5] == new_item_locals[b][-1] + 0xD000 and (repack_data[x][0] == 0 or repack_data[x][0] == 1):
                newlen += 1
                check_spot.append([new_item_locals[b][7], b])
                break
            x += 1
        i = 0
        while parsed_fmapdat[new_item_locals[b][0]][7][i*12+10:i*12+12] != new_item_locals[b][7].to_bytes(2, 'little'):
            i += 1
        parsed_fmapdat[new_item_locals[b][0]][7][i*12:i*12+12] = struct.pack('<HHHHHH', *new_item_locals[b][2:8])

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
        code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16)
        code_bin.write(fmapdat_offset_table)
        code_bin.seek(FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16)
        code_bin.write(fmapdat_offset_table)

    randomize_repack.pack(input_folder, repack_data, settings)

#randomize_data(input_folder, stat_mult)
