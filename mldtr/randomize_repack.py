from mnlscript.tools.decompiler.dt.command_matchers import join_thread
from pymsbmnl import LMSDocument, msbt_from_file
from mnllib.n3ds import fs_std_romfs_path
from mnllib import Subroutine, RawDataCommand, CodeCommand, Variable
from mnllib.dt import FEventScriptManager, FMES_NUMBER_OF_CHUNKS, MESSAGE_DIR_PATH, DTLMSAdapter, read_msbt_archive, write_msbt_archive
from mnlscript import CodeCommandWithOffsets, emit_command, update_commands_with_offsets, Screen, label, \
    SubroutineExt
from mnlscript.dt import PLACEHOLDER_OFFSET, Variables, change_room, MusicFlag, set_action_icons_shown, \
    set_actor_attribute, Actors, tint_screen, set_blocked_buttons, ButtonFlags, set_movement_multipliers, \
    set_touches_blocked, branch_if, TextboxSoundsPreset, say, wait, Globals, call, branch, TextboxAlignment, \
    add_in_place, start_battle, WorldType, Transition, Sound, TextboxTailType, ActorAttribute, Variable
from typing import cast
from tqdm import tqdm
import math
import functools
import inspect
import mnlscript

# Workaround for dynamic scope in Nuitka
def subroutine(*args, **kwargs):
    def decorator(function):
        @mnlscript.subroutine(*args, **kwargs)
        @functools.wraps(function)
        def subroutine(sub: Subroutine):
            if '__compiled__' in globals():
                inspect.currentframe().f_locals['sub'] = sub
            function(sub=sub)
        return subroutine
    return decorator

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

def get_dream_origin(room):
    if 0x1E <= room <= 0x2B or 0x2D <= room <= 0x2F or 0xF1 <= room <= 0xF3 or room == 0x19A or room == 0x1CD or room == 0x1CE:
        return [0x00B, 0xA0]
    elif room == 0x02C:
        return [0x001, 0x8D]
    elif room == 0x030:
        return [0x003, 0x69]
    elif room == 0x031 or room == 0x19B:
        return [0x141, 0x6A]
    elif room == 0x032 or room == 0x199:
        return [0x008, 0x75]
    elif room == 0x09D or room == 0x19A:
        return [0x004, 0x120]
    elif 0x0A2 <= room <= 0x0AA or 0x0F4 <= room <= 0x0FA:
        return [0x097, 0x66]
    elif 0x0AC <= room <= 0x0AE:
        return [0x13A, 0x6C]
    elif room == 0x0B1 or 0x13C <= room <= 0x13E:
        return [0x012, 0x104]
    elif 0x0B2 <= room <= 0x0B4 or room == 0x1D6:
        return [0x28C, 0x97]
    elif room == 0x0B5:
        return [0x019, 0x11E]
    elif room == 0x0B6:
        return [0x1DC, 0x8D]
    elif 0x0B7 <= room <= 0x0B9:
        return [0x101, 0x72]
    elif 0x0BA <= room <= 0x0C7 or 0x0E4 <= room <= 0x0E6:
        return [0x102, 0x53]
    elif 0x0D2 <= room <= 0x0D6 or 0x161 <= room <= 0x172 or room == 0x1C9 or room == 0x1CA:
        return [0x03A, 0x10D]
    elif 0x0D8 <= room <= 0x0DA:
        return [0x13B, 0x82]
    elif 0x0DB <= room <= 0x0DE:
        return [0x13A, 0x6B]
    elif 0x0E7 <= room <= 0x0EA:
        return [0x104, 0x89]
    elif room == 0x0EB:
        return [0x05D, 0x50]
    elif room == 0x0EC:
        return [0x019, 0x120]
    elif room == 0x0ED:
        return [0x060, 0x7E]
    elif room == 0x0EE:
        return [0x013, 0x124]
    elif room == 0x0EF or room == 0x292:
        return [0x061, 0x5D]
    elif room == 0x0F0 or room == 0x293:
        return [0x103, 0x7C]
    elif 0x0FB <= room <= 0x0FD or 0x224 <= room <= 0x233:
        return [0x29D, 0x6B]
    elif room == 0x106 or 0x10D <= room <= 0x122:
        return [0x288, 0x7E]
    elif 0x123 <= room <= 0x12C or room == 0x1CF or room == 0x1E1 or room == 0x294 or room == 0x295:
        return [0x10A, 0x78]
    elif room == 0x12D:
        return [0x039, 0x127]
    elif room == 0x12E or room == 0x12F:
        return [0x035, 0x11E]
    elif room == 0x130:
        return [0x036, 0x10F]
    elif room == 0x131 or room == 0x132:
        return [0x109, 0x90]
    elif room == 0x133 or room == 0x134:
        return [0x109, 0x91]
    elif room == 0x13F or room == 0x1E7:
        return [0x068, 0x64]
    elif 0x173 <= room <= 0x177:
        return [0x03B, 0x116]
    elif 0x178 <= room <= 0x17A:
        return [0x04F, 0x109]
    elif 0x17B <= room <= 0x17D:
        return [0x04C, 0x107]
    elif room == 0x17E:
        return [0x038, 0x121]
    elif 0x17F <= room <= 0x181:
        return [0x03A, 0x10E]
    elif room == 0x182:
        return [0x048, 0x63]
    elif room == 0x1E8:
        return [0x068, 0x65]
    elif 0x1E9 <= room <= 0x1EB:
        return [0x077, 0x7C]
    elif room == 0x1EC or room == 0x1ED:
        return [0x077, 0x7B]
    elif 0x1EE <= room <= 0x204:
        return [0x07F, 0x58]
    elif 0x205 <= room <= 0x207:
        return [0x10B, 0x6A]
    elif room == 0x209 or room == 0x20A:
        return [0x06E, 0x4C]
    elif room == 0x20C or room == 0x20D:
        return [0x072, 0x111]
    elif room == 0x20E:
        return [0x06A, 0xF9]
    elif room == 0x219:
        return [0x189, 0x12A]
    elif 0x21A <= room <= 0x21C:
        return [0x18B, 0x12A]
    elif room == 0x21D or room == 0x21E:
        return [0x18D, 0x104]
    elif room == 0x21F or room == 0x220:
        return [0x190, 0x123]
    elif room == 0x221 or room == 0x222:
        return [0x191, 0x76]
    elif room == 0x223:
        return [0x193, 0x6A]
    elif room == 0x234:
        return [0x18A, 0x10A]
    elif room == 0x235:
        return [0x189, 0x12D]
    elif room == 0x236:
        return [0x18F, 0x105]
    elif room == 0x237:
        return [0x18F, 0x106]
    elif room == 0x238:
        return [0x186, 0x84]
    elif room == 0x250 or room == 0x280:
        return [0x076, 0xFC]
    elif 0x252 <= room <= 0x259:
        return [0x144, 0x133]
    elif 0x25A <= room <= 0x25E:
        return [0x14D, 0xB6]
    elif 0x25F <= room <= 0x263:
        return [0x151, 0x7D]
    elif 0x264 <= room <= 0x267:
        return [0x157, 0x68]
    elif 0x268 <= room <= 0x26A:
        return [0x157, 0x67]
    elif 0x26B <= room <= 0x26D or room == 0x28F:
        return [0x157, 0x69]
    elif 0x26E <= room <= 0x27B:
        return [0x15D, 0x5B]
    else:
        return [-1, -1]

def find_index_in_2d_list(arr, target_value, index):
    for row in range(len(arr)):
        if arr[row][index] == target_value:
            return row
    return None  # Return None if the element is not found

def find_every_index_in_2d_list(arr, target_value, index):
    indexes = []
    for row in range(len(arr)):
        if arr[row][index] == target_value:
            indexes.append(row)
    return indexes

def pack(input_folder, repack_data, settings, new_item_locals, new_item_logic, key_item_pool_checked):
    with tqdm(total=65, desc="Setting up FEvent...") as sbar:
        #Sets up the FEvent to be read
        fevent_manager = FEventScriptManager(input_folder)

        #Allows editing of FMes
        message_dir = fs_std_romfs_path(MESSAGE_DIR_PATH, data_dir=input_folder)
        for message_file_path in sorted(message_dir.glob("*/FMes.dat")):
            language = message_file_path.parent.name
            with (
                message_file_path.open("rb") as message_file,
                message_file_path.with_suffix(".bin").open("rb") as offset_table,
            ):
                Globals.text_chunks[language] = dict(
                    enumerate(read_msbt_archive(message_file, offset_table, language))
                )

        #Import the msbt for the item names
        try:
            item_name_path = next(fs_std_romfs_path(MESSAGE_DIR_PATH, data_dir=input_folder).glob('*_English'))
        except StopIteration:
            item_name_path = next(fs_std_romfs_path(MESSAGE_DIR_PATH, data_dir=input_folder).iterdir())
        item_name_path /= 'Item.msbt'
        item_msgs = msbt_from_file(lambda: DTLMSAdapter(MESSAGE_DIR_PATH), fs_std_romfs_path(item_name_path, data_dir=input_folder))
        sbar.update(10)

        #Initializes the first room using the subroutine below
        script = fevent_manager.parsed_script(0x028C, 0)
        script.subroutines[0x26].commands[1] = CodeCommandWithOffsets(0x0003, [0x01, PLACEHOLDER_OFFSET], offset_arguments={1: 'assign_variables'})

        #Subroutine for the first room
        @subroutine(subs=script.subroutines, hdr=script.header)
        def assign_variables(sub: Subroutine):
            Variables[0xCC10] = 1.0 #Skips Luigi's panicking
            Variables[0xCC4C] = 1.0 #Save Tutorial
            Variables[0xCC11] = 1.0 #Check-X Quiz
            Variables[0xC5C9] = 1.0 #Hurry With Zee Quickness
            Variables[0xCC1B] = 1.0 #First Gromba Fight
            Variables[0xCC1D] = 1.0 #Second Gromba Fight
            Variables[0xCC1E] = 1.0 #Reuniting with Luigi
            Variables[0xCC1F] = 1.0 #Meet Starlow for First Time
            Variables[0xCC24] = 1.0 #Your sightseeing is finished
            Variables[0xCA53] = 1.0 #Opens gate to platform room
            Variables[0xE016] = 1.0 #Unlocks access to the pause menu
            Variables[0xCC25] = 1.0 #Watched Backstory for Pi'illo Island
            Variables[0xCC26] = 1.0 #Rode platform into deep Pi'illo Castle
            Variables[0xCC39] = 1.0 #Watched smoldergeist intro
            Variables[0xCC87] = 1.0 #Watched smoldergeist intro
            Variables[0xE01C] = 1.0 #Allows items in battle
            Variables[0xCC3A] = 1.0 #Watched jump tutorial
            Variables[0xCC3E] = 1.0 #First Smoldergeist Minigame
            Variables[0xCC41] = 1.0 #Second Smoldergeist Minigame
            Variables[0xCC45] = 1.0 #Grombas circle cutscene
            Variables[0xCA35] = 1.0 #Grombas circle flag 1
            Variables[0xCA36] = 1.0 #Grombas circle flag 2
            Variables[0xCC47] = 1.0 #Final Smoldergeist Minigame
            Variables[0xCC48] = 1.0 #Peach is in danger... again!
            Variables[0xCC27] = 1.0 #Got badges and watched tutorial
            Variables[0xE01D] = 1.0 #Gives access to badges and expert challenges
            Variables[0xCCCC] = 1.0 #Smoldergeist expert challenge tutorial
            #Variables[0x9015] = 1.0 #Fixes bridge in Deep Pi'illo Castle
            Variables[0xC5CA] = 1.0 #How did you come OUT of the hidden area!?
            Variables[0xCC29] = 1.0 #First entered collection room
            Variables[0xCC2A] = 1.0 #Swim to Dream World
            Variables[0xCB01] = 1.0 #Landed in Dream World for first time
            Variables[0xCB02] = 1.0 #Antasma flies away with Peach
            Variables[0xCB03] = 1.0 #Monsieur explains how a door works
            Variables[0xCB04] = 1.0 #Monsieur offers to help with the maze
            Variables[0xCB00] = 1.0 #Mario and Dreamy Luigi meet
            Variables[0xCB06] = 1.0 #Bros chase after Peach again
            Variables[0xCB05] = 1.0 #Dromba battled
            Variables[0x9010] = 1.0 #Dromba bridge is up
            #Variables[0xCB07] = 1.0 #Final Dreamy Castle cutscene
            Variables[0xCB08] = 1.0 #Dreambert is revived
            Variables[0xCC2B] = 1.0 #Dreambert awakes
            Variables[0xCC2C] = 1.0 #Dreambert runs out of castle cutscene
            Variables[0xCC2D] = 1.0 #"There are many sights" cutscene
            Variables[0xCC2E] = 1.0 #Blimport bridge collapses
            wait(3)
            Variables[0xCC2F] = 1.0 #Mario falls on Luigi
            Variables[0xCC30] = 1.0 #See first Pi'illo
            Variables[0xCB2F] = 1.0 #First entered first Pi'illo
            Variables[0xCB2E] = 1.0 #First Luiginary work cutscene
            Variables[0xCB2D] = 1.0 #Also set with first Luiginary work
            Variables[0xCB49] = 1.0 #First Luiginary work cutscene part 2
            Variables[0xCB31] = 1.0 #First nightmare chunk of first Pi'illo
            Variables[0xCB0C] = 1.0 #Part of cutscene above
            Variables[0xCC32] = 1.0 #Second Pi'illo has already been entered (fixes loading zone)
            Variables[0xCB0E] = 1.0 #Tutorial for nightmare chunk counter
            Variables[0xCB33] = 1.0 #Doors close for Luiginary sneeze tutorial
            Variables[0xCB10] = 1.0 #Luiginary sneeze tutorial
            Variables[0xCC31] = 1.0 #First Pi'illo saved, can access Pi'illo folk in collection
            Variables[0xCC33] = 1.0 #Second Pi'illo under bridge is saved
            Variables[0xCC37] = 1.0 #Third Pi'illo under bridge is saved
            Variables[0xCABD] = 1.0 #Shell Hutch Tutorial
            Variables[0xC300] = 1.0 #First Boss Brickle cutscene watched
            Variables[0xC322] = 1.0 #Flowers are down
            Variables[0xC302] = 1.0 #Picked up hammers
            Variables[0xC323] = 1.0 #First feather obtained
            Variables[0xC95C] = 1.0 #Second feather obtained
            Variables[0xC305] = 1.0 #Flowers are in bloom
            Variables[0xC302] = 1.0 #Key Items is in Pause Menu
            Variables[0xC90A] = 1.0 #Saved Toad from Thorbs
            Variables[0xE01A] = 1.0 #Unlock Bros Attacks
            Variables[0xC938] = 1.0 #Capnap tutorial
            Variables[0xC939] = 1.0 #Capnap tutorial 2
            Variables[0xC93A] = 1.0 #Capnap tutorial 3?
            Variables[0xC306] = 1.0 #Boss Brickle gets stuck in fountain
            Variables[0xC952] = 1.0 #First entered pipeworks
            Variables[0xC953] = 1.0 #Fountain minigame started
            Variables[0xC30D] = 1.0 #Fountain minigame ended
            Variables[0xC30E] = 1.0 #Boss Brickle is saved
            Variables[0xC30C] = 1.0 #Boss Brickle is saved
            Variables[0xC92E] = 1.0 #Boss Brickle under attack cutscene
            #Variables[0xC954] = 1.0 #Grobot Battle Start
            #Variables[0xC92F] = 1.0 #Grobot Defeated
            Variables[0xC930] = 1.0 #Cutscene before entering Eldream's pillow
            wait(3)
            Variables[0xC000] = 1.0 #Eldream Dream World Enter
            Variables[0xC001] = 1.0 #Boss Brickle declares you his rivals
            Variables[0xC028] = 1.0 #Boss Brickle declares you his rivals
            Variables[0xC003] = 1.0 #Boss Brickle thinks he needs a bigger carrot
            Variables[0xC010] = 1.0 #Boss Brickle wants to water the plants, but can't
            Variables[0xC011] = 1.0 #Brickle explains how to activate the water pump
            Variables[0xC00B] = 1.0 #Flung Brickle onto ledge
            Variables[0xC00C] = 1.0 #Boss Brickle wants you to attack the Dreamcaps
            Variables[0xC132] = 1.0 #Got all attack pieces and defeated Dreamcaps
            #Variables[0xE01B] = 1.0 #Unlock Dream World Attacks
            Variables[0xC045] = 1.0 #Bunny hops away in flower room
            Variables[0xC024] = 1.0 #Cornered bunny and got nightmare chunk
            Variables[0x9016] = 1.0 #Bridge under Nightmare Chunk room breaks
            Variables[0xC956] = 1.0 #Eldream's nightmare chunk is shattered
            Variables[0xC04D] = 1.0 #Saved Eldream, Dream's Deep portal is open
            Variables[0xC06D] = 1.0 #Skipped opening cutscene for Dream's Deep
            Variables[0xC048] = 1.0 #Prince Dreambert cutscene when entering Dream's Deep
            Variables[0xC068] = 1.0 #Luigi explains how the different entrance works
            Variables[0xC071] = 1.0 #Dreamy Luigi follows you in Dream's Deep
            Variables[0xC074] = 1.0 #"Where were you" cutscene when leaving Dream's Deep
            #Variables[0xCABF] = 1.0 #Opens gate at bottom of Mushrise Park
            Variables[0xC335] = 1.0 #Dozing Sands badge cutscene
            #emit_command(0x0033, [0x2003, 0x01], Variables[0x3000]) #Gives bronze badge
            Variables[0xC376] = 1.0 #Guy fell down sand slope
            Variables[0xC336] = 1.0 #Shelltops hammer Sandoons
            Variables[0xC337] = 1.0 #Saved Shelltops
            Variables[0xC338] = 1.0 #Fake Block 1 hit
            Variables[0xC3AE] = 1.0 #Fake Block 2 hit
            Variables[0xC35F] = 1.0 #Pi'illo is knocked down
            Variables[0xC33A] = 1.0 #Shelltops move out of way
            Variables[0xC33B] = 1.0 #Unlock beans in pause screen, Shelltops are done
            Variables[0xC058] = 1.0 #Giant wall of enemies, Mario and Luigi book it
            Variables[0xC059] = 1.0 #First enter Luiginary work
            Variables[0xC05C] = 1.0 #Don't walk off edges, idiot
            Variables[0xC05D] = 1.0 #Enemies run away in fear
            Variables[0xC085] = 1.0 #Moves Mario and Luigi forward and stops
            Variables[0xC05E] = 1.0 #Exiting Luiginary Stack tutorial
            Variables[0xE014] = 1.0 #Can exit Luiginary Stack
            Variables[0xC334] = 1.0 #Cutscene for getting first Dozite
            wait(3)
            Variables[0xC342] = 1.0 #Got first Dozite
            #Variables[0x9040] = 1.0 #Bridge is up
            Variables[0xC33D] = 1.0 #Britta appears
            Variables[0xC33E] = 1.0 #Another talk with Britta
            Variables[0xC340] = 1.0 #First drilldigger tutorial
            Variables[0xC36D] = 1.0 #Drilldigger tutorial with Britta
            Variables[0xC34B] = 1.0 #First Deco Pi'illo rock broken
            Variables[0xC07C] = 1.0 #Drill dreamwork tutorial
            Variables[0xC07E] = 1.0 #Ha! I'm over HERE now!
            Variables[0xC07D] = 1.0 #Centrifugal force
            Variables[0xC07F] = 1.0 #Break dream stone with hammer (duh)
            Variables[0xC389] = 1.0 #First main Deco Pi'illo is saved
            Variables[0xC362] = 1.0 #Second main Deco Pi'illo is saved
            Variables[0xC361] = 1.0 #Third main Deco Pi'illo is saved
            Variables[0xC34A] = 1.0 #Final main Deco Pi'illo is saved
            Variables[0xC347] = 1.0 #Torkscrew eats Pi'illo
            Variables[0xC348] = 1.0 #Barrier is broken
            Variables[0xC349] = 1.0 #Minigame is played
            Variables[0xC366] = 1.0 #Britta checks out the new area
            Variables[0xC368] = 1.0 #Scene before saving Dreamstone
            Variables[0xC050] = 1.0 #Confirm if you know how to use the stack
            Variables[0xC052] = 1.0 #Luiginary stack ground pound tutorial flag 1
            Variables[0xC06C] = 1.0 #Luiginary stack ground pound tutorial flag 2
            Variables[0xC025] = 1.0 #Luiginary stack high jump tutorial flag 1
            Variables[0xC053] = 1.0 #Luiginary stack high jump tutorial flag 2
            Variables[0xC054] = 1.0 #First encountered Dreamstone and found out he's a jerk
            Variables[0xC055] = 1.0 #Caught up to Dreamstone, he retreats
            Variables[0xC056] = 1.0 #Caught back up to Dreamstone, he retreats again
            Variables[0xC0A5] = 1.0 #Defeated Drilldozer
            Variables[0xC3B8] = 1.0 #Accepting tours for Mount Pajamaja cutscene
            #Variables[0xC369] = 1.0 #Opens side rooms in Pi'illo Castle platform area and fixes bridge in Blimport
            #Variables[0xC960] = 1.0 #Tree blocking Wakeport has been removed
            wait(3)
            Variables[0xC961] = 1.0 #Wakeport intro watched
            Variables[0xC9E3] = 1.0 #Popple is introduced
            Variables[0xC978] = 1.0 #Badge campaign
            Variables[0xC962] = 1.0 #Registered for tour
            Variables[0xC964] = 1.0 #Massif hunt begin
            Variables[0xC96F] = 1.0 #Attack piece cutscene Zeekeeper guy
            Variables[0xC987] = 1.0 #Talked to the hoo who wants a girlfriend
            Variables[0xC988] = 1.0 #Accepted his sidequest
            Variables[0xC97E] = 1.0 #Kylie Koopa first met
            Variables[0xC978] = 1.0 #Watched badge tutorial in Wakeport
            Variables[0xC96B] = 1.0 #Panel tutorial cutscene
            Variables[0xC969] = 1.0 #Panel tutorial complete
            #Variables[0xC96C] = 1.0 #Bridge is down
            Variables[0xC96D] = 1.0 #Toad is no longer worried
            Variables[0xC96A] = 1.0 #Big Massif is awake
            Variables[0xC977] = 1.0 #
            Variables[0xC600] = 1.0 #Massif dream intro part 1
            Variables[0xC61E] = 1.0 #Massif dream intro part 2
            Variables[0xC633] = 1.0 #Door to the main area is open
            Variables[0xC601] = 1.0 #Hooraws Bail
            Variables[0xCF80] = 1.0 #Timer tutorial
            Variables[0xC096] = 1.0 #Timer slow tutorial
            Variables[0xC097] = 1.0 #Timer fast tutorial
            Variables[0xC098] = 1.0 #Timer Dreambert leaves
            Variables[0xC09A] = 1.0 #Other part of timer tutorial
            Variables[0xC0AC] = 1.0 #Fall slow to hit red coins
            Variables[0xC0AE] = 1.0 #Crunch to hit bombs
            wait(3)
            #Variables[0xC3B9] = 1.0 #Massifs pushed rock and opened Mount Pajamaja
            Variables[0xC3BB] = 1.0 #Massifs explain how a gate works
            Variables[0xCFC2] = 1.0 #Massifs are in right position for cutscene above
            Variables[0xC3C6] = 1.0 #Big Massif tells you to hurry up
            Variables[0xC3C7] = 1.0 #Massifs tell you to come over to them
            Variables[0xC3C8] = 1.0 #Spin Jump tutorial
            Variables[0xC3CB] = 1.0 #Mega Low Intro
            Variables[0xC3CC] = 1.0 #RISING BEEF!!!
            Variables[0xC3CD] = 1.0 #Massifs are high
            Variables[0xC3CE] = 1.0 #Massifs commit die
            Variables[0xC3CF] = 1.0 #A Massif hint: turn valve
            Variables[0xC3D0] = 1.0 #Mega Phil Intro
            Variables[0xCCBF] = 1.0 #Luiginary Cone Tutorial
            Variables[0xC41B] = 1.0 #Side Drill Tutorial
            Variables[0xC4B2] = 1.0 #Tunnel in Side Drill tutorial is broken
            Variables[0xC41C] = 1.0 #Side Drill Tutorial Part 2
            Variables[0xC428] = 1.0 #Rock in second Side Drill tutorial is broken
            Variables[0xC4B8] = 1.0 #Drink fountain tutorial
            Variables[0xC4B6] = 1.0 #Drank from fountain the first time
            Variables[0xC3EB] = 1.0 #Change of scenery cutscene (currently broken)
            Variables[0xC3D4] = 1.0 #Massifs break ice tutorial
            Variables[0xC3D5] = 1.0 #Massifs break ice tutorial
            Variables[0xC3F2] = 1.0 #Wind blows things!?
            Variables[0xC422] = 1.0 #Mega Cush and Shawn intro
            Variables[0xC425] = 1.0 #The people at the top of the mountain look evil
            Variables[0xC424] = 1.0 #Dreambeats cutscene
            Variables[0xC426] = 1.0 #Retreated to Dream World
            Variables[0xC640] = 1.0 #First entered Mount Pajamaja Summit dreampoint
            Variables[0xC641] = 1.0 #Trapped in Mount Pajamaja Summit
            Variables[0xC642] = 1.0 #Luiginary temperature tutorial
            Variables[0xC643] = 1.0 #Luiginary temperature tutorial
            Variables[0xCC9D] = 1.0 #We can erupt the volcano cutscene
            Variables[0xC645] = 1.0 #Luiginary cone storm tutorial
            Variables[0xC646] = 1.0 #Made it to the top, considering agitating the volcano
            Variables[0xC427] = 1.0 #Exited Pajamaja Summit Cutscene
            Variables[0xC4AD] = 1.0 #Gold pipes appear in early game areas
            Variables[0xCC7F] = 1.0 #Peach is in Driftwood Shores Cutscene
            Variables[0xCC80] = 1.0 #Part of same cutscene as above?
            Variables[0xCC81] = 1.0 #Allows you to talk to the guys that let you into Driftwood Shores
            Variables[0xCC4E] = 1.0 #Broque is faking liking you
            Variables[0xCC4F] = 1.0 #Can access Driftwood Shore
            Variables[0x9061] = 1.0 #Removes invisible wall blocking Driftwood Shore
            wait(3)
            Variables[0xCC50] = 1.0 #Intro to the Rose Broquet
            Variables[0xCC51] = 1.0 #Broque Madame intro
            Variables[0xCC54] = 1.0 #Prevents crash
            #Variables[0xCC63] = 1.0 #Been to deluxe shop in the Rose Broquet
            Variables[0xCC57] = 1.0 #Direct attention to statues
            #Variables[0xCC58] = 1.0 #MAJOR DISCOVERY!!!
            Variables[0xCC52] = 1.0 #First encounter inner tube
            Variables[0xCB41] = 1.0 #Seadrick dreampoint talked to him
            Variables[0xCB42] = 1.0 #Seadrick dreampoint allowed to leave
            Variables[0xCB72] = 1.0 #Maybe we should look around
            Variables[0xCC56] = 1.0 #Peach was the imposter
            Variables[0xCC65] = 1.0 #First Crab Minigame cutscene
            Variables[0xCC67] = 1.0 #Won First Crab Minigame
            Variables[0xCB57] = 1.0 #Seatoon cutscene
            Variables[0xCC69] = 1.0 #Another dreampoint is available
            Variables[0xCB59] = 1.0 #Seabelle (who is a total supermodel) cutscene
            Variables[0xCC6A] = 1.0 #Another dreampoint is nearby
            Variables[0xCB58] = 1.0 #Seabury cutscene
            Variables[0xCB6A] = 1.0 #First puzzle room tutorial
            Variables[0xCC53] = 1.0 #Talk to Broque Madame after Elite Trio's defeat
            Variables[0xCC82] = 1.0 #Doctor Snoozemore Appears
            Variables[0xCC83] = 1.0 #Doctor Snoozemore Cutscene Watched
            Variables[0xC0B4] = 1.0 #Pi'illo Castle dream's deep opens
            Variables[0xC09B] = 1.0 #First entered Pi'illo Castle Dream's Deep
            Variables[0xC0A7] = 1.0 #Same cutscene as above?
            Variables[0xC09F] = 1.0 #Luiginary Ball tutorial
            Variables[0xC0A0] = 1.0 #Luiginary Ball tutorial part 2
            Variables[0xC0A3] = 1.0 #Learning Luiginary Ball Hookshot
            Variables[0xC0A4] = 1.0 #Learning Luiginary Ball Throw
            Variables[0xC5CC] = 1.0 #You must find the Ultibed parts cutscene
            Variables[0xC0A1] = 1.0 #Ultibed appears in pause menu
            Variables[0xC438] = 1.0 #Ultibed cutscene in Mount Pajamaja is watched
            Variables[0xC4AE] = 1.0 #Fixes a glitch in the rock code
            Variables[0xC9A1] = 1.0 #Massifs are desperate for tourists
            Variables[0xC9A2] = 1.0 #Ball Hop tutorial
            Variables[0xC9A3] = 1.0 #Finished learning the Ball Hop
            Variables[0xC9A4] = 1.0 #Massifs are impatient yet again
            Variables[0xC9A6] = 1.0 #Massifs can't open gate
            Variables[0xC9A7] = 1.0 #Massifs give you attack pieces
            Variables[0xC9D0] = 1.0 #Pi'illo Castle Battle Ring introduction
            Variables[0xC304] = 1.0 #Spawns more rocks in Mushrise Park
            Variables[0xC9F5] = 1.0 #Boss Brickle ponders who can help him
            Variables[0xC9B2] = 1.0 #Ultibed in Mushrise Park start
            Variables[0xC9B3] = 1.0 #Ultibed in Mushrise Park start
            Variables[0xC9F3] = 1.0 #Guy lets you into a rock area
            Variables[0xC9F4] = 1.0 #Tree blocking other rock area is removed
            #Variables[0xC9D9] = 1.0 #Driftwood Jelly Sheets have been stolen
            Variables[0xC9D4] = 1.0 #Can enter the cave
            Variables[0xC9DD] = 1.0 #Listened to the old coot vent
            #Variables[0xC9DE] = 1.0 #Second Crab Minigame complete
            Variables[0xC9AF] = 1.0 #Britta yells at cliff
            Variables[0xC9B0] = 1.0 #Dozing Sands glowing rock introduction
            Variables[0xC9B1] = 1.0 #Dreambert assumes he knows what the rock means
            Variables[0xC9F8] = 1.0 #Popple notices the collector's hiding something
            Variables[0xC9E1] = 1.0 #Wiggler first cutscene watched
            Variables[0xC9E2] = 1.0 #Wiggler second cutscene watched
            wait(3)
            #Variables[0xC9E0] = 1.0 #Wiggler is defeated
            Variables[0xC9EA] = 1.0 #Bedsmith appears
            Variables[0xC59F] = 1.0 #Cog to enter Somnom Woods is available
            Variables[0x9099] = 1.0 #Stairs to switch in Somnom Woods are up
            Variables[0xC5A0] = 1.0 #Cog has been turned
            Variables[0x909A] = 1.0 #Switch in Somnom Woods has been turned
            Variables[0xC5A1] = 1.0 #Bedsmith builds the Ultibed
            Variables[0xC5C6] = 1.0 #Camera pans to show the rest of the area
            Variables[0xC5C5] = 1.0 #The first Pi'illo Master is ahead
            Variables[0xC5C8] = 1.0 #Met first Pi'illo Master
            Variables[0xC71A] = 1.0 #Luiginary propeller tutorial part 1
            Variables[0xC71C] = 1.0 #Luiginary propeller tutorial part 2
            #Variables[0xC5A4] = 1.0 #Panel tutorial
            Variables[0xC5A2] = 1.0 #Watched cutscene with children of Sommon
            Variables[0xC5A5] = 1.0 #Children of Sommon introduce minigame
            Variables[0xC5A6] = 1.0 #First ball hop minigame is complete
            Variables[0xC9F2] = 1.0 #The master is behind the mole mario gate explanation
            Variables[0xC5D3] = 1.0 #Children of Sommon introduce second minigame
            Variables[0xC70B] = 1.0 #First entered the tree room
            #Variables[0xCB76] = 1.0 #Getting near the Zeekeeper
            Variables[0xC746] = 1.0 #Almost reached the apex
            Variables[0xC439] = 1.0 #We're finally at Neo Bowser Castle
            Variables[0xC45E] = 1.0 #Elite Trio flee
            Variables[0xC43B] = 1.0 #Kamek randomized the rooms in the first area
            Variables[0xC475] = 1.0 #Switch is on the other side
            Variables[0xC474] = 1.0 #Cutscene before entering Kamek's first dream world
            Variables[0xC0B6] = 1.0 #Kamek 1 is defeated
            Variables[0xC4AA] = 1.0 #Bowser and Antasma notice your progress
            Variables[0xC447] = 1.0 #Kamek randomizes the second area
            Variables[0xC0B7] = 1.0 #Kamek 2 is defeated
            #Variables[0xC451] = 1.0 #Kamek 3's magic is borked
            Variables[0xC455] = 1.0 #Flame pipe introduction
            Variables[0xE00B] = 1.0 #Gives Luiginary stack
            Variables[0xE00C] = 1.0 #Gives Luiginary tornado (but none of its abilities)
            change_room(0x0298, position=(0.0, 0.0, 0.0), init_sub=-0x1, music=MusicFlag.FORCE_KEEP_CURRENT)
            emit_command(0x0056, [0x01, 0x028D0026])  # Execute the command that was replaced with a call to this subroutine.

        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Changes the room the second you enter the blimp falling cutscene
        script = fevent_manager.parsed_script(0x0298, 0)
        original_len = script.subroutines[0x2a].serialized_len(fevent_manager, 0, with_footer=False)
        script.subroutines[0x2a].commands.clear()
        change_room(0x0064, position=(0x1F, 0x0, 0x1F), init_sub=-0x1, music=MusicFlag.FORCE_KEEP_CURRENT,
                    subroutine=script.subroutines[0x2a])
        new_len = script.subroutines[0x2a].serialized_len(fevent_manager, 0, with_footer=False)
        script.subroutines[0x2a].commands.append(RawDataCommand(b'\xff' * (original_len - new_len)))

        #Sets up Blimport so you have everything
        script = fevent_manager.parsed_script(0x0064, 0)
        script.subroutines[0x3d].commands[138] = CodeCommandWithOffsets(0x0003, [0x01, PLACEHOLDER_OFFSET], offset_arguments={1: 'center_and_unite'})

        #Subroutine for the first room
        @subroutine(subs=script.subroutines, hdr=script.header)
        def center_and_unite(sub: Subroutine):
            set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
            set_movement_multipliers(Screen.TOP, 1.0, 1.0)
            set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
            set_touches_blocked(False)
            set_action_icons_shown(True, animated=False)
            set_actor_attribute(Actors.LUIGI, 0x00, 1.0)
            set_actor_attribute(Actors.LUIGI, 0x01, 1.0)
            set_actor_attribute(Actors.MARIO, 0x17, 8.0)
            emit_command(0x00B4, [Actors.MARIO, 0x00, 0x022F, 0x0000, 0x021F])
            emit_command(0x00B4, [Actors.LUIGI, 0x00, 0x022F, 0x0000, 0x01FF])
            emit_command(0x00DB, [0x01, 0x01])
            emit_command(0x00DA, [0x00])
            emit_command(0x00DC)
            tint_screen('00000000', initial='------FF', transition_duration=16)
            Variables[0xE000] = int(settings[0][0])
            Variables[0xE001] = int(settings[0][1])
            Variables[0xE002] = int(settings[0][2])
            Variables[0xE003] = int(settings[0][3])
            Variables[0xE004] = int(settings[0][4])
            Variables[0xE005] = int(settings[0][5])
            Variables[0xE00A] = int(settings[0][6])
            Variables[0xE00D] = int(settings[0][7])
            Variables[0xE00E] = int(settings[0][8])
            Variables[0xE00F] = int(settings[0][9])
            Variables[0xE010] = int(settings[0][10])
            Variables[0xE011] = int(settings[0][11])
            Variables[0xE012] = int(settings[0][12])
            Variables[0xE013] = int(settings[0][13])
            Variables[0x9015] = int(settings[0][14])
            Variables[0xC369] = int(settings[0][15])
            Variables[0xCABF] = int(settings[0][16])
            Variables[0x9040] = int(settings[0][17])
            Variables[0xC343] = int(settings[0][18])
            Variables[0xC344] = int(settings[0][19])
            Variables[0xC345] = int(settings[0][20])
            Variables[0xC346] = int(settings[0][21])
            if settings[0][18] == 1.0 and settings[0][19] == 1.0 and settings[0][20] == 1.0 and settings[0][21] == 1.0:
                Variables[0x903F] = 1.0
            Variables[0xC960] = int(settings[0][22])
            Variables[0xC3B9] = int(settings[0][23])
            add_in_place(settings[0][24] + settings[0][25] + settings[0][26], Variables[0xB0F7])
            add_in_place(settings[0][24] + settings[0][25] + settings[0][26], Variables[0xB02D])
            Variables[0xC47E] = int(settings[0][27])
            if settings[1][0] == 1:
                Variables[0x904A] = 1.0
                Variables[0x905C] = 1.0
                Variables[0x90A5] = 1.0
            Variables[0xCC28] = settings[2][0]
            Variables[0xCB07] = settings[2][1]
            Variables[0xC0B5] = settings[2][1]
            Variables[0xC92F] = settings[2][2]
            Variables[0xC04C] = settings[2][3]
            Variables[0xC367] = settings[2][4]
            Variables[0xC057] = settings[2][5]
            Variables[0xC60E] = settings[2][6]
            Variables[0xC423] = settings[2][7]
            Variables[0xC647] = settings[2][8]
            #Variables[0xC648] = settings[2][8]
            Variables[0xC649] = settings[2][8]
            #Variables[0xC64E] = settings[2][8]
            Variables[0xCB45] = settings[2][9]
            Variables[0xC9E0] = settings[2][10]
            Variables[0xC621] = settings[2][11]
            Variables[0xC622] = settings[2][11]
            Variables[0xC623] = settings[2][11]
            Variables[0xC637] = settings[2][11]
            Variables[0xC5AF] = settings[2][12]
            Variables[0xC0BF] = settings[2][13]
            Variables[0xC0CA] = settings[2][14]
            Variables[0xC45C] = settings[2][15]
            change_room(0x001c, position=(800.0, 80.0, 800.0), init_sub=-0x01, facing=8)

        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Removes the hammer tutorial cutscene
        script = fevent_manager.parsed_script(0x0001, 0)
        script.header.triggers[4] = (0, 0, 0, 0, 0, 0x0032, 0x78012)

        #Sets the script to look at the room you fight Torkscrew
        script = fevent_manager.parsed_script(0x0102, 0)

        #Names the label so it can be accessed later (Hex value got by subtracting comment on top from comment on label)
        #cast(SubroutineExt, script.subroutines[0x49]).labels = {
        #    'label_151': 0x2D55,
        #}

        #Allows you to access Torkscrew even if the cutscene breaks by changing the initialization subroutine
        cast(SubroutineExt, script.subroutines[script.header.init_subroutine]).name = 'init_doz'
        script.header.init_subroutine = None
        @subroutine(subs=script.subroutines, hdr=script.header, init=True)
        def access_torkscrew(sub: Subroutine):
            branch_if(Variables[0x903F], "==", 0.0, 'label_0')
            branch_if(Variables[0xC367], "==", 1.0, 'label_0')
            change_room(0x02AB, position=(1000.0, 0.0, 2000.0), init_sub=-0x01)

            label('label_0', manager=fevent_manager)
            call('init_doz')

        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Fixes Smoldergeist
        script = fevent_manager.parsed_script(0x0094, 0)
        @subroutine(subs=script.subroutines, hdr=script.header)
        def fix_smoldergeist(sub: Subroutine):
            branch_if(Variables[0xCC28], "==", 1.0, 'label_0')
            start_battle(0x00027008, WorldType.REAL, transition=Transition.BOSS, music=Sound(5, 0x0006), unk4=0x08)
            Variables[0xCC28] = 1.0

            label('label_0', manager=fevent_manager)
        script.header.triggers[0] = (0x022600AF, 0x0258032F, 0x00000000, 0x00000000, 0xFFFF0000, len(script.subroutines)-1, 0x00078012)
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Fixes Bowser and Antasma
        script = fevent_manager.parsed_script(0x00F3, 0)
        @subroutine(subs=script.subroutines, hdr=script.header)
        def fix_bowser_and_antasma(sub: Subroutine):
            branch_if(Variables[0xC04C], "==", 1.0, 'label_0')
            start_battle(0x0002500C, WorldType.DREAM, transition=Transition.BOSS, music=Sound(5, 0x0006), unk4=0x0E)
            #emit_command(0x0033, [0x200A, 0x01], Variables[0x3000]) #Gives guard badge
            Variables[0xC04C] = 1.0

            label('label_0', manager=fevent_manager)
        script.header.triggers[0] = (0xFFF00320, 0x001005DC, 0x00000000, 0x00000000, 0x000A006E, len(script.subroutines)-1, 0x00010002)
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Fixes a glitch in the Massif lobby that gives you some abilities early
        script = fevent_manager.parsed_script(0x010e, 0)
        cast(SubroutineExt, script.subroutines[0xa]).name = 'pass_code'
        script.subroutines[0xb0].commands[-2] = CodeCommandWithOffsets(0x0003, [0x01, PLACEHOLDER_OFFSET], offset_arguments={1: 'pass_code'})
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

        #Stops Massifs pushing rock cutscene from appearing
        script = fevent_manager.parsed_script(0x0067, 0)
        if settings[1][1] == 1:
            script.header.actors.append((0x0025027B, 0x000002E4, 0xFFFF000E, 0xFFFFFFFF, 0xFFFFFFFF, 0x01980143))
            script.header.actors.append((0x000002BB, 0x000002E4, 0xFFFF000E, 0xFFFFFFFF, 0xFFFFFFFF, 0x01980143))
        cast(SubroutineExt, script.subroutines[script.header.init_subroutine]).name = 'init_rockroom'
        cast(SubroutineExt, script.subroutines[0x6b]).name = 'sub_0x6b'
        cast(SubroutineExt, script.subroutines[0x6c]).name = 'sub_0x6c'
        script.header.init_subroutine = None
        @subroutine(subs=script.subroutines, hdr=script.header, init=True)
        def rock_pos(sub: Subroutine):
            set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
            set_movement_multipliers(Screen.TOP, 0.0, 0.0)
            set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
            set_touches_blocked(True)
            call('sub_0x6b')
            branch_if(Variables[0xC369], '==', 1.0, 'label_0', invert=True)
            branch_if(Variables[0xC961], '==', 0.0, 'label_0', invert=True)
            branch_if(Variables[0xC4AE], '==', 0.0, 'sub_0x6c')

            label('label_0', manager=fevent_manager)
            tint_screen('00000000', initial='------FF', transition_duration=16)
            set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
            set_movement_multipliers(Screen.TOP, 1.0, 1.0)
            set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
            set_touches_blocked(False)
            branch_if(Variables[0xC3B9], '!=', 0.0, 'label_1')
            emit_command(0x00B4, [0x0D, 0x00, 0x0339, 0x0000, 0x02E4])
            if settings[1][1] == 1:
                emit_command(0x00B4, [len(script.header.actors)-2, 0x00, 0x0339, 0x0025, 0x02E4])
                emit_command(0x00B4, [len(script.header.actors)-1, 0x00, 0x0379, 0x0000, 0x02E4])

            label('label_1', manager=fevent_manager)

        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(2)

        #Sets the script to look at the room where Mega Phil and Low reside
        script = fevent_manager.parsed_script(0x0068, 0)

        cast(SubroutineExt, script.subroutines[0x63]).name = 'sub_0x63'

        #A new subroutine that acts like the original one for Mega Low
        @subroutine(subs=script.subroutines, hdr=script.header)
        def mega_low(sub: Subroutine):
            branch_if(Variables[0xC3C9], '==', 1.0, 'label_0', invert=True)
            call('sub_0x63')

            label('label_0', manager=fevent_manager)

        #Changes Pi'illo so it runs the new subroutine
        script.header.actors[8] = (0x00D20424, 0x80080271, 0x00290017, 0xFFFFFFFF, 0x00000071, 0x005B8168)
        script.header.actors[9] = (0x00D20424, 0x00010271, 0x0029000E, 0xFFFFFFFF, 0x00000071, 0x0250014C)

        #Stops Starlow from stopping you if you go left
        script.header.triggers[4] = (0, 0, 0, 0, 0, 0x0000000A, 0x00078012)

        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Fixes the Mammoshka boss fight
        script = fevent_manager.parsed_script(0x007D, 0)
        cast(SubroutineExt, script.subroutines[0x2d]).labels = {
            'label_0': 0x88,
            'label_3': 0x15E,
        }
        script.subroutines[0x2d].commands[5] = CodeCommandWithOffsets(0x0002, [0x0, Variables[0xC438], 1.0, 0x01, PLACEHOLDER_OFFSET], offset_arguments={4: 'label_0'})
        script.subroutines[0x2d].commands[11] = CodeCommandWithOffsets(0x0002, [0x0, Variables[0xC438], 1.0, 0x01, PLACEHOLDER_OFFSET], offset_arguments={4: 'label_3'})
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        #Fixes a weird quirk with Dreamy Driftwood Shore giving you Luiginary Works
        script = fevent_manager.parsed_script(0x00D3, 0)
        script.subroutines[0xb8].commands[-17] = CodeCommandWithOffsets(0x000E, [1.0], Variable(0xC000))
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

        #Blocks Dream World in the Summit until you have the needed abilities
        #script = fevent_manager.parsed_script(0x007F, 0)
        #script_index = 0x007F * 2

        # Workaround for dynamic scope in Nuitka
        #if '__compiled__' in globals():
        #    inspect.currentframe().f_locals['script_index'] = script_index

        #cast(SubroutineExt, script.subroutines[0x52]).name = 'sub_0x52'
        #@subroutine(subs=script.subroutines, hdr=script.header)
        #def summit_access(sub: Subroutine):
        #    branch_if(Variables[0xE00A], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xE00E], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xE00F], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xE010], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xE011], '==', 0.0, 'label_0')
        #    call('sub_0x52')

        #    label('label_0', manager=fevent_manager)
        #    say(None, TextboxSoundsPreset.SILENT, "You don't have the\nrequired abilities.[Pause 45]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)

        #script.header.triggers[0] = (0x018203EE, 0x02140450, 0x00000000, 0x00000000, 0x01000040, len(script.subroutines)-1, 0x00078002)
        #update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))


        #Adds a trigger right before Bowser in Neo Bowser Castle that warps you out if you haven't defeated all bosses
        #script = fevent_manager.parsed_script(0x015E, 0)
        #script_index = 0x015E * 2

        # Workaround for dynamic scope in Nuitka
        #if '__compiled__' in globals():
        #    inspect.currentframe().f_locals['script_index'] = script_index

        #@subroutine(subs=script.subroutines, hdr=script.header)
        #def defeat_all_bosses(sub: Subroutine):
        #    branch_if(Variables[0xCC28], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xCB07], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC92F], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC04C], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC367], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC057], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC60E], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC423], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC649], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xCB45], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC637], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC5AE], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC0BF], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC0B8], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC0CA], '==', 0.0, 'label_0')
        #    branch_if(Variables[0xC45C], '==', 0.0, 'label_0')
        #    branch('label_1')

        #    label('label_0', manager=fevent_manager)
        #    set_blocked_buttons(Screen.TOP, ButtonFlags.ALL, res=Variables[0x3000])
        #    set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL, res=Variables[0x3001])
        #    set_movement_multipliers(Screen.TOP, 0.0, 0.0)
        #    set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
        #    set_touches_blocked(True)
        #    say(None, TextboxSoundsPreset.SILENT, "You must defeat all bosses\nbefore you can face Bowser.[Pause 45]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
        #    change_room(0x01C8, position=(1400.0, 0.0, 1360.0), init_sub=-0x1)

        #    label('label_1', manager=fevent_manager)

        #script.header.triggers.append((0x00000000, 0x01F302A8, 0x00000000, 0x00000000, 0xFFFF0046, len(script.subroutines)-1, 0x00078022))
        #update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

        #Adds dialogue to Toadsworth in Pi'illo Castle, guiding you to his overpriced badge shop
        script = fevent_manager.parsed_script(0x0082, 0)
        script_index = 0x0082 * 2

        # Workaround for dynamic scope in Nuitka
        if '__compiled__' in globals():
            inspect.currentframe().f_locals['script_index'] = script_index

        @subroutine(subs=script.subroutines, hdr=script.header)
        def buy_overpriced_badges(sub: Subroutine):
            set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
            set_movement_multipliers(Screen.TOP, 0.0, 0.0)
            set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
            set_touches_blocked(True)
            branch_if(Variables[0xCDA0], '==', 1.0, 'label_0')
            say(0x06, TextboxSoundsPreset.TOAD, 'I daresay, you should stimulate the economy\nby going to the badge shop![Wait]')
            branch('label_1')

            label('label_0', manager=fevent_manager)
            say(0x06, TextboxSoundsPreset.TOAD, 'See? Even an old tycoon like me\ncan save local businesses![Wait]')

            label('label_1', manager=fevent_manager)
            set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
            set_movement_multipliers(Screen.TOP, 1.0, 1.0)
            set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
            set_touches_blocked(False)

        script.header.actors[6] = (0x00000000, 0x80000000, 0xFFFF0018, 0xFFFFFFFF, len(script.subroutines)-1, 0x00591168)
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(1)

        # Changes Pi'illo Castle's badge shop to be Toadsworth's Overpriced Badge Shop
        script = fevent_manager.parsed_script(0x0088, 0)
        script_index = 0x0088 * 2

        # Workaround for dynamic scope in Nuitka
        if '__compiled__' in globals():
            inspect.currentframe().f_locals['script_index'] = script_index

        @subroutine(subs=script.subroutines, hdr=script.header)
        def buy_overpriced_badges(sub: Subroutine):
            set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
            set_movement_multipliers(Screen.TOP, 0.0, 0.0)
            set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
            set_touches_blocked(True)
            branch_if(Variables[0xCDA0], '==', 1.0, 'label_0')
            #Intro dialogue
            Variables[0xCDA0] = 1.0
            say(0x06, TextboxSoundsPreset.TOAD, 'Hello... valued customer...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            say(0x06, TextboxSoundsPreset.TOAD, 'Huh? Oh, sorry, I\'m just a little bummed...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            say(0x06, TextboxSoundsPreset.TOAD, 'See, ever since the economic recession\nof 2021, we had to sell our shop\nto Toadsworth.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            say(0x06, TextboxSoundsPreset.TOAD, 'I have nothing against the guy, but...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            say(0x06, TextboxSoundsPreset.TOAD, '...well, you\'ll see when you see our prices.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            say(0x06, TextboxSoundsPreset.TOAD, 'Anyway, with that out of the way...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)

            label('label_0', manager=fevent_manager)
            #Choose a badge - page 1
            say(0x06, TextboxSoundsPreset.TOAD, 'Which badge will it be?\n[Option][Indent 10]Strike Badge - 400 coins\n[Option][Indent 10]Guard Badge - 500 coins\n[Option][Indent 10]Bronze Badge - 500 coins\n' +
                                                '[Option][Indent 10]Virus Badge - 800 coins\n[Option][Indent 10]Master Badge - 1200 coins\n[Option][Indent 10]Next Page\n[Option][Indent 10]Never mind', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.MIDDLE_LEFT)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 6.0, 'label_2')
            branch_if(Variables[0x1000], '==', 5.0, 'label_3')
            branch('label_4')

            label('label_4', manager=fevent_manager)
            #Confirmation - page 1
            Variables[0x1001] = Variables[0x1000]
            say(0x06, TextboxSoundsPreset.TOAD, 'Are you sure this is the one?\n[Option][Indent 10]Yes\n[Option][Indent 10]No', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 1.0, 'label_0')
            branch_if(Variables[0x1001], '==', 0.0, 'label_8')
            branch_if(Variables[0x1001], '==', 1.0, 'label_9')
            branch_if(Variables[0x1001], '==', 2.0, 'label_10')
            branch_if(Variables[0x1001], '==', 3.0, 'label_11')
            branch_if(Variables[0x1001], '==', 4.0, 'label_12')

            label('label_8', manager=fevent_manager)
            #Gives the Strike Badge
            branch_if(Variables[0xCDA1], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 400.0, 'label_13')
            emit_command(0x0031, [-0x00000190], Variables[0x1002])
            emit_command(0x0033, [0x2009, 0x01], Variables[0x3000])
            Variables[0xCDA1] = 1.0
            branch('label_7')

            label('label_9', manager=fevent_manager)
            #Gives the Guard Badge
            branch_if(Variables[0xCDA2], '==', 1.0, 'label_9')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 500.0, 'label_13')
            emit_command(0x0031, [-0x000001F4], Variables[0x1002])
            emit_command(0x0033, [0x200A, 0x01], Variables[0x3000])
            Variables[0xCDA2] = 1.0
            branch('label_7')

            label('label_10', manager=fevent_manager)
            #Gives the Bronze Badge
            branch_if(Variables[0xCDA3], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 500.0, 'label_13')
            emit_command(0x0031, [-0x000001F4], Variables[0x1002])
            emit_command(0x0033, [0x2003, 0x01], Variables[0x3000])
            Variables[0xCDA3] = 1.0
            branch('label_7')

            label('label_11', manager=fevent_manager)
            #Gives the Virus Badge
            branch_if(Variables[0xCDA4], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 800.0, 'label_13')
            emit_command(0x0031, [-0x00000320], Variables[0x1002])
            emit_command(0x0033, [0x200B, 0x01], Variables[0x3000])
            Variables[0xCDA4] = 1.0
            branch('label_7')

            label('label_12', manager=fevent_manager)
            #Gives the Master Badge
            branch_if(Variables[0xCDA5], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 1200.0, 'label_13')
            emit_command(0x0031, [-0x000004B0], Variables[0x1002])
            emit_command(0x0033, [0x2001, 0x01], Variables[0x3000])
            Variables[0xCDA5] = 1.0
            branch('label_7')

            label('label_3', manager=fevent_manager)
            #Choose a badge - page 2
            say(0x06, TextboxSoundsPreset.TOAD, 'We also have...\n[Option][Indent 10]Risk Badge - 1200 coins\n[Option][Indent 10]Silver Badge - 3000 coins\n[Option][Indent 10]Expert Badge - 5000 coins\n' +
                                                '[Option][Indent 10]Miracle Badge - 5000 coins\n[Option][Indent 10]Gold Badge - 10000 coins\n[Option][Indent 10]Previous Page\n[Option][Indent 10]Never mind', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.MIDDLE_LEFT)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 6.0, 'label_2')
            branch_if(Variables[0x1000], '==', 5.0, 'label_0')
            branch('label_5')

            label('label_5', manager=fevent_manager)
            #Confirmation - page 2
            Variables[0x1001] = Variables[0x1000]
            say(0x06, TextboxSoundsPreset.TOAD, 'Are you sure this is the one?\n[Option][Indent 10]Yes\n[Option][Indent 10]No', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 1.0, 'label_0')
            branch_if(Variables[0x1001], '==', 0.0, 'label_14')
            branch_if(Variables[0x1001], '==', 1.0, 'label_15')
            branch_if(Variables[0x1001], '==', 2.0, 'label_16')
            branch_if(Variables[0x1001], '==', 3.0, 'label_17')
            branch_if(Variables[0x1001], '==', 4.0, 'label_18')

            label('label_14', manager=fevent_manager)
            #Gives the Risk Badge
            branch_if(Variables[0xCDA6], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 1200.0, 'label_13')
            emit_command(0x0031, [-0x000004B0], Variables[0x1002])
            emit_command(0x0033, [0x200C, 0x01], Variables[0x3000])
            Variables[0xCDA6] = 1.0
            branch('label_7')

            label('label_15', manager=fevent_manager)
            #Gives the Silver Badge
            branch_if(Variables[0xCDA7], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 3000.0, 'label_13')
            emit_command(0x0031, [-0x00000BB8], Variables[0x1002])
            emit_command(0x0033, [0x2004, 0x01], Variables[0x3000])
            Variables[0xCDA7] = 1.0
            branch('label_7')

            label('label_16', manager=fevent_manager)
            #Gives the Expert Badge
            branch_if(Variables[0xCDA8], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 5000.0, 'label_13')
            emit_command(0x0031, [-0x00001388], Variables[0x1002])
            emit_command(0x0033, [0x2002, 0x01], Variables[0x3000])
            Variables[0xCDA8] = 1.0
            branch('label_7')

            label('label_17', manager=fevent_manager)
            #Gives the Miracle Badge
            branch_if(Variables[0xCDA9], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 5000.0, 'label_13')
            emit_command(0x0031, [-0x00001388], Variables[0x1002])
            emit_command(0x0033, [0x200D, 0x01], Variables[0x3000])
            Variables[0xCDA9] = 1.0
            branch('label_7')

            label('label_18', manager=fevent_manager)
            #Gives the Gold Badge
            branch_if(Variables[0xCDAA], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 10000.0, 'label_13')
            emit_command(0x0031, [-0x00002710], Variables[0x1002])
            emit_command(0x0033, [0x2005, 0x01], Variables[0x3000])
            Variables[0xCDAA] = 1.0
            branch('label_7')

            label('label_6', manager=fevent_manager)
            #Message for if you already have the badge you tried to buy
            say(0x06, TextboxSoundsPreset.TOAD, 'Sir, you already have that badge.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            branch('label_0')

            label('label_7', manager=fevent_manager)
            #Message for when you buy the badge
            say(0x06, TextboxSoundsPreset.TOAD, 'Thank you for your service...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            branch('label_0')

            label('label_13', manager=fevent_manager)
            #Message for if you don't have enough coins
            say(0x06, TextboxSoundsPreset.TOAD, 'Sir, you don\'t have enough coins.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)
            branch('label_0')

            label('label_2', manager=fevent_manager)
            #Message for if you're done browsing
            say(0x06, TextboxSoundsPreset.TOAD, 'Thank you, sirs...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.TOP_LEFT)

            label('label_1', manager=fevent_manager)
            set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
            set_movement_multipliers(Screen.TOP, 1.0, 1.0)
            set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
            set_touches_blocked(False)

        script.header.actors[7] = (0x0000040B, 0x0004042E, 0xFFFF0004, 0xFFFFFFFF, len(script.subroutines)-1, 0x0090010A)
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(15)

        # Changes Dozing Sands's badge shop to be Toadsworth's Overpriced Badge Shop
        script = fevent_manager.parsed_script(0x005D, 0)
        script_index = 0x005D * 2

        # Workaround for dynamic scope in Nuitka
        if '__compiled__' in globals():
            inspect.currentframe().f_locals['script_index'] = script_index

        @subroutine(subs=script.subroutines, hdr=script.header)
        def buy_overpriced_badges(sub: Subroutine):
            set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
            set_movement_multipliers(Screen.TOP, 0.0, 0.0)
            set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
            set_touches_blocked(True)
            branch_if(Variables[0xCDA0], '==', 1.0, 'label_0')
            #Intro dialogue
            Variables[0xCDA0] = 1.0
            say(0x02, TextboxSoundsPreset.TOAD, 'Oh, great, it\'s YOU guys.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Yeah, thanks SO MUCH for supporting us\nduring the financial crash of 2021.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Thanks to you, we had to sell\nthe business to Toadsworth![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'All I can say is, if you don\'t like\nthese prices, you know who to blame.[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Anyway...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)

            label('label_0', manager=fevent_manager)
            #Choose a badge - page 1
            say(0x02, TextboxSoundsPreset.TOAD, 'What will it be?\n[Option][Indent 10]Strike Badge - 400 coins\n[Option][Indent 10]Guard Badge - 500 coins\n[Option][Indent 10]Bronze Badge - 500 coins\n' +
                                                '[Option][Indent 10]Virus Badge - 800 coins\n[Option][Indent 10]Master Badge - 1200 coins\n[Option][Indent 10]Next Page\n[Option][Indent 10]Never mind', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 6.0, 'label_2')
            branch_if(Variables[0x1000], '==', 5.0, 'label_3')
            branch('label_4')

            label('label_4', manager=fevent_manager)
            #Confirmation - page 1
            Variables[0x1001] = Variables[0x1000]
            say(0x02, TextboxSoundsPreset.TOAD, 'This one calling your name?\n[Option][Indent 10]Yes\n[Option][Indent 10]No', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 1.0, 'label_0')
            branch_if(Variables[0x1001], '==', 0.0, 'label_8')
            branch_if(Variables[0x1001], '==', 1.0, 'label_9')
            branch_if(Variables[0x1001], '==', 2.0, 'label_10')
            branch_if(Variables[0x1001], '==', 3.0, 'label_11')
            branch_if(Variables[0x1001], '==', 4.0, 'label_12')

            label('label_8', manager=fevent_manager)
            #Gives the Strike Badge
            branch_if(Variables[0xCDA1], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 400.0, 'label_13')
            emit_command(0x0031, [-0x00000190], Variables[0x1002])
            emit_command(0x0033, [0x2009, 0x01], Variables[0x3000])
            Variables[0xCDA1] = 1.0
            branch('label_7')

            label('label_9', manager=fevent_manager)
            #Gives the Guard Badge
            branch_if(Variables[0xCDA2], '==', 1.0, 'label_9')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 500.0, 'label_13')
            emit_command(0x0031, [-0x000001F4], Variables[0x1002])
            emit_command(0x0033, [0x200A, 0x01], Variables[0x3000])
            Variables[0xCDA2] = 1.0
            branch('label_7')

            label('label_10', manager=fevent_manager)
            #Gives the Bronze Badge
            branch_if(Variables[0xCDA3], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 500.0, 'label_13')
            emit_command(0x0031, [-0x000001F4], Variables[0x1002])
            emit_command(0x0033, [0x2003, 0x01], Variables[0x3000])
            Variables[0xCDA3] = 1.0
            branch('label_7')

            label('label_11', manager=fevent_manager)
            #Gives the Virus Badge
            branch_if(Variables[0xCDA4], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 800.0, 'label_13')
            emit_command(0x0031, [-0x00000320], Variables[0x1002])
            emit_command(0x0033, [0x200B, 0x01], Variables[0x3000])
            Variables[0xCDA4] = 1.0
            branch('label_7')

            label('label_12', manager=fevent_manager)
            #Gives the Master Badge
            branch_if(Variables[0xCDA5], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 1200.0, 'label_13')
            emit_command(0x0031, [-0x000004B0], Variables[0x1002])
            emit_command(0x0033, [0x2001, 0x01], Variables[0x3000])
            Variables[0xCDA5] = 1.0
            branch('label_7')

            label('label_3', manager=fevent_manager)
            #Choose a badge - page 2
            say(0x02, TextboxSoundsPreset.TOAD, 'Ooo, a big spender, are ya?\n[Option][Indent 10]Risk Badge - 1200 coins\n[Option][Indent 10]Silver Badge - 3000 coins\n[Option][Indent 10]Expert Badge - 5000 coins\n' +
                                                '[Option][Indent 10]Miracle Badge - 5000 coins\n[Option][Indent 10]Gold Badge - 10000 coins\n[Option][Indent 10]Previous Page\n[Option][Indent 10]Never mind', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 6.0, 'label_2')
            branch_if(Variables[0x1000], '==', 5.0, 'label_0')
            branch('label_5')

            label('label_5', manager=fevent_manager)
            #Confirmation - page 2
            Variables[0x1001] = Variables[0x1000]
            say(0x02, TextboxSoundsPreset.TOAD, 'This one calling your name?\n[Option][Indent 10]Yes\n[Option][Indent 10]No', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 1.0, 'label_0')
            branch_if(Variables[0x1001], '==', 0.0, 'label_14')
            branch_if(Variables[0x1001], '==', 1.0, 'label_15')
            branch_if(Variables[0x1001], '==', 2.0, 'label_16')
            branch_if(Variables[0x1001], '==', 3.0, 'label_17')
            branch_if(Variables[0x1001], '==', 4.0, 'label_18')

            label('label_14', manager=fevent_manager)
            #Gives the Risk Badge
            branch_if(Variables[0xCDA6], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 1200.0, 'label_13')
            emit_command(0x0031, [-0x000004B0], Variables[0x1002])
            emit_command(0x0033, [0x200C, 0x01], Variables[0x3000])
            Variables[0xCDA6] = 1.0
            branch('label_7')

            label('label_15', manager=fevent_manager)
            #Gives the Silver Badge
            branch_if(Variables[0xCDA7], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 3000.0, 'label_13')
            emit_command(0x0031, [-0x00000BB8], Variables[0x1002])
            emit_command(0x0033, [0x2004, 0x01], Variables[0x3000])
            Variables[0xCDA7] = 1.0
            branch('label_7')

            label('label_16', manager=fevent_manager)
            #Gives the Expert Badge
            branch_if(Variables[0xCDA8], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 5000.0, 'label_13')
            emit_command(0x0031, [-0x00001388], Variables[0x1002])
            emit_command(0x0033, [0x2002, 0x01], Variables[0x3000])
            Variables[0xCDA8] = 1.0
            branch('label_7')

            label('label_17', manager=fevent_manager)
            #Gives the Miracle Badge
            branch_if(Variables[0xCDA9], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 5000.0, 'label_13')
            emit_command(0x0031, [-0x00001388], Variables[0x1002])
            emit_command(0x0033, [0x200D, 0x01], Variables[0x3000])
            Variables[0xCDA9] = 1.0
            branch('label_7')

            label('label_18', manager=fevent_manager)
            #Gives the Gold Badge
            branch_if(Variables[0xCDAA], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 10000.0, 'label_13')
            emit_command(0x0031, [-0x00002710], Variables[0x1002])
            emit_command(0x0033, [0x2005, 0x01], Variables[0x3000])
            Variables[0xCDAA] = 1.0
            branch('label_7')

            label('label_6', manager=fevent_manager)
            #Message for if you already have the badge you tried to buy
            say(0x02, TextboxSoundsPreset.TOAD, 'Look, I know you\'re eager to give me coins,\nbut you already have that badge![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            branch('label_0')

            label('label_7', manager=fevent_manager)
            #Message for when you buy the badge
            say(0x02, TextboxSoundsPreset.TOAD, 'Yes! CHA-CHING! I\'ll be eating happy tonight![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            branch('label_0')

            label('label_13', manager=fevent_manager)
            #Message for if you don't have enough coins
            say(0x02, TextboxSoundsPreset.TOAD, 'Ah, you think you can scam me again, don\'t you?[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            branch('label_0')

            label('label_2', manager=fevent_manager)
            #Message for if you're done browsing
            say(0x02, TextboxSoundsPreset.TOAD, 'Thanks for actually stopping by this time![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)

            label('label_1', manager=fevent_manager)
            set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
            set_movement_multipliers(Screen.TOP, 1.0, 1.0)
            set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
            set_touches_blocked(False)

        script.header.actors[3] = (0x000002AA, 0x000602C1, 0xFFFF0001, 0xFFFFFFFF, len(script.subroutines)-1, 0x0090010A)
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(15)

        # Changes Wakeport's badge shop to be Toadsworth's Overpriced Badge Shop
        script = fevent_manager.parsed_script(0x0043, 0)
        script_index = 0x0043 * 2

        # Workaround for dynamic scope in Nuitka
        if '__compiled__' in globals():
            inspect.currentframe().f_locals['script_index'] = script_index

        @subroutine(subs=script.subroutines, hdr=script.header)
        def buy_overpriced_badges(sub: Subroutine):
            set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
            set_movement_multipliers(Screen.TOP, 0.0, 0.0)
            set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
            set_touches_blocked(True)
            branch_if(Variables[0xCDA0], '==', 1.0, 'label_0')
            #Intro dialogue
            Variables[0xCDA0] = 1.0
            say(0x02, TextboxSoundsPreset.TOAD, 'Oh, hey! Welcome back, Mario and Luigi![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Man, I\'m so happy! I thought we were done for\nafter the financial crash of 2021![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Luckily, Toadsworth swooped in\nto save our business![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Unfortunately, our prices went up by quite a bit,\nbut at least we\'re still here![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            say(0x02, TextboxSoundsPreset.TOAD, 'Anyway...[Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)

            label('label_0', manager=fevent_manager)
            #Choose a badge - page 1
            say(0x02, TextboxSoundsPreset.TOAD, 'What can I get for you?\n[Option][Indent 10]Strike Badge - 400 coins\n[Option][Indent 10]Guard Badge - 500 coins\n[Option][Indent 10]Bronze Badge - 500 coins\n' +
                                                '[Option][Indent 10]Virus Badge - 800 coins\n[Option][Indent 10]Master Badge - 1200 coins\n[Option][Indent 10]Next Page\n[Option][Indent 10]Never mind', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 6.0, 'label_2')
            branch_if(Variables[0x1000], '==', 5.0, 'label_3')
            branch('label_4')

            label('label_4', manager=fevent_manager)
            #Confirmation - page 1
            Variables[0x1001] = Variables[0x1000]
            say(0x02, TextboxSoundsPreset.TOAD, 'Does this look right?\n[Option][Indent 10]Yes\n[Option][Indent 10]No', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 1.0, 'label_0')
            branch_if(Variables[0x1001], '==', 0.0, 'label_8')
            branch_if(Variables[0x1001], '==', 1.0, 'label_9')
            branch_if(Variables[0x1001], '==', 2.0, 'label_10')
            branch_if(Variables[0x1001], '==', 3.0, 'label_11')
            branch_if(Variables[0x1001], '==', 4.0, 'label_12')

            label('label_8', manager=fevent_manager)
            #Gives the Strike Badge
            branch_if(Variables[0xCDA1], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 400.0, 'label_13')
            emit_command(0x0031, [-0x00000190], Variables[0x1002])
            emit_command(0x0033, [0x2009, 0x01], Variables[0x3000])
            Variables[0xCDA1] = 1.0
            branch('label_7')

            label('label_9', manager=fevent_manager)
            #Gives the Guard Badge
            branch_if(Variables[0xCDA2], '==', 1.0, 'label_9')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 500.0, 'label_13')
            emit_command(0x0031, [-0x000001F4], Variables[0x1002])
            emit_command(0x0033, [0x200A, 0x01], Variables[0x3000])
            Variables[0xCDA2] = 1.0
            branch('label_7')

            label('label_10', manager=fevent_manager)
            #Gives the Bronze Badge
            branch_if(Variables[0xCDA3], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 500.0, 'label_13')
            emit_command(0x0031, [-0x000001F4], Variables[0x1002])
            emit_command(0x0033, [0x2003, 0x01], Variables[0x3000])
            Variables[0xCDA3] = 1.0
            branch('label_7')

            label('label_11', manager=fevent_manager)
            #Gives the Virus Badge
            branch_if(Variables[0xCDA4], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 800.0, 'label_13')
            emit_command(0x0031, [-0x00000320], Variables[0x1002])
            emit_command(0x0033, [0x200B, 0x01], Variables[0x3000])
            Variables[0xCDA4] = 1.0
            branch('label_7')

            label('label_12', manager=fevent_manager)
            #Gives the Master Badge
            branch_if(Variables[0xCDA5], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 1200.0, 'label_13')
            emit_command(0x0031, [-0x000004B0], Variables[0x1002])
            emit_command(0x0033, [0x2001, 0x01], Variables[0x3000])
            Variables[0xCDA5] = 1.0
            branch('label_7')

            label('label_3', manager=fevent_manager)
            #Choose a badge - page 2
            say(0x02, TextboxSoundsPreset.TOAD, 'We also have these!\n[Option][Indent 10]Risk Badge - 1200 coins\n[Option][Indent 10]Silver Badge - 3000 coins\n[Option][Indent 10]Expert Badge - 5000 coins\n' +
                                                '[Option][Indent 10]Miracle Badge - 5000 coins\n[Option][Indent 10]Gold Badge - 10000 coins\n[Option][Indent 10]Previous Page\n[Option][Indent 10]Never mind', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 6.0, 'label_2')
            branch_if(Variables[0x1000], '==', 5.0, 'label_0')
            branch('label_5')

            label('label_5', manager=fevent_manager)
            #Confirmation - page 2
            Variables[0x1001] = Variables[0x1000]
            say(0x02, TextboxSoundsPreset.TOAD, 'Does this look right?\n[Option][Indent 10]Yes\n[Option][Indent 10]No', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
            branch_if(Variables[0x1000], '==', 1.0, 'label_0')
            branch_if(Variables[0x1001], '==', 0.0, 'label_14')
            branch_if(Variables[0x1001], '==', 1.0, 'label_15')
            branch_if(Variables[0x1001], '==', 2.0, 'label_16')
            branch_if(Variables[0x1001], '==', 3.0, 'label_17')
            branch_if(Variables[0x1001], '==', 4.0, 'label_18')

            label('label_14', manager=fevent_manager)
            #Gives the Risk Badge
            branch_if(Variables[0xCDA6], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 1200.0, 'label_13')
            emit_command(0x0031, [-0x000004B0], Variables[0x1002])
            emit_command(0x0033, [0x200C, 0x01], Variables[0x3000])
            Variables[0xCDA6] = 1.0
            branch('label_7')

            label('label_15', manager=fevent_manager)
            #Gives the Silver Badge
            branch_if(Variables[0xCDA7], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 3000.0, 'label_13')
            emit_command(0x0031, [-0x00000BB8], Variables[0x1002])
            emit_command(0x0033, [0x2004, 0x01], Variables[0x3000])
            Variables[0xCDA7] = 1.0
            branch('label_7')

            label('label_16', manager=fevent_manager)
            #Gives the Expert Badge
            branch_if(Variables[0xCDA8], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 5000.0, 'label_13')
            emit_command(0x0031, [-0x00001388], Variables[0x1002])
            emit_command(0x0033, [0x2002, 0x01], Variables[0x3000])
            Variables[0xCDA8] = 1.0
            branch('label_7')

            label('label_17', manager=fevent_manager)
            #Gives the Miracle Badge
            branch_if(Variables[0xCDA9], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 5000.0, 'label_13')
            emit_command(0x0031, [-0x00001388], Variables[0x1002])
            emit_command(0x0033, [0x200D, 0x01], Variables[0x3000])
            Variables[0xCDA9] = 1.0
            branch('label_7')

            label('label_18', manager=fevent_manager)
            #Gives the Gold Badge
            branch_if(Variables[0xCDAA], '==', 1.0, 'label_6')
            emit_command(0x0030, [], Variables[0x1002])
            branch_if(Variables[0x1002], '<', 10000.0, 'label_13')
            emit_command(0x0031, [-0x00002710], Variables[0x1002])
            emit_command(0x0033, [0x2005, 0x01], Variables[0x3000])
            Variables[0xCDAA] = 1.0
            branch('label_7')

            label('label_6', manager=fevent_manager)
            #Message for if you already have the badge you tried to buy
            say(0x02, TextboxSoundsPreset.TOAD, 'Sorry, you already have that badge![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            branch('label_0')

            label('label_7', manager=fevent_manager)
            #Message for when you buy the badge
            say(0x02, TextboxSoundsPreset.TOAD, 'Thank you so much, sirs![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            branch('label_0')

            label('label_13', manager=fevent_manager)
            #Message for if you don't have enough coins
            say(0x02, TextboxSoundsPreset.TOAD, 'Sorry, you don\'t have enough coins![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)
            branch('label_0')

            label('label_2', manager=fevent_manager)
            #Message for if you're done browsing
            say(0x02, TextboxSoundsPreset.TOAD, 'Have a nice day![Wait]', tail=TextboxTailType.SMALL, alignment=TextboxAlignment.BOTTOM_CENTER)

            label('label_1', manager=fevent_manager)
            set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
            set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
            set_movement_multipliers(Screen.TOP, 1.0, 1.0)
            set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
            set_touches_blocked(False)

        script.header.actors[3] = (0x00000177, 0x0000018E, 0xFFFF0001, 0xFFFFFFFF, len(script.subroutines)-1, 0x0050010E)
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
        sbar.update(15)

    #Fixes attack piece blocks
    with tqdm(total=1744, desc="Fixing blocks and softlocks......") as fbar:
        attack_dat = [0x004, 0x005, 0x010, 0x011, 0x012, 0x013, 0x014, 0x017, 0x019, 0x01F, 0x020, 0x021, 0x022, 0x027, 0x028, 0x02A,
                      0x034, 0x035, 0x036, 0x038, 0x039, 0x03A, 0x03B, 0x03D, 0x040, 0x04B, 0x04C, 0x04D, 0x04F, 0x062, 0x069, 0x06A, 0x06C,
                      0x06D, 0x06F, 0x070, 0x072, 0x075, 0x076, 0x079, 0x07C, 0x0BB, 0x0BD, 0x0BE, 0x0C4, 0x0C5, 0x0C6, 0x0D2, 0x0D6, 0x0E4,
                      0x0F5, 0x0F6, 0x0FA, 0x10C, 0x124, 0x125, 0x126, 0x127, 0x128, 0x129, 0x12A, 0x13D, 0x144, 0x145, 0x146, 0x147, 0x148,
                      0x14B, 0x14C, 0x14E, 0x14F, 0x161, 0x164, 0x165, 0x167, 0x168, 0x16C, 0x177, 0x17A, 0x17D, 0x187, 0x188, 0x189, 0x18A,
                      0x18B, 0x18F, 0x190, 0x192, 0x194, 0x1E7, 0x1F0, 0x1F1, 0x1F2, 0x1F4, 0x1F6, 0x1F7, 0x1F8, 0x1F9, 0x1FA, 0x204, 0x22A,
                      0x22B, 0x22C, 0x22D, 0x22E, 0x22F, 0x231, 0x232, 0x233, 0x295,]

        #print(i[1])
        for i in attack_dat:
            #print(i)
            script = fevent_manager.parsed_script(i, 0)
            @subroutine(subs=script.subroutines, hdr=script.header)
            def rid_block(sub: Subroutine):
                set_actor_attribute(Variables[0x7007], 0x00, 0.0)
                set_actor_attribute(Variables[0x7007], 0x01, 0.0)
            #Exceptions for camera blocks
            if i == 0x040:
                actor_blacklist = [6]
            elif i == 0x04D:
                actor_blacklist = [18]
            elif i == 0x072:
                actor_blacklist = [26]
            elif i == 0x144:
                #First is a camera block, second is a Kamek block
                actor_blacklist = [18, 20]
            elif i == 0x188:
                actor_blacklist = [7]
            #Exceptions for save blocks
            elif i == 0x03A:
                actor_blacklist = [28]
            elif i == 0x18b:
                actor_blacklist = [23]
            #Exceptions for Dozing Sands track calling blocks
            elif i == 0x010:
                actor_blacklist = [11]
            elif i == 0x013:
                actor_blacklist = [19]
            elif i == 0x014:
                actor_blacklist = [11]
            elif i == 0x019:
                actor_blacklist = [19]
            #Exceptions for Kamek blocks
            elif i == 0x145:
                actor_blacklist = [3]
            elif i == 0x146:
                actor_blacklist = [3]
            elif i == 0x147:
                actor_blacklist = [3]
            #No exceptions, no list
            else:
                actor_blacklist = []
            for a in range(len(script.header.actors)):
                if (script.header.actors[a][5] // 0x1000) % 0x1000 == 0x748 and script.header.actors[a][5] % 0x100 == 0x43:
                    try:
                        actor_blacklist.index(a)
                        #print(hex(i) + " " + str(a))
                    except ValueError:
                        temp_list = list(script.header.actors[a])
                        temp_list[2] = (len(script.subroutines) - 1) * 0x10000 + temp_list[2] % 0x10000
                        script.header.actors[a] = tuple(temp_list)
            fbar.update(1)

        # An array of every block, bean spot, and dream world block in Dream Team
        spot_info = [[[0xf, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0x11, 0x13], [0x10, 0x12, 0x14, 0x15, 0x16, 0x17], []],

                     [[0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28,
                       0x29, 0x2a, 0x2b, 0x2d, 0x2e, 0x2f, 0x94f, 0x950, 0x951, 0x952, 0x953], [], [0x9d, 0x9e, 0x9f,
                       0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa8, 0xa9, 0xab, 0xad, 0xaf, 0xb1, 0x66b, 0xb8, 0xb9, 0xba, 0xbb, 0xbc,
                       0xbd, 0xbf, 0xc1, 0xc3, 0xc5, 0xc7, 0xc9, 0xcb, 0xcd, 0xcf, 0xd1, 0xd3, 0xd5, 0xd7, 0xd9, 0xdb, 0xdd, 0xdf,
                       0xe1, 0xe3, 0xe5, 0xe7, 0xe9, 0xeb, 0xec, 0xed, 0xee, 0xf5, 0xf6, 0x910, 0x911, 0x35d, 0x35e, 0x912]],

                     [[0x34, 0x35, 0x0, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3e, 0x3f, 0x40, 0x41, 0x1, 0x2, 0x3, 0x4, 0x42,
                       0x5, 0x6, 0x2c, 0x30, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4e, 0x4f, 0x50, 0x51, 0x56, 0x57, 0x58, 0x59,
                       0x5b, 0x5c, 0x5e, 0x5f, 0x60, 0x61, 0x62, 0x955, 0x67, 0x68, 0x6b, 0x956, 0x957, 0x70, 0x71, 0x72,
                       0x73, 0x74, 0x75], [0x3b, 0x3c, 0x3d, 0x954, 0x43, 0x4b, 0x4c, 0x4d, 0x52, 0x53, 0x54, 0x55, 0x5a, 0x63, 0x64,
                       0x65, 0x66, 0x6c, 0x6d, 0x6e, 0x6f, 0x76], [0x8c, 0x77, 0x79, 0x7b, 0x7d, 0xb3, 0x7f, 0x81, 0xb4, 0x83, 0xb5,
                       0x84, 0x958, 0x8d, 0x8e, 0xb6, 0x90, 0x9c, 0xb7, 0x959, 0x91, 0x92, 0x1c5, 0x93, 0x98, 0x95a, 0x95b, 0x97, 0x94]],

                     [[0x31, 0x111, 0x112, 0x113, 0x32, 0x115, 0x116, 0x33, 0x5d, 0x69, 0x6a, 0x11a, 0x11b, 0x11c,
                       0x86, 0x11f, 0x120, 0x121, 0x122, 0x123, 0x87, 0x125, 0x945, 0x88, 0x89, 0x12f, 0x130, 0x131, 0x132,
                       0x8a, 0x8b, 0x134, 0x135, 0x136, 0x137, 0x138, 0x946, 0x139, 0x13a, 0xff, 0x100, 0x101, 0x102, 0x104,
                       0x105, 0x106, 0x10d, 0x10e, 0x209, 0x10a, 0x10b, 0x13b, 0x13c, 0x13e, 0x143, 0x144, 0x95c, 0x145, 0x146,
                       0x13f, 0x140, 0x14d, 0x14e, 0x14f, 0x150, 0x151, 0x12c, 0x12d, 0x12e], [0xfd, 0x10f, 0x110, 0x114, 0x3c9,
                       0x117, 0x119, 0x11d, 0x11e, 0x124, 0x126, 0x127, 0x128, 0x133, 0xfe, 0x103, 0x107, 0x108, 0x10c, 0x109,
                       0x13d, 0x91a, 0x3db, 0x147, 0x148, 0x149, 0x14a, 0x14b, 0x14c, 0x129, 0x12a, 0x12b], [0x19d, 0x19e, 0x1c4, 0x1cd,
                       0x1ce, 0x1cf, 0x1c2, 0x1d0, 0x1e6, 0x903, 0x904, 0x905, 0x200, 0x201, 0x906, 0x907, 0x20b, 0x211,
                       0x221, 0x222, 0x908, 0x909, 0x90a, 0x90b, 0x238, 0x239, 0x90e, 0x90f, 0x241, 0x242, 0x243, 0x244,
                       0x245, 0x246, 0x247, 0x248, 0x249, 0x96d]],

                     [[0x5e7, 0x1c6, 0x5ea, 0x1c7, 0x1c8, 0x5ef, 0x1c9, 0x1ca, 0x5f2, 0x5f3, 0x5f4, 0x5f5,
                       0x1cc, 0x5f7, 0x5f8, 0x5f9, 0x5fa, 0x5fb, 0x5fc, 0x603, 0x202, 0x604, 0x605, 0x606, 0x203, 0x5e2, 0x5e3, 0x5e4, 0x5e5,
                       0x5fd, 0x5fe, 0x5ff, 0x600, 0x601, 0x602, 0x5f6], [0x5e8, 0x5e9, 0x5eb, 0x5ec, 0x5ed, 0x5ee, 0x5f0, 0x5f1, 0x5e6,
                       0x921, 0x922, 0x923], [0x25f, 0x260, 0x261, 0x262, 0x263, 0x264, 0x265,
                       0x266, 0x267, 0x268, 0x269, 0x26a, 0x26b, 0x26c, 0x26d, 0x26e, 0x26f, 0x270, 0x271, 0x272, 0x273, 0x579, 0x57a,
                       0x274, 0x275, 0x276, 0x914, 0x915, 0x916, 0x917, 0x918, 0x919, 0xf3, 0x2b9, 0xf4, 0x2bc, 0x2bd, 0x96c,
                       0x2d6, 0x2d7, 0x2d8, 0x2f8, 0x2f9, 0x2fc, 0x2fd, 0x2f2, 0x2f3, 0x2f4, 0x2f5, 0x2f6, 0x2f7, 0x9a3]],

                     [[0x625, 0x626, 0x627, 0x628, 0x629, 0x20a, 0x62a, 0x20c, 0x62d, 0x62e, 0x20d, 0x20e, 0x630, 0x632,
                       0x20f, 0x633, 0x634, 0x635, 0x636, 0x638, 0x963, 0x210, 0xea, 0x63b, 0x63c, 0x63d, 0xef, 0x60a, 0x63e, 0x63f, 0x8ab, 0x91d,
                       0xf0, 0x642, 0xf1, 0x643, 0x644, 0x646, 0x648, 0xf2, 0x649, 0x64a, 0x947, 0x64b, 0x64c, 0x64e, 0x64f, 0x650, 0x651, 0x902,
                       0x655, 0x657, 0x658, 0x964, 0x659, 0x65a, 0x65b, 0x913], [0x62b, 0x62c, 0x62f, 0x962, 0x631, 0x637, 0x639, 0x63a, 0x640, 0x641,
                       0x91e, 0x645, 0x647, 0x937, 0x938, 0x64d, 0x652, 0x939, 0x93a, 0x653, 0x654, 0x8f8, 0x65c, 0x65d], [0x36f, 0x370, 0x98d,
                       0x390, 0x391, 0x392, 0x393, 0x394, 0x6f6, 0x6dc, 0x395, 0x396, 0x397, 0x399, 0x39a, 0x39b, 0x39c, 0x39d, 0x39e, 0x98e,
                       0x39f, 0x3a0, 0x3a1, 0x98f, 0x990, 0x3a2, 0x3a3, 0x3a4, 0x3a5, 0x991, 0x70e, 0x70f, 0x3a8, 0x3a9, 0x3aa, 0x992,
                       0x3ab, 0x3ac, 0x993, 0x3ad, 0x3ae, 0x3af, 0x3b0, 0x994, 0x995, 0x3b9, 0x996, 0x3ba, 0x997, 0x3c1, 0x3c2,
                       0x3c5, 0x3c6, 0x3c7, 0x3c8, 0x95d, 0x3ca, 0x3cb, 0x3cc, 0x3d0, 0x3d1, 0x3d8, 0x3d9, 0x77b, 0x398, 0x998, 0x3da, 0x3dd,
                       0x3de, 0x3df, 0x3e0, 0x41a, 0x41b]],

                     [[0x1cb, 0x60d, 0x60e, 0x60f, 0x1e3, 0x1e4, 0x611, 0x612, 0x91b, 0x91c, 0x1e5, 0x61a, 0x61e, 0x61f, 0x620, 0x621, 0x622,
                       0x607, 0x608, 0x609, 0x95e, 0x204, 0x60b, 0x95f, 0x205, 0x613, 0x614, 0x616, 0x206, 0x207, 0x617, 0x618, 0x208, 0x61b, 0x61c],
                      [0x610, 0x623, 0x624, 0x60c, 0x615, 0x960, 0x619, 0x961, 0x3dc, 0x61d], [0x90c, 0x4db, 0x4e2, 0x4e3, 0x4e4, 0x90d,
                       0x4eb, 0x979, 0x97a, 0x4f5, 0x4f6, 0x97b, 0x45e, 0x45f, 0x4fb, 0x4fc, 0x4fd, 0x97c, 0x97d, 0x97e, 0x49e, 0x501,
                       0x505, 0x97f, 0x980, 0x510, 0x511, 0x981, 0x53b, 0x53c, 0x53d, 0x982, 0x983, 0x568, 0x569,
                       0x56a, 0x56b, 0x56c, 0x56d, 0x573, 0x574, 0x512, 0x51a]],

                     [[0x82c, 0x82e, 0x82f, 0x831, 0x832, 0x833, 0x834, 0x836, 0x837, 0x838, 0x984, 0x839, 0x985, 0x83c, 0x986, 0x83d, 0x987, 0x988,
                       0x83e, 0x83f, 0x841, 0x842, 0x843, 0x844, 0x847, 0x989, 0x848, 0x98a, 0x849, 0x84a, 0x98b, 0x84d, 0x84e, 0x98c,
                       0x850, 0x851, 0x852, 0x853], [0x82d, 0x830, 0x835, 0x83a, 0x83b, 0x840, 0x845, 0x846, 0x84b, 0x84c, 0x84f, 0x96a, 0x96b,
                       0x854, 0x855, 0x856, 0x857, 0x858, 0x859], [0x821, 0x7b0, 0x7b1, 0x7b2, 0x7b3, 0x7b4, 0x7b5, 0x7b6, 0x7d8, 0x7d9, 0x7da,
                       0x7e0, 0x7e1, 0x7e2, 0x7e3, 0x7e4, 0x7e5, 0x7e6, 0x7e7, 0x999, 0x7e8, 0x7e9, 0x7ea, 0x7eb, 0x7ec, 0x7ed, 0x7ee, 0x99a, 0x99b,
                       0x7ef, 0x7f3, 0x99c, 0x99d, 0x7f4, 0x803, 0x804, 0x805, 0x99e, 0x806, 0x933, 0x80a, 0x80b, 0x99f, 0x9a0,
                       0x80c, 0x80d, 0x80e, 0x80f, 0x9a1, 0x812, 0x813, 0x9a2, 0x825, 0x826, 0x827, 0x828, 0x829, 0x82a, 0x82b, 0x91f, 0x920]],

                     [[0x65e, 0x65f, 0x660, 0x661, 0x96e, 0x662, 0x96f, 0x663, 0x970, 0x971, 0x664, 0x665, 0x666, 0x972, 0x118, 0x142, 0x66a,
                       0x93b, 0x93c, 0x93d, 0x93e, 0x93f, 0x973, 0x974, 0x66e, 0x66f, 0x975, 0x976, 0x965, 0x966, 0x967, 0x977,
                       0x673, 0x674, 0x8f9, 0x8fa, 0x978, 0x677, 0x678, 0x679, 0x67a, 0x67d, 0x949, 0x94a, 0x67f, 0x680, 0x94c, 0x94d,
                       0x681, 0x682, 0x683, 0x686, 0x687, 0x688, 0x689, 0x68a, 0x68b, 0x675, 0x676, 0x940, 0x941, 0x948], [0x667, 0x668,
                       0x669, 0x670, 0x671, 0x67b, 0x67c, 0x67e, 0x94b, 0x932, 0x684, 0x685, 0x968, 0x969, 0x68c, 0x68d, 0x68e, 0x68f],
                      [0x85a, 0x85b, 0x85c, 0x85d, 0x85e, 0x85f, 0x860, 0x861, 0x862, 0x863, 0x89b, 0x89c, 0x89d, 0x89e, 0x89f, 0x8a0, 0x8a1,
                       0x8a2, 0x8a3, 0x934, 0x8a4, 0x8a7, 0x8a8, 0x8a9, 0x8aa, 0x935, 0x8ac, 0x8b6, 0x8b7, 0x8b8, 0x8bf, 0x8c5, 0x8c6, 0x8c7,
                       0x8e1, 0x8e2, 0x8e3, 0x8e4, 0x8e5, 0x94e, 0x8f5, 0x8f6, 0x8f7]]]

        #The length of each item type within each array, and the resulting offset for the next room
        room_lengths = [[[1, 0, 4, 0, 4, 0, 0, 1, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 1, 4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],

                        [[0, 0, 0, 0, 2, 0, 2, 1, 1, 0, 0, 1, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 1, 2, 4, 4],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 5, 0, 0, 0, 0, 0, 1, 7, 0, 2, 25, 1, 4, 2, 0, 0, 1, 1, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0]],

                        [[2, 6, 2, 2, 5, 8, 3, 4, 4, 2, 6, 5, 3, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                         [0, 4, 0, 0, 1, 0, 3, 4, 1, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 3, 2, 2, 1, 1, 0, 1, 4, 1, 2, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]],

                        [[0, 4, 3, 7, 6, 3, 0, 0, 6, 8, 2, 4, 1, 2, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 3, 2, 2, 0, 0, 0, 0, 5, 3],
                         [1, 2, 2, 2, 2, 4, 0, 0, 0, 1, 0, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 6, 3],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 2, 2, 0, 0, 1, 0, 1, 0, 2, 4, 1, 1, 0, 0, 0, 3, 2, 1, 0, 4, 0, 0, 0, 3, 1, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]],

                        [[1, 2, 3, 6, 0, 7, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0, 4, 2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                         [2, 1, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 3, 3, 2, 5, 0, 2, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 1, 1, 2, 1, 2, 2, 1, 3, 3, 0, 2, 0, 1, 0, 0, 0, 0, 1, 0, 4, 0, 0, 3]],

                        [[3, 0, 2, 2, 2, 1, 4, 5, 2, 1, 4, 0, 6, 0, 0, 2, 3, 1, 1, 4, 2, 2, 3, 0, 0, 0, 0, 2, 2, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 2, 0, 2, 1, 1, 0, 1, 1, 0, 3, 0, 0, 0, 1, 0, 1, 2, 1, 0, 2, 0, 1, 2, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 5, 0, 1, 1, 2, 0, 0, 1, 7, 5, 5, 2, 4, 2, 1, 5, 1, 2, 2, 2, 0, 5, 3, 2, 0, 2, 1, 0, 2, 0, 1, 1, 3, 0, 0, 0, 0, 0, 2, 0, 0]],

                        [[4, 6, 2, 0, 0, 4, 1, 0, 4, 3, 4, 4, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 0, 0, 0, 0, 0, 0, 2, 0, 1, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 4, 2, 0, 0, 1, 3, 2, 4, 2, 0, 1, 1, 3, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 0, 1, 2, 4, 0, 1, 1, 1, 1]],

                        [[0, 0, 0, 1, 2, 2, 2, 4, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 0, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 1, 0, 1, 0, 2, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 3, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 4, 0, 1, 0, 2, 0, 1, 3, 0, 0, 0, 0, 1, 3, 0, 1, 9, 1, 3, 1, 4, 2, 4, 5, 3, 3, 1, 2, 1, 2]],

                        [[0, 0, 0, 2, 3, 2, 2, 1, 4, 2, 1, 7, 4, 0, 4, 5, 4, 0, 0, 3, 0, 4, 2, 0, 1, 0, 2, 1, 3, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 2, 0, 2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 0, 3, 3, 2, 1, 0, 1, 1, 1, 1, 2, 1, 1, 0, 1, 0, 0, 2, 0, 0, 1, 0, 3, 0, 0, 0, 1, 0, 2, 0, 2, 0, 0, 1, 0, 2, 1, 0, 0]]]

        room_local_index = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        room_local_info_index = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        area_names = ["Blimport", "Pi'illo Castle" ,"Mushrise Park", "Dozing Sands", "Wakeport", "Mount Pajamaja", "Driftwood Shore", "Somnom Woods", "Neo Bowser Castle"]

        # Adds the quick warp and tracker features to every room that needs it
        for s in range(0x2B0):
            if get_room(s) != "Unknown":
                script = fevent_manager.parsed_script(s, 0)
                script_index = s * 2

                # Workaround for dynamic scope in Nuitka
                if '__compiled__' in globals():
                    inspect.currentframe().f_locals['script_index'] = script_index

                @subroutine(subs=script.subroutines, hdr=script.header)
                def show_stats(sub: Subroutine):
                    if get_room(s) == "Pi'illo Castle" or get_room(s) == "Dreamy Pi'illo Castle":
                        branch('label_1')
                    elif get_room(s) == "Mushrise Park" or get_room(s) == "Dreamy Mushrise Park":
                        branch('label_2')
                    elif get_room(s) == "Dozing Sands" or get_room(s) == "Dreamy Dozing Sands":
                        branch('label_3')
                    elif get_room(s) == "Wakeport" or get_room(s) == "Dreamy Wakeport":
                        branch('label_4')
                    elif get_room(s) == "Mount Pajamaja" or get_room(s) == "Dreamy Mount Pajamaja":
                        branch('label_5')
                    elif get_room(s) == "Driftwood Shore" or get_room(s) == "Dreamy Driftwood Shore":
                        branch('label_6')
                    elif get_room(s) == "Somnom Woods" or get_room(s) == "Dreamy Somnom Woods":
                        branch('label_7')
                    elif get_room(s) == "Neo Bowser Castle" or get_room(s) == "Dreamy Neo Bowser Castle":
                        branch('label_8')
                    for a in range(len(spot_info)):
                        label('label_' + str(a), manager=fevent_manager)
                        Variables[0x6000] = 0.0
                        Variables[0x6001] = 0.0
                        Variables[0x6002] = 0.0
                        Variables[0x6003] = 0.0
                        total_check = [0, 0, 0]
                        for b in range(len(spot_info[a])):
                            for c in spot_info[a][b]:
                                Variables[0x6000 + b] += Variables[0xD000 + c]
                                total_check[b] += 1
                        Variables[0x6003] += Variables[0x6000]
                        Variables[0x6003] += Variables[0x6001]
                        Variables[0x6003] += Variables[0x6002]
                        if a > 0:
                            prev_area = a-1
                        else:
                            prev_area = len(spot_info)-1
                        if a < len(spot_info)-1:
                            next_area = a+1
                        else:
                            next_area = 0
                        say(None, TextboxSoundsPreset.SILENT, "[DelayOff]Totals for " + area_names[a] + ":\nBlocks:       [Color #2C65FF][Var 0000 digits=3] [Color #000000]/" + str(total_check[0]) +
                            "\nBean Spots:   [Color #2C65FF][Var 0001 digits=3] [Color #000000]/" + str(total_check[1]) +
                            "\nDream Blocks: [Color #2C65FF][Var 0002 digits=3] [Color #000000]/" + str(total_check[2]) +
                            "\nTotal:        [Color #2C65FF][Var 0003 digits=3] [Color #000000]/" + str(total_check[0] + total_check[1] + total_check[2]) +
                            "\n[Option]" + area_names[prev_area] + "   [Option]" + area_names[next_area] + "\n[Option]Room Totals            [Option]Close")
                        emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
                        branch_if(Variables[0x1000], '==', 0.0, 'label_' + str(prev_area))
                        branch_if(Variables[0x1000], '==', 1.0, 'label_' + str(next_area))
                        branch_if(Variables[0x1000], '==', 2.0, 'label_9')
                        branch_if(Variables[0x1000], '==', 3.0, 'label_10')

                    label('label_9', manager=fevent_manager)
                    text_to_print = "[DelayOff]Current Room Stats\n"
                    Variables[0x6000] = 0.0
                    Variables[0x6001] = 0.0
                    Variables[0x6002] = 0.0
                    Variables[0x6003] = 0.0
                    room_id = 0
                    if get_room(s) == "Blimport":
                        room_id = 0
                    elif get_room(s) == "Pi'illo Castle" or get_room(s) == "Dreamy Pi'illo Castle":
                        room_id = 1
                    elif get_room(s) == "Mushrise Park" or get_room(s) == "Dreamy Mushrise Park":
                        room_id = 2
                    elif get_room(s) == "Dozing Sands" or get_room(s) == "Dreamy Dozing Sands":
                        room_id = 3
                    elif get_room(s) == "Wakeport" or get_room(s) == "Dreamy Wakeport":
                        room_id = 4
                    elif get_room(s) == "Mount Pajamaja" or get_room(s) == "Dreamy Mount Pajamaja":
                        room_id = 5
                    elif get_room(s) == "Driftwood Shore" or get_room(s) == "Dreamy Driftwood Shore":
                        room_id = 6
                    elif get_room(s) == "Somnom Woods" or get_room(s) == "Dreamy Somnom Woods":
                        room_id = 7
                    elif get_room(s) == "Neo Bowser Castle" or get_room(s) == "Dreamy Neo Bowser Castle":
                        room_id = 8
                    if get_room(s)[0:5] == "Dream":
                        spot_type = 2
                        #print("Is Dream")
                    else:
                        spot_type = 0
                    rl = room_lengths[room_id][spot_type][room_local_info_index[room_id]]
                    if rl > 0:
                        text_to_print += "Blocks:       [Color #2C65FF][Var 0000 digits=3] [Color #000000]/" + str(rl) + "\n"
                        for l in range(rl):
                            Variables[0x6000] += Variables[0xD000 + spot_info[room_id][spot_type][room_local_index[room_id][spot_type]+l]]
                        room_local_index[room_id][spot_type] += rl
                    if spot_type == 0:
                        spot_type = 1
                        rl = room_lengths[room_id][spot_type][room_local_info_index[room_id]]
                        if rl > 0:
                            text_to_print += "Bean Spots:   [Color #2C65FF][Var 0001 digits=3] [Color #000000]/" + str(rl) + "\n"
                            for l in range(rl):
                                Variables[0x6001] += Variables[0xD000 + spot_info[room_id][spot_type][room_local_index[room_id][spot_type]+l]]
                            room_local_index[room_id][spot_type] += rl
                    room_local_info_index[room_id] += 1
                    say(None, TextboxSoundsPreset.SILENT, text_to_print + "[Option]Overall Stats   [Option]Close")
                    emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
                    if get_room(s) == "Pi'illo Castle" or get_room(s) == "Dreamy Pi'illo Castle":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_1')
                    elif get_room(s) == "Mushrise Park" or get_room(s) == "Dreamy Mushrise Park":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_2')
                    elif get_room(s) == "Dozing Sands" or get_room(s) == "Dreamy Dozing Sands":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_3')
                    elif get_room(s) == "Wakeport" or get_room(s) == "Dreamy Wakeport":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_4')
                    elif get_room(s) == "Mount Pajamaja" or get_room(s) == "Dreamy Mount Pajamaja":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_5')
                    elif get_room(s) == "Driftwood Shore" or get_room(s) == "Dreamy Driftwood Shore":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_6')
                    elif get_room(s) == "Somnom Woods" or get_room(s) == "Dreamy Somnom Woods":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_7')
                    elif get_room(s) == "Neo Bowser Castle" or get_room(s) == "Dreamy Neo Bowser Castle":
                        branch_if(Variables[0x1000], '==', 0.0, 'label_8')
                    else:
                        branch_if(Variables[0x1000], '==', 0.0, 'label_0')
                    branch_if(Variables[0x1000], '==', 1.0, 'label_10')

                    label('label_10', manager=fevent_manager)

                original_world = -1
                if get_dream_origin(s)[0] != -1:
                    original_world = get_dream_origin(s)[0]
                    original_sub = get_dream_origin(s)[1]

                @subroutine(subs=script.subroutines, hdr=script.header)
                def quick_warp(sub: Subroutine):
                    set_actor_attribute(Variables[0x7007], 0x00, 0.0)
                    set_actor_attribute(Variables[0x7007], 0x01, 0.0)
                    if s == 0x01C or s == 0x039 or s == 0x13A:
                        emit_command(0x0126, [0x00, 0x01])
                    label('label_0', manager=fevent_manager)
                    if s != 0x208:
                        if settings[3][1] == 1:
                            Variables[0x1000] = Variables[0x702A] & (ButtonFlags.X + ButtonFlags.L + ButtonFlags.R)
                            branch_if(Variables[0x1000], '==', 1792.0, 'label_1')
                        else:
                            Variables[0x1000] = Variables[0x702A] & ButtonFlags.X
                            branch_if(Variables[0x1000], '==', 1024.0, 'label_1')
                    if settings[3][2] == 1:
                        Variables[0x1000] = Variables[0x702A] & (ButtonFlags.Y + ButtonFlags.L + ButtonFlags.R)
                        branch_if(Variables[0x1000], '==', 2816.0, 'label_4')
                    else:
                        Variables[0x1000] = Variables[0x702A] & ButtonFlags.Y
                        branch_if(Variables[0x1000], '==', 2048.0, 'label_4')
                    wait(1)
                    branch('label_0')

                    label('label_1', manager=fevent_manager)
                    set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
                    set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
                    set_movement_multipliers(Screen.TOP, 0.0, 0.0)
                    set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
                    set_touches_blocked(True)
                    if original_world == -1:
                        say(None, TextboxSoundsPreset.SILENT, "[DelayOff]Go to the Warp Pipe menu?\n[Option]No          [Option]Yes", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    else:
                        say(None, TextboxSoundsPreset.SILENT, "[DelayOff]Go to the Real World?\n[Option]No          [Option]Yes", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    emit_command(0x0008, [Variables[0x6004]], Variables[0x1000])
                    branch_if(Variables[0x1000], '==', 0.0, 'label_2')
                    if original_world == -1:
                        branch_if(Variables[0xC47F], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC480], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC481], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC482], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC483], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC484], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC485], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC486], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC487], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC488], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC489], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC48A], '==', 1.0, 'label_3')
                        branch_if(Variables[0xC4B9], '==', 1.0, 'label_3')
                        set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
                        set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
                        set_movement_multipliers(Screen.TOP, 1.0, 1.0)
                        set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
                        set_touches_blocked(False)
                        say(None, TextboxSoundsPreset.SILENT, "[DelayOff]Unlock a golden pipe first.[Pause 45]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                        branch('label_0')

                        label('label_3', manager=fevent_manager)
                        emit_command(0x00DF, [0x0000FFFF]) #Gets you out of Ball Hop and returns any other state to normal
                        Variables[0xB138] = 0.0 #Resets the platform in Somnom Woods to prevent softlocks
                        change_room(0x0296, position=(0.0, 0.0, 0.0), init_sub=0x25, music=MusicFlag.FORCE_KEEP_CURRENT)
                    else:
                        change_room(original_world, position=(0.0, 0.0, 0.0), init_sub=original_sub)

                    label('label_4', manager=fevent_manager)
                    #emit_command(0x00DF, [0x0000FFFF])
                    set_blocked_buttons(Screen.TOP, ButtonFlags.ALL)
                    set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL)
                    set_movement_multipliers(Screen.TOP, 0.0, 0.0)
                    set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
                    set_touches_blocked(True)
                    call('show_stats')
                    branch('label_2')

                    label('label_2', manager=fevent_manager)
                    set_blocked_buttons(Screen.TOP, ButtonFlags.NONE)
                    set_blocked_buttons(Screen.BOTTOM, ButtonFlags.NONE)
                    set_movement_multipliers(Screen.TOP, 1.0, 1.0)
                    set_movement_multipliers(Screen.BOTTOM, 1.0, 1.0)
                    set_touches_blocked(False)
                    branch('label_0')

                try:
                    sprite_index = script.header.sprite_groups.index(0x0001)
                except ValueError:
                    script.header.sprite_groups.append(0x0001)
                    sprite_index = len(script.header.sprite_groups) - 1
                script.header.actors.append((0x00000000, 0x00000000, (len(script.subroutines)-1)*0x10000 + sprite_index,
                                             0xFFFFFFFF, len(script.subroutines)-1, 0x00748143))
                update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

                fbar.update(3)

        #Adds rocks that prevent softlocks in overworld [Room ID, HOW_ROCKS_PLACED (0 = Horizontal, 1 = Vertical, 2 = Up, 3 = Square), START_X, START_Y, START_Z, ROCKS_TO_PLACE, ability logic]
        rock_add = [[0x077, 0, 640, 600, 964, 6, [4]], [0x002, 1, 1402, 66, 200, 2, [0]], [0x006, 1, 160, 0, 608, 2, [0]], [0x007, 1, 1378, 75, 496, 2, [0]], [0x0AF, 0, 1000, 50, 660, 3, [18, 19, 20, 21]], [0x011, 0, 672, 0, 600, 4, [0, 1 + settings[3][0]]],
                    [0x101, 1, 248, 0, 200, 3, [0, 1 + settings[3][0]]], [0x018, 1, 640, 280, 324, 3, [0]], [0x184, 0, 520, 0, 800, 3, [0]], [0x04F, 3, 1840, 30, 1150, 1, [0]], [0x01C, 0, 768, 132, 512, 3, [14]],

                    [0x102, 3, 1000, 64, 480, 3, [6]], [0x00B, 0, 1408, 80, 448, 5, [6]], [0x07F, 3, 1006, 0, 400, 1, [6, 8, 9, 10, 11]], [0x288, 0, 552, 40, 510, 2, [6]],
                    [0x03A, 0, 936, 10, 800, 2, [6]], [0x03B, 0, 1205, 33, 1380, 1, [6]], [0x04C, 0, 975, 30, 920, 2, [6, 10]], [0x104, 0, 735, 180, 355, 1, [6]],
                    [0x144, 0, 1000, 100, 620, 4, [6]], [0x14D, 0, 1000, 100, 650, 4, [6]], [0x151, 0, 778, 30, 506, 4, [6]],

                    [0x13A, 0, 1585, 0, 1310, 1, [6]], [0x013, 0, 505, 75, 2080, 1, [6]], [0x019, 0, 980, 0, 2092, 1, [6]], [0x019, 0, 3005, 65, 2173, 1, [6]],
                    [0x28A, 0, 640, 0, 1230, 1, [6]], [0x101, 0, 530, 0, 910, 1, [6]], [0x061, 0, 1827, 155, 494, 1, [6, 7, 8, 12, 13]], [0x103, 0, 1469, 180, 616, 1, [6, 8, 9]],
                    [0x004, 0, 1122, 0, 1535, 1, [6, 10]], [0x008, 0, 219, 165, 367, 1, [6, 8]], [0x036, 0, 1550, 0, 832, 1, [6]], [0x035, 0, 962, 10, 360, 1, [6, 8, 9]],
                    [0x06E, 0, 832, 660, 242, 1, [6, 8, 10]], [0x072, 0, 675, 600, 790, 1, [6, 10]],
                    [0x076, 0, 775, 200, 1215, 1, [6, 10]], [0x038, 0, 2040, 165, 520, 1, [6]], [0x189, 0, 802, 180, 623, 1, [6]], [0x189, 0, 1945, 40, 1380, 1, [6]],
                    [0x18B, 0, 875, 40, 1975, 1, [6]], [0x190, 0, 1228, 220, 435, 1, [6]], [0x18d, 0, 728, 40, 758, 1, [6]], [0x191, 0, 398, 40, 253, 1, [6]],
                    [0x193, 0, 638, 0, 455, 1, [6]], [0x18f, 0, 795, 120, 195, 1, [6]], [0x18f, 0, 1123, 360, 118, 1, [6]], [0x141, 0, 762, 0, 815, 1, [6, 7, 8, 12, 13]],

                    [0x0AA, 2, 400, 70, 0, 1, [6, 7, 12, 13]], [0x0D8, 2, 400, 0, 0, 1, [6]], [0x0AD, 2, 600, 0, 0, 1, [6]], [0x1E7, 2, 475, 1200, 0, 1, [6, 8]]]

        #Deletes the softlock preventing rocks in Britta's Meeting Room if Ball Hop Prevention is off
        if settings[1][1] == 0:
            del rock_add[4]

        ability_names = ["Hammers", "Mini Mario", "Mole Mario", "Spin Jump", "Side Drill", "Ball Hop", "Luiginary Works", "Luiginary Ball Ability", "Luiginary Stack Spring Jump",
                          "Luiginary Stack Ground Pound", "Luiginary Cone Jump", "Luiginary Cone Storm", "Luiginary Ball Hookshot", "Luiginary Ball Throw", "Pi'illo Castle Key", "Blimport Bridge", "Mushrise Park Gate",
                          "First Dozite", "Dozite 1", "Dozite 2", "Dozite 3", "Dozite 4", "Access to Wakeport", "Access to Mount Pajamaja", "Dream Egg 1", "Dream Egg 2", "Dream Egg 3", "Access to Neo Bowser Castle"]
        ability_ids = [0xE000, 0xE001, 0xE002, 0xE003, 0xE004, 0xE005, 0xE00A, 0xE00D, 0xE00F, 0xE00E, 0xE010, 0xE011, 0xE012, 0xE013,
                       0x9015, 0xC369, 0xCABF, 0x9040, 0xC343, 0xC344, 0xC345, 0xC346, 0xC960, 0xC3B9, 0xB0F7, 0xB0F7, 0xB0F7, 0xC47E]

        for r in rock_add:
            #print(r[0])
            script = fevent_manager.parsed_script(r[0], 0)
            script_index = r[0] * 2

            # Workaround for dynamic scope in Nuitka
            if '__compiled__' in globals():
                inspect.currentframe().f_locals['script_index'] = script_index

            t = "[DelayOff]Abilities required:"
            for a in r[6]:
                t += "\n[Color #2C65FF]" + ability_names[a] + "[Color #000000]"
            t += "[Pause " + str(50 + len(r[6])*10) + "]"
            @subroutine(subs=script.subroutines, hdr=script.header)
            def abilities_needed(sub: Subroutine):
                say(None, TextboxSoundsPreset.SILENT, t, offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
            sub_name = f'sub_0x{len(script.subroutines) - 1:x}'
            cast(SubroutineExt, abilities_needed).name = sub_name

            try:
                sprite_index = script.header.sprite_groups.index(0x5F)
            except ValueError:
                script.header.sprite_groups.append(0x5F)
                sprite_index = len(script.header.sprite_groups)-1

            @subroutine(subs=script.subroutines, hdr=script.header)
            def despawn_rocks(sub: Subroutine):
                for de in r[6]:
                    branch_if(Variables[ability_ids[de]], '==', 0.0, 'label_0')
                set_actor_attribute(Variables[0x7007], 0x00, 0.0)
                set_actor_attribute(Variables[0x7007], 0x01, 0.0)

                label('label_0', manager=fevent_manager)
            sub_name = f'sub_0x{len(script.subroutines) - 1:x}'
            cast(SubroutineExt, despawn_rocks).name = sub_name

            update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

            for ac in range(r[5]):
                if r[1] == 0:
                    script.header.actors.append((r[3] * 0x10000 + r[2] + ac*0x60, r[4], (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, 0x02900143))
                elif r[1] == 1:
                    script.header.actors.append((r[3] * 0x10000 + r[2], r[4] + ac*0x60, (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, 0x02900143))
                elif r[1] == 3:
                    script.header.actors.append((r[3] * 0x10000 + r[2] + ac*0x60, r[4], (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, 0x02900143))
                    script.header.actors.append((r[3] * 0x10000 + r[2] + 0x60*r[5] - ac*0x60, r[4] + 0x60*r[5], (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-1, 0x02900143))
                    script.header.actors.append((r[3] * 0x10000 + r[2], r[4] + 0x60*r[5] - ac*0x60, (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, 0x02900143))
                    script.header.actors.append((r[3] * 0x10000 + r[2] + 0x60*r[5], r[4] + ac*0x60, (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, 0x02900143))
                else:
                    script.header.actors.append((r[3] * 0x10000 + ac*0x600000 + r[2], r[4], (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, 0x02900143))
            fbar.update(2)

    with tqdm(total=len(repack_data), desc="Repacking randomized data...") as rbar:
        #Repacks all the randomized data
        blockcount = 0
        block_fix = []
        spotnum = 0
        for i in repack_data:
            #Sets the script to look at the room hammers will be placed
            script = fevent_manager.parsed_script(i[1], 0)

            #Doubles the script index for the message file
            script_index = i[1] * 2

            # Workaround for dynamic scope in Nuitka
            if '__compiled__' in globals():
                inspect.currentframe().f_locals['script_index'] = script_index

            #Sets up which block it should look at
            block_attr = 0xFFFF
            if (get_room(i[1]) == "Mushrise Park" or get_room(i[1]) == "Dozing Sands" or get_room(i[1]) == "Blimport" or get_room(i[1]) == "Wakeport" or get_room(i[1]) == "Driftwood Shore" or
                    get_room(i[1]) == "Mount Pajamaja" or get_room(i[1]) == "Pi'illo Castle" or get_room(i[1]) == "Neo Bowser Castle" or get_room(i[1]) == "Somnom Woods"):
                block_sprite = 0x0000
                block_sprite_hit = 0x0001
                try:
                    script.header.sprite_groups[script.header.sprite_groups.index(0x0003)] = 0x0000
                except ValueError:
                    pass
            else:
                block_sprite = 0x0011
                block_sprite_hit = 0x0012

            if 2 <= i[0] <= 4 or i[0] == 6:
                block_actor = 0x17001C3
            else:
                block_actor = 0x748143

            #Labels which item the subroutine gives
            addon = ""
            if i[6] < 0x6000:
                if 0x2000 <= i[6] <= 0x2006:
                    addon = item_msgs.messages[2 + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x2008 <= i[6] <= 0x200E:
                    addon = item_msgs.messages[0x1E + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x2010 <= i[6] <= 0x2016:
                    addon = item_msgs.messages[-6 + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x2018 <= i[6] <= 0x201E:
                    addon = item_msgs.messages[-2 + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x2020 <= i[6] <= 0x2022:
                    addon = item_msgs.messages[-46 + (i[6] >> 1 & 0x0FFF) * 4].text
                elif i[6] == 0x2024:
                    addon = item_msgs.messages[-30 + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x2026 <= i[6] <= 0x2030:
                    addon = item_msgs.messages[2 + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x2032 <= i[6] <= 0x2038:
                    addon = item_msgs.messages[0x1A + (i[6] >> 1 & 0x0FFF) * 4].text
                elif 0x203A <= i[6] <= 0x2044:
                    addon = item_msgs.messages[-14 + (i[6] >> 1 & 0x0FFF) * 4].text
            elif i[6] < 0xB000:
                addon = item_msgs.messages[0x152 + (i[6] >> 1 & 0x0FFF) * 4].text
            if i[6] == 0xB030 or i[6] == 0xB031:
                addon = "3D Red Shell"
                check_1 = 0xB030
                check_2 = 0xB031
                attack_id = 0xE01E
                attack_name = "3D Red Shell"
            if i[6] == 0xB032 or i[6] == 0xB033:
                addon = "Luiginary Ball Attack"
                check_1 = 0xB032
                check_2 = 0xB033
                attack_id = 0xE028
                attack_name = "Luiginary Ball Attack"
            if i[6] == 0xB037 or i[6] == 0xB038:
                addon = "Fire Flower"
                check_1 = 0xB037
                check_2 = 0xB038
                attack_id = 0xE021
                attack_name = "Fire Flower"
            if i[6] == 0xB039 or i[6] == 0xB03A:
                addon = "Luiginary Stack Attack"
                check_1 = 0xB039
                check_2 = 0xB03A
                attack_id = 0xE029
                attack_name = "Luiginary Stack Attack"
            if i[6] == 0xB03B or i[6] == 0xB03C:
                addon = "Bye-Bye Cannon"
                check_1 = 0xB03B
                check_2 = 0xB03C
                attack_id = 0xE024
                attack_name = "Bye-Bye Cannon"
            if i[6] == 0xB03D or i[6] == 0xB03E:
                addon = "Dropchopper"
                check_1 = 0xB03D
                check_2 = 0xB03E
                attack_id = 0xE020
                attack_name = "Dropchopper"
            if i[6] == 0xB03F or i[6] == 0xB040:
                addon = "Luiginary Hammer"
                check_1 = 0xB03F
                check_2 = 0xB040
                attack_id = 0xE02A
                attack_name = "Luiginary Hammer"
            if i[6] == 0xB041 or i[6] == 0xB042:
                addon = "Bomb Derby"
                check_1 = 0xB041
                check_2 = 0xB042
                attack_id = 0xE022
                attack_name = "Bomb Derby"
            if i[6] == 0xB043 or i[6] == 0xB044:
                addon = "Luiginary Flame"
                check_1 = 0xB043
                check_2 = 0xB044
                attack_id = 0xE02B
                attack_name = "Luiginary Flame"
            if i[6] == 0xB045 or i[6] == 0xB046:
                addon = "Slingsniper"
                check_1 = 0xB045
                check_2 = 0xB046
                attack_id = 0xE025
                attack_name = "Slingsniper"
            if i[6] == 0xB047 or i[6] == 0xB048:
                addon = "Luiginary Wall"
                check_1 = 0xB047
                check_2 = 0xB048
                attack_id = 0xE02C
                attack_name = "Luiginary Wall"
            if i[6] == 0xB049 or i[6] == 0xB04A:
                addon = "Jet-Board Bash"
                check_1 = 0xB049
                check_2 = 0xB04A
                attack_id = 0xE023
                attack_name = "Jet-Board Bash"
            if i[6] == 0xB04B or i[6] == 0xB04C:
                addon = "Luiginary Typhoon"
                check_1 = 0xB04B
                check_2 = 0xB04C
                attack_id = 0xE02D
                attack_name = "Luiginary Typhoon"
            if i[6] == 0xB059 or i[6] == 0xB05A:
                addon = "3D Green Shell"
                check_1 = 0xB059
                check_2 = 0xB05A
                attack_id = 0xE01F
                attack_name = "3D Green Shell"
            if i[6] == 0xB05B or i[6] == 0xB05C:
                addon = "Star Rocket"
                check_1 = 0xB05B
                check_2 = 0xB05C
                attack_id = 0xE026
                attack_name = "Star Rocket"
            coin_amount = 1
            if i[6] == 0x0002:
                coin_amount = 5
            if i[6] == 0x0004:
                coin_amount = 10
            if i[6] == 0x0006:
                coin_amount = 50
            if i[6] == 0x0008:
                coin_amount = 100
            #Sets up the subroutine to add a new ability
            if i[6] == 0xE001:
                addon = "Mini Mario"
            if i[6] == 0xE002:
                addon = "Mole Mario"
            if i[6] == 0xE004:
                addon = "Side Drill"
            if i[6] == 0xE005:
                addon = "Ball Hop"
            if i[6] == 0xE00A:
                addon = "Luiginary Works"
            if i[6] == 0xE00D:
                addon = "Luiginary Ball Ability"
            if i[6] == 0xE00E:
                addon = "Luiginary Stack Ground Pound"
            if i[6] == 0xE00F:
                addon = "Luiginary Stack Spring Jump"
            if i[6] == 0xE010:
                addon = "Luiginary Cone Jump"
            if i[6] == 0xE011:
                addon = "Luiginary Cone Tornado"
            if i[6] == 0xE012:
                addon = "Luiginary Ball Hookshot"
            if i[6] == 0xE013:
                addon = "Luiginary Ball Hammer"
            if i[6] == 0xE075:
                addon = "Pi'illo Castle Key"
            if i[6] == 0xC369:
                addon = "Blimport Bridge"
            if i[6] == 0xCABF:
                addon = "Mushrise Park Gate"
            if i[6] == 0xC343 or i[6] == 0xC344 or i[6] == 0xC345 or i[6] == 0xC346 or i[6] == 0xE0A0:
                addon = "Dozite"
            if i[6] == 0xC960:
                addon = "Wakeport"
            if i[6] == 0xC3B9:
                addon = "Mount Pajamaja"
            if i[6] == 0xC47E:
                addon = "Neo Bowser Castle"
            if i[6] == 0xE001 or i[6] == 0xE002:
                invi = (0xE001 - i[6]) + 0xE002
                invi_name = ["[Color #2C65FF]Mini Mario", "[Color #2C65FF]Mole Mario"]
            if i[6] == 0xB0F7:
                addon = "Dream Egg"
            if i[6] == 0xE0A0:
                item = "the first [Color #2C65FF]" + addon
            elif i[6] == 0xC960 or i[6] == 0xC3B9 or i[6] == 0xC47E:
                item = "access to [Color #2C65FF]" + addon
            elif (i[6] == 0xCABF or i[6] == 0xC369 or i[6] == 0xE004 or i[6] == 0xE005 or (0xE00D <= i[6] <= 0xE013) or i[6] == 0xE075):
                item = "the [Color #2C65FF]" + addon
            elif 0xB030 <= i[6] <= 0xB05C:
                item = "an Attack Piece\nfor the [Color #2C65FF]" + addon
            elif i[6] == 0xE001 or i[6] == 0xE002 or i[6] == 0xE00A:
                item = "[Color #2C65FF]" + addon
            elif addon[0:1] == 'A' or addon[0:1] == 'E' or addon[0:1] == 'I' or addon[0:1] == 'O' or addon[0:1] == 'U' or addon[0:2] == 'HP':
                item = "an [Color #2C65FF]" + addon
            else:
                item = "a [Color #2C65FF]" + addon
            if i[0] == 7:
                actor = 0
                while script.header.actors[actor][2] != 0xF70016:
                    actor += 1
            @subroutine(subs=script.subroutines, hdr=script.header)
            def get_item(sub: Subroutine):
                if i[0] != 5:
                    set_actor_attribute(len(script.header.actors), 0x30, 0.0)
                    try:
                        emit_command(0x008C, [len(script.header.actors), script.header.sprite_groups.index(block_sprite_hit), 0x0000, 0x01])
                    except ValueError:
                        emit_command(0x008C, [len(script.header.actors), len(script.header.sprite_groups), 0x0000, 0x01])
                    branch_if(Variables[i[5]], '==', 1.0, 'label_0')
                    Variables[i[5]] = 1.0
                else:
                    if (i[5] < 0xC000 or i[5] > 0xCFFF) and i[0] != 0 and i[0] != 1:
                        branch_if(Variables[i[5]], '==', 0.0, 'label_0')
                    if i[6] > 0xC000:
                        branch_if(Variables[i[6]], '==', 1.0, 'label_0')
                    elif i[6] > 0xB0E0 or i[6] < 0xB000:
                        if i[-1] > 10:
                            branch_if(Variables[i[-1]], '==', 1.0, 'label_0')
                        else:
                            branch_if(Variables[i[-2]], '==', 1.0, 'label_0')
                    else:
                        if i[-1] > 10:
                            branch_if(Variables[i[-1]], '==', 1.0, 'label_0')
                            Variables[i[-1]] = 1.0
                        else:
                            branch_if(Variables[i[-2]], '==', 1.0, 'label_0')
                            Variables[i[-2]] = 1.0
                if i[6] == 0xE001 or i[6] == 0xE002:
                    branch_if(Variables[i[7]], '==', 1.0, 'label_0')
                    branch_if(Variables[0xE000], '==', 0.0, 'label_1')
                    branch_if(Variables[invi], '==', 0.0, 'label_2')
                elif i[6] == 0xE004:
                    branch_if(Variables[0xE003], '==', 0.0, 'label_1')
                    branch_if(Variables[i[7]], '==', 1.0, 'label_0')
                elif 0xC343 <= i[6] <= 0xC346:
                    Variables[i[6]] = 1.0
                    branch_if(Variables[0xC343], '==', 0.0, 'label_1')
                    branch_if(Variables[0xC344], '==', 0.0, 'label_1')
                    branch_if(Variables[0xC345], '==', 0.0, 'label_1')
                    branch_if(Variables[0xC346], '==', 0.0, 'label_1')
                    Variables[0xE09F] = 1.0
                    say(None, TextboxSoundsPreset.SILENT,
                        "[DelayOff]You got the final [Color #2C65FF]" + addon + "[Color #000000]![Pause 60]",
                        offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    branch('label_0')
                if i[6] > 0xC000:
                    Variables[i[6]] = 1.0
                    if i[5] < 0xD000:
                        Variables[i[5]] = 1.0
                elif i[6] > 0xB0E0:
                    add_in_place(1.0, Variables[0xB0F7])
                    add_in_place(1.0, Variables[0xB02D])
                    Variables[i[len(i) - 1]] = 1.0
                elif i[6] > 0xB000:
                    Variables[i[6]] |= i[7]
                    branch_if(Variables[check_1], '!=', 0x1F, 'label_1')
                    branch_if(Variables[check_2], '!=', 0x1F, 'label_1')
                    Variables[attack_id] = 1.0
                    say(None, TextboxSoundsPreset.SILENT,
                        "[DelayOff]You've unlocked the [Color #2C65FF]" + attack_name + "[Color #000000]![Pause 60]",
                        offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    if (attack_name == "Luiginary Typhoon" or attack_name == "Luiginary Wall" or attack_name == "Luiginary Flame"
                        or attack_name == "Luiginary Hammer" or attack_name == "Luiginary Stack Attack" or attack_name == "Luiginary Ball Attack"):
                        Variables[0xE01B] = 1.0 #Unlocks the luiginary attack block
                    branch('label_0')
                elif i[6] >= 0x6000:
                    emit_command(0x0033, [int(math.floor((i[6] - 0x4000) / 2)) + 0x28, 0x01], Variables[0x300B])
                    if i[-1] > 10:
                        Variables[i[-1]] = 1.0
                    else:
                        Variables[i[-2]] = 1.0
                elif i[6] >= 0x2000:
                    emit_command(0x0033, [int(math.floor(i[6]/2)), 0x01], Variables[0x300B])
                    if i[-1] > 10:
                        Variables[i[-1]] = 1.0
                    else:
                        Variables[i[-2]] = 1.0
                else:
                    emit_command(0x0031, [coin_amount * i[7]], Variables[0x300B])
                    if i[-1] > 10:
                        Variables[i[-1]] = 1.0
                    else:
                        Variables[i[-2]] = 1.0
                if i[6] < 0x1000:
                    say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got [Color #2C65FF]" + str(coin_amount) + "[Color #000000]coin(s)![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    branch('label_0')
                elif (i[-1] < 0xC020 or i[-1] >= 0xC0A0) and i[-1] > 10:
                    say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got " + item + "[Color #000000]![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    branch('label_0')
                #elif i[-2] < 0xC020 or i[-2] >= 0xC0A0:
                #    say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got " + item + "[Color #000000]![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                #    branch('label_0')

                if i[6] == 0xE001 or i[6] == 0xE002 or i[6] == 0xE004 or (0xB000 < i[6] < 0xB0E0) or (0xC343 <= i[6] <= 0xC346):
                    label('label_1', manager=fevent_manager)
                    if 0xE001 <= i[6] <= 0xE004:
                        Variables[i[7]] = 1.0
                        if i[6] == 0xE004:
                            Variables[0xE003] = 1.0
                            say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got the [Color #2C65FF]Spin Jump[Color #000000]![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                        else:
                            Variables[0xE000] = 1.0
                            say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got [Color #2C65FF]Hammers[Color #000000]![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    else:
                        say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got " + item + "[Color #000000]![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    branch('label_0')

                if i[6] == 0xE001 or i[6] == 0xE002:
                    label('label_2', manager=fevent_manager)
                    Variables[i[7]] = 1.0
                    Variables[invi] = 1.0
                    say(None, TextboxSoundsPreset.SILENT, "[DelayOff]You got " + invi_name[invi - 0xE001] + "[Color #000000]![Pause 60]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    branch('label_0')

                label('label_0', manager=fevent_manager)

            #Gives the subroutine a unique name to prevent crashes
            sub_name = f'sub_0x{len(script.subroutines) - 1:x}'
            cast(SubroutineExt, get_item).name = sub_name

            if i[0] != 5:
                #Updates block graphics
                try:
                    script.header.sprite_groups.index(block_sprite_hit)
                except ValueError:
                    script.header.sprite_groups.append(block_sprite_hit)
                try:
                    sprite_index = script.header.sprite_groups.index(block_sprite)
                except ValueError:
                    script.header.sprite_groups.append(block_sprite)
                    sprite_index = len(script.header.sprite_groups) - 1

                #New initialization subroutine for blocks
                @subroutine(subs=script.subroutines, hdr=script.header)
                def set_block(sub: Subroutine):
                    if i[0] == 2:
                        set_actor_attribute(Variables[0x7007], 0x5F, 3.0)
                    elif i[0] == 3:
                        set_actor_attribute(Variables[0x7007], 0x5F, 5.0)
                    elif i[0] == 4:
                        set_actor_attribute(Variables[0x7007], 0x5F, 1.0)
                    #elif i[0] == 6:
                    #    set_actor_attribute(Variables[0x7007], 0x5C, 1.0)
                    branch_if(Variables[i[5]], '==', 0.0, 'label_0')
                    set_actor_attribute(Variables[0x7007], 0x30, 0.0)
                    #if i[0] == 6:
                    #    set_actor_attribute(Variables[0x7007], 0x5C, 0.0)
                    try:
                        emit_command(0x008C, [Variables[0x7007], script.header.sprite_groups.index(block_sprite_hit), 0x0000, 0x01])
                    except ValueError:
                        script.header.sprite_groups.append(block_sprite_hit)
                        emit_command(0x008C, [Variables[0x7007], script.header.sprite_groups.index(block_sprite_hit), 0x0000, 0x01])

                    label('label_0', manager=fevent_manager)

                # Gives the subroutine a unique name to prevent crashes
                sub_name = f'sub_0x{len(script.subroutines) - 1:x}'
                cast(SubroutineExt, set_block).name = sub_name

                #Updates the info
                script.header.actors.append((i[3]*0x10000 + i[2], i[4], (len(script.subroutines)-1)*0x10000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-2, block_actor))
                blockcount += 1
                block_fix.append(i[5])
            else:
                #Updates triggers if it's a bean spot
                if i[3] > 0:
                    script.header.triggers.append((((i[4]-0x10)*0x10000 + (i[2])-0x10), ((i[4]+0x10)*0x10000 + (i[2])+0x10), 0x00000000, 0x00000000,
                                                   ((i[3] + 0x15) * 0x10000) + (i[3] - 1), len(script.subroutines) - 1, 0x00078022))
                else:
                    script.header.triggers.append((((i[4]-0x10)*0x10000 + (i[2])-0x10), ((i[4]+0x10)*0x10000 + (i[2])+0x10), 0x00000000, 0x00000000,
                                                   ((i[3] + 0x15) * 0x10000), len(script.subroutines) - 1, 0x00078022))

            #Recompiles things
            update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
            rbar.update(1)

    with tqdm(total=4, desc="Saving...") as ubar:
        #Recompiles FEvent
        fevent_manager.save_all(data_dir=input_folder)
        ubar.update(1)

        #Recompiles FMes (takes a while)
        for language, text_chunks in Globals.text_chunks.items():
            default_chunk = LMSDocument(lambda: DTLMSAdapter(language))
            text_chunks_list = [
                text_chunks.get(i, default_chunk)
                for i in range(FMES_NUMBER_OF_CHUNKS)
            ]
            with (
                (message_dir / language / "FMes.dat").open("wb") as message_file,
                (message_dir / language / "FMes.bin").open("wb") as offset_table,
            ):
                write_msbt_archive(text_chunks_list, message_file, offset_table)
            ubar.update(1)
