from pymsbmnl import LMSDocument, msbt_from_file
from mnllib.n3ds import fs_std_romfs_path
from mnllib import Subroutine, RawDataCommand
from mnllib.dt import FEventScriptManager, FMES_NUMBER_OF_CHUNKS, MESSAGE_DIR_PATH, DTLMSAdapter, read_msbt_archive, write_msbt_archive
from mnlscript import CodeCommandWithOffsets, emit_command, update_commands_with_offsets, Screen, label, \
    SubroutineExt
from mnlscript.dt import PLACEHOLDER_OFFSET, Variables, change_room, MusicFlag, set_action_icons_shown, \
    set_actor_attribute, Actors, tint_screen, set_blocked_buttons, ButtonFlags, set_movement_multipliers, \
    set_touches_blocked, branch_if, TextboxSoundsPreset, say, wait, Globals, call, branch, TextboxAlignment, \
    add_in_place
from typing import cast
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

def find_index_in_2d_list(arr, target_value):
    for row_index, row in enumerate(arr):
        for col_index, element in enumerate(row):
            if element == target_value:
                return (row_index, col_index)
    return None  # Return None if the element is not found

def pack(input_folder, repack_data, settings):
    print("Setting up FEvent...")
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
    item_msgs = msbt_from_file(lambda: DTLMSAdapter('US_English'), fs_std_romfs_path('Message/US_English/Item.msbt', data_dir=input_folder))

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
        Variables[0xE075] = 1.0 #Fixes bridge in Deep Pi'illo Castle
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
        Variables[0xE070] = 1.0 #Dromba bridge is up
        #Variables[0xCB07] = 1.0 #Final Dreamy Castle cutscene
        Variables[0xCB08] = 1.0 #Dreambert is revived
        Variables[0xCC2B] = 1.0 #Dreambert awakes
        Variables[0xCC2C] = 1.0 #Dreambert runs out of castle cutscene
        Variables[0xCC2D] = 1.0 #"There are many sights" cutscene
        Variables[0xCC2E] = 1.0 #Blimport bridge collapses
        wait(3)
        Variables[0xCC2F] = 1.0 #Mario falls on Luigi
        Variables[0xCC30] = 1.0 #See first Pi'illo
        Variables[0xCC31] = 1.0 #First Pi'illo saved, can access Pi'illo folk in collection
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
        Variables[0xE01B] = 1.0 #Unlock Dream World Attacks
        Variables[0xC045] = 1.0 #Bunny hops away in flower room
        Variables[0xC024] = 1.0 #Cornered bunny and got nightmare chunk
        Variables[0xE076] = 1.0 #Bridge under Nightmare Chunk room breaks
        Variables[0xC956] = 1.0 #Eldream's nightmare chunk is shattered
        Variables[0xC04D] = 1.0 #Saved Eldream, Dream's Deep portal is open
        Variables[0xC06D] = 1.0 #Skipped opening cutscene for Dream's Deep
        Variables[0xC048] = 1.0 #Prince Dreambert cutscene when entering Dream's Deep
        Variables[0xC068] = 1.0 #Luigi explains how the different entrance works
        Variables[0xC071] = 1.0 #Dreamy Luigi follows you in Dream's Deep
        Variables[0xC074] = 1.0 #"Where were you" cutscene when leaving Dream's Deep
        #Variables[0xCABF] = 1.0 #Opens gate at bottom of Mushrise Park
        Variables[0xC335] = 1.0 #Dozing Sands badge cutscene
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
        #Variables[0xE0A0] = 1.0 #Bridge is up
        Variables[0xC33D] = 1.0 #Britta appears
        Variables[0xC33E] = 1.0 #Another talk with Britta
        Variables[0xC340] = 1.0 #First drilldigger tutorial
        Variables[0xC36D] = 1.0 #Drilldigger tutorial with Britta
        Variables[0xC34B] = 1.0 #First Deco Pi'illo rock broken
        Variables[0xC07C] = 1.0 #Drill dreamwork tutorial
        Variables[0xC07E] = 1.0 #Ha! I'm over HERE now!
        Variables[0xC07D] = 1.0 #Centrifugal force
        Variables[0xC07F] = 1.0 #Break dream stone with hammer (duh)
        Variables[0xC389] = 1.0 #First main Deco Pi'illo nightmare chunk broken
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
        Variables[0xC96B] = 1.0 #Panel tutorial cutscene
        Variables[0xC969] = 1.0 #Panel tutorial complete
        Variables[0xC96C] = 1.0 #Bridge is down
        Variables[0xC96D] = 1.0 #Toad is no longer worried
        Variables[0xC96A] = 1.0 #Big Massif is awake
        Variables[0xC601] = 1.0 #Hooraws Bail
        Variables[0xCF80] = 1.0 #Timer tutorial
        Variables[0xC096] = 1.0 #Timer slow tutorial
        Variables[0xC097] = 1.0 #Timer fast tutorial
        Variables[0xC098] = 1.0 #Timer Dreambert leaves
        Variables[0xC0AD] = 1.0 #Fall slow to hit red coins
        Variables[0xC0AE] = 1.0 #Crunch to hit bombs
        wait(3)
        #Variables[0xC3B9] = 1.0 #Massifs pushed rock and opened Mount Pajamaja
        Variables[0xC3BB] = 1.0 #Massifs explain how a gate works
        Variables[0xCFC2] = 1.0 #Massifs are in right position for cutscene above
        Variables[0xC3C6] = 1.0 #Big Massif tells you to hurry up
        Variables[0xC3CB] = 1.0 #Mega Low Intro
        Variables[0xC3CC] = 1.0 #RISING BEEF!!!
        Variables[0xC3CD] = 1.0 #Massifs are high
        Variables[0xC3CE] = 1.0 #Massifs commit die
        Variables[0xC3CF] = 1.0 #A Massif hint: turn valve
        Variables[0xC3D0] = 1.0 #Mega Phil Intro
        Variables[0xCCBF] = 1.0 #Luiginary Cone Tutorial
        Variables[0xC41B] = 1.0 #Side Drill Tutorial
        Variables[0xC41C] = 1.0 #Side Drill Tutorial Part 2
        Variables[0xC4B8] = 1.0 #Drink fountain tutorial
        Variables[0xC3D4] = 1.0 #Massifs break ice tutorial
        Variables[0xC3D5] = 1.0 #Massifs break ice tutorial
        Variables[0xC3F2] = 1.0 #Wind blows things!?
        Variables[0xC422] = 1.0 #Mega Cush and Shawn intro
        Variables[0xC425] = 1.0 #The people at the top of the mountain look evil
        Variables[0xC640] = 1.0 #First entered Mount Pajamaja Summit dreampoint
        Variables[0xC641] = 1.0 #Trapped in Mount Pajamaja Summit
        Variables[0xC4AD] = 1.0 #Gold pipes appear in early game areas
        Variables[0xCC7F] = 1.0 #Peach is in Driftwood Shores Cutscene
        Variables[0xCC80] = 1.0 #Part of same cutscene as above?
        Variables[0xCC81] = 1.0 #Allows you to talk to the guys that let you into Driftwood Shores
        Variables[0xCC4E] = 1.0 #Broque is faking liking you
        Variables[0xCC4F] = 1.0 #Can access Driftwood Shores
        Variables[0xE0C1] = 1.0 #Removes invisible wall blocking Driftwood Shores
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
        Variables[0xCC69] = 1.0 #Another dreampoint is available
        Variables[0xCC6A] = 1.0 #Another dreampoint is nearby
        Variables[0xCC53] = 1.0 #Talk to Broque Madame after Elite Trio's defeat
        Variables[0xCC82] = 1.0 #Doctor Snoozemore Appears
        Variables[0xCC83] = 1.0 #Doctor Snoozemore Cutscene Watched
        Variables[0xC0B4] = 1.0 #Pi'illo Castle dream's deep opens
        Variables[0xC0A1] = 1.0 #Ultibed appears in pause menu
        Variables[0xC5CC] = 1.0 #You must find the Ultibed parts cutscene
        Variables[0xC438] = 1.0 #Ultibed cutscene in Mount Pajamaja is watched
        Variables[0xC4AE] = 1.0 #Fixes a glitch in the rock code
        Variables[0xC304] = 1.0 #Spawns more rocks in Mushrise Park
        Variables[0xC9F5] = 1.0 #Boss Brickle ponders who can help him
        Variables[0xC9B2] = 1.0 #Ultibed in Mushrise Park start
        Variables[0xC9B3] = 1.0 #Ultibed in Mushrise Park start
        Variables[0xC9F3] = 1.0 #Guy lets you into a rock area
        Variables[0xC9F4] = 1.0 #Tree blocking other rock area is removed
        #Variables[0xC9D9] = 1.0 #Driftwood Jelly Sheets have been stolen
        #Variables[0xC9DA] = 1.0 #Something something chase the fiends
        Variables[0xC9DD] = 1.0 #Listened to the old coot vent
        Variables[0xC9DE] = 1.0 #Second Crab Minigame complete
        Variables[0xC9E1] = 1.0 #Wiggler first cutscene watched
        Variables[0xC9E2] = 1.0 #Wiggler second cutscene watched
        wait(3)
        #Variables[0xC9E0] = 1.0 #Wiggler is defeated
        Variables[0xC9EA] = 1.0 #Bedsmith appears
        Variables[0xC59F] = 1.0 #Cog to enter Somnom Woods is available
        Variables[0xE0F9] = 1.0 #Stairs to switch in Somnom Woods are up
        Variables[0xC5A0] = 1.0 #Cog has been turned
        Variables[0xE0FA] = 1.0 #Switch in Somnom Woods has been turned
        Variables[0xC45E] = 1.0 #Elite Trio flee
        Variables[0xC43B] = 1.0 #Kamek randomized the rooms in the first area
        Variables[0xC475] = 1.0 #Switch is on the other side
        Variables[0xC474] = 1.0 #Cutscene before entering Kamek's first dream world
        Variables[0xC447] = 1.0 #Kamek randomizes the second area
        Variables[0xE00B] = 1.0 #Gives Luiginary stack
        Variables[0xE00C] = 1.0 #Gives Luiginary tornado (but none of its abilities)
        change_room(0x0298, position=(0.0, 0.0, 0.0), init_sub=-0x1, music=MusicFlag.FORCE_KEEP_CURRENT)
        emit_command(0x0056, [0x01, 0x028D0026])  # Execute the command that was replaced with a call to this subroutine.

    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

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
        Variables[0xE075] = int(settings[0][14])
        Variables[0xC369] = int(settings[0][15])
        Variables[0xCABF] = int(settings[0][16])
        Variables[0xE0A0] = int(settings[0][17])
        Variables[0xC343] = int(settings[0][18])
        Variables[0xC344] = int(settings[0][19])
        Variables[0xC345] = int(settings[0][20])
        Variables[0xC346] = int(settings[0][21])
        if settings[0][18] == 1.0 and settings[0][19] == 1.0 and settings[0][20] == 1.0 and settings[0][21] == 1.0:
            Variables[0xE09F] = 1.0
        Variables[0xC960] = int(settings[0][22])
        Variables[0xC3B9] = int(settings[0][23])
        Variables[0xB0F7] += int(settings[0][24])
        Variables[0xB0F7] += int(settings[0][25])
        Variables[0xB0F7] += int(settings[0][26])
        Variables[0xC47E] = int(settings[0][27])
        if settings[1][0] == 1:
            Variables[0xE0AA] = 1.0
            Variables[0xE0BC] = 1.0
            Variables[0xE105] = 1.0
        change_room(0x001c, position=(800.0, 0.0, 800.0), init_sub=-0x01, facing=8)

    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    #Sets up Pi'illo Castle grounds so you can go past the invisible wall and the NPCs are still there
    script = fevent_manager.parsed_script(0x001c, 0)
    script.subroutines[0x53].commands[1] = CodeCommandWithOffsets(0x0126, [0x00, 0x01])
    script.subroutines[0x54].commands[318] = CodeCommandWithOffsets(0x0002, [0x0, Variables[0xCC80], 1.0, 0x01, PLACEHOLDER_OFFSET], offset_arguments={4: 'end'})
    cast(SubroutineExt, script.subroutines[0x54]).labels = {
        'end': script.subroutines[0x54].serialized_len(fevent_manager, 0, with_footer=False) - 6,
    }
    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    script = fevent_manager.parsed_script(0x0001, 0)
    script.header.triggers[1] = (0, 0, 0, 0, 0, 0x0032, 0x78012)

    #Sets the script to look at the room you fight Torkscrew
    script = fevent_manager.parsed_script(0x0102, 0)

    #Names the label so it can be accessed later (Hex value got by subtracting comment on top from comment on label)
    cast(SubroutineExt, script.subroutines[0x49]).labels = {
        'label_151': 0x2D55,
    }

    #Allows you to access Torkscrew even if the cutscene breaks
    @subroutine(subs=script.subroutines, hdr=script.header)
    def access_torkscrew(sub: Subroutine):
        branch_if(Variables[0xE09F], "==", 0.0, 'label_0')
        branch_if(Variables[0xC367], "==", 1.0, 'label_0')
        change_room(0x02AB, position=(1000.0, 0.0, 2000.0), init_sub=-0x1)

        label('label_0', manager=fevent_manager)

    #Adds trigger so you can fight the boss
    script.header.triggers.append((0x02F50000, 0x2FFF2FFF, 0x00000000, 0x00000000, 0xFFFF0000, 0x0000005C, 0x00078022))

    #Skips the post-boss cutscene
    script.subroutines[0x49].commands[6] = CodeCommandWithOffsets(0x0003, [0x01, PLACEHOLDER_OFFSET], offset_arguments={1: 'label_151'})
    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    #Stops Massifs pushing rock cutscene from appearing
    script = fevent_manager.parsed_script(0x0067, 0)
    if settings[1][1] == 1:
        script.header.actors.append((0x0025027B, 0x000002E4, 0xFFFF000E, 0xFFFFFFFF, 0xFFFFFFFF, 0x01980143))
        script.header.actors.append((0x000002BB, 0x000002E4, 0xFFFF000E, 0xFFFFFFFF, 0xFFFFFFFF, 0x01980143))
    cast(SubroutineExt, script.subroutines[script.header.init_subroutine]).name = 'init'
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

    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    #Fixes the Mammoshka boss fight
    script = fevent_manager.parsed_script(0x007D, 0)
    cast(SubroutineExt, script.subroutines[0x2d]).labels = {
        'label_3': 0x15E,
    }
    script.subroutines[0x2d].commands[11] = CodeCommandWithOffsets(0x0002, [0x0, Variables[0xC438], 1.0, 0x01, PLACEHOLDER_OFFSET], offset_arguments={4: 'label_3'})
    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    #Blocks Dream World in the Summit until you have the needed abilities
    script = fevent_manager.parsed_script(0x007F, 0)
    script_index = 0x007F * 2

    # Workaround for dynamic scope in Nuitka
    if '__compiled__' in globals():
        inspect.currentframe().f_locals['script_index'] = script_index

    cast(SubroutineExt, script.subroutines[0x52]).name = 'sub_0x52'
    @subroutine(subs=script.subroutines, hdr=script.header)
    def summit_access(sub: Subroutine):
        branch_if(Variables[0xE00A], '==', 0.0, 'label_0')
        branch_if(Variables[0xE00E], '==', 0.0, 'label_0')
        branch_if(Variables[0xE00F], '==', 0.0, 'label_0')
        branch_if(Variables[0xE010], '==', 0.0, 'label_0')
        branch_if(Variables[0xE011], '==', 0.0, 'label_0')
        branch('sub_0x52')

        label('label_0', manager=fevent_manager)
        say(None, TextboxSoundsPreset.SILENT, "You don't have the\nrequired abilities.[Pause 45]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)

    script.header.triggers[0] = (0x018203EE, 0x02140450, 0x00000000, 0x00000000, 0x01000040, len(script.subroutines)-1, 0x00078002)
    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))


    #Adds a trigger right before Bowser in Neo Bowser Castle that warps you out if you haven't defeated all bosses
    script = fevent_manager.parsed_script(0x015E, 0)
    script_index = 0x015E * 2

    # Workaround for dynamic scope in Nuitka
    if '__compiled__' in globals():
        inspect.currentframe().f_locals['script_index'] = script_index

    @subroutine(subs=script.subroutines, hdr=script.header)
    def defeat_all_bosses(sub: Subroutine):
        branch_if(Variables[0xCC28], '==', 0.0, 'label_0')
        branch_if(Variables[0xCB07], '==', 0.0, 'label_0')
        branch_if(Variables[0xC92F], '==', 0.0, 'label_0')
        branch_if(Variables[0xC04C], '==', 0.0, 'label_0')
        branch_if(Variables[0xC367], '==', 0.0, 'label_0')
        branch_if(Variables[0xC057], '==', 0.0, 'label_0')
        branch_if(Variables[0xC60E], '==', 0.0, 'label_0')
        branch_if(Variables[0xC423], '==', 0.0, 'label_0')
        branch_if(Variables[0xC649], '==', 0.0, 'label_0')
        branch_if(Variables[0xCB45], '==', 0.0, 'label_0')
        branch_if(Variables[0xC637], '==', 0.0, 'label_0')
        branch_if(Variables[0xC5AE], '==', 0.0, 'label_0')
        branch_if(Variables[0xC0BF], '==', 0.0, 'label_0')
        branch_if(Variables[0xC0B8], '==', 0.0, 'label_0')
        branch_if(Variables[0xC0CA], '==', 0.0, 'label_0')
        branch_if(Variables[0xC45C], '==', 0.0, 'label_0')
        branch('label_1')

        label('label_0', manager=fevent_manager)
        set_blocked_buttons(Screen.TOP, ButtonFlags.ALL, res=Variables[0x3000])
        set_blocked_buttons(Screen.BOTTOM, ButtonFlags.ALL, res=Variables[0x3001])
        set_movement_multipliers(Screen.TOP, 0.0, 0.0)
        set_movement_multipliers(Screen.BOTTOM, 0.0, 0.0)
        set_touches_blocked(True)
        say(None, TextboxSoundsPreset.SILENT, "You must defeat all bosses\nbefore you can face Bowser.[Pause 45]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
        change_room(0x01C8, position=(1400.0, 0.0, 1360.0), init_sub=-0x1)

        label('label_1', manager=fevent_manager)

    script.header.triggers.append((0x00000000, 0x01F302A8, 0x00000000, 0x00000000, 0xFFFF0046, len(script.subroutines)-1, 0x00078022))
    update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    #Edits every room with attack piece blocks so they're all deactivated by default
    attack_dat = [0x001, 0x004, 0x005, 0x010, 0x011, 0x012, 0x013, 0x014, 0x017, 0x019, 0x01F, 0x020, 0x021, 0x022, 0x027, 0x028, 0x02A,
                  0x034, 0x035, 0x036, 0x038, 0x039, 0x03A, 0x03B, 0x03D, 0x040, 0x04B, 0x04C, 0x04D, 0x04F, 0x062, 0x069, 0x06A, 0x06C,
                  0x06D, 0x06F, 0x070, 0x072, 0x075, 0x076, 0x079, 0x07C, 0x0BB, 0x0BD, 0x0BE, 0x0C4, 0x0C5, 0x0C6, 0x0D2, 0x0D6, 0x0E4,
                  0x0F5, 0x0F6, 0x0FA, 0x10C, 0x124, 0x125, 0x126, 0x127, 0x128, 0x129, 0x12A, 0x13D, 0x144, 0x145, 0x146, 0x147, 0x148,
                  0x14B, 0x14C, 0x14E, 0x14F, 0x161, 0x164, 0x165, 0x167, 0x168, 0x16C, 0x177, 0x17A, 0x17D, 0x1E7, 0x1F8, 0x295,]
    j = []
    for i in range(len(attack_dat)):
        script = fevent_manager.parsed_script(attack_dat[i], 0)
        cast(SubroutineExt, script.subroutines[script.header.init_subroutine]).name = 'init'
        script.header.init_subroutine = None
        @subroutine(subs=script.subroutines, hdr=script.header, init=True)
        def attack_flag(sub: Subroutine):
            for a in range(len(script.header.actors)):
                if (script.header.actors[a][5] // 0x1000) % 0x1000 == 0x748 and script.header.actors[a][5] % 0x100 == 0x43:
                    j.append([script.header.actors[a][0] % 0x10000, script.header.actors[a][0] // 0x10000, script.header.actors[a][1] % 0x10000, attack_dat[i]])
                    set_actor_attribute(a, 0x00, 0.0)
                    set_actor_attribute(a, 0x01, 0.0)
            call('init')
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    print("Repacking randomized data...")
    #Repacks all the randomized data
    blockcount = 0
    block_info = []
    prevroom = 0
    for i in repack_data:
        #Updates the previous script if there are blocks to be updated
        if i[1] != prevroom and blockcount > 0:
            cast(SubroutineExt, script.subroutines[script.header.init_subroutine]).name = 'og_init'
            script.header.init_subroutine = None
            @subroutine(subs=script.subroutines, hdr=script.header, init=True)
            def fix_blocks(sub: Subroutine):
                for a in range(blockcount):
                    if block_info[a][1] == 0.0:
                        branch_if(Variables[block_info[a][0]], '==', block_info[a][1], 'label_' + str(a))
                    else:
                        Variables[0xCD90] = Variables[block_info[a][0]] >> int(math.log2(block_info[a][1]))
                        branch_if(Variables[0xCD90], '!=', 1.0, 'label_' + str(a))
                    set_actor_attribute(len(script.header.actors) - blockcount + a, 0x30, 0.0)
                    try:
                        emit_command(0x008C, [len(script.header.actors) - blockcount + a, script.header.sprite_groups.index(0x0001), 0x0000, 0x01])
                    except ValueError:
                        emit_command(0x008C, [len(script.header.actors) - blockcount + a, len(script.header.sprite_groups), 0x0000, 0x01])
                        script.header.sprite_groups.append(0x0001)

                    label('label_' + str(a), manager=fevent_manager)
                    if a == blockcount - 1:
                        call('og_init')
            update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))
            blockcount = 0
            block_info = []

        #Sets the script to look at the room hammers will be placed
        script = fevent_manager.parsed_script(i[1], 0)

        #Doubles the script index for the message file
        script_index = i[1] * 2

        # Workaround for dynamic scope in Nuitka
        if '__compiled__' in globals():
            inspect.currentframe().f_locals['script_index'] = script_index

        #Sets up the subroutine to give an item
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
            addon = "Mushrise Park"
            check_1 = 0xB030
            check_2 = 0xB031
            attack_id = 0xE01E
            attack_name = "Red Shell"
        if i[6] == 0xB032 or i[6] == 0xB033:
            addon = "Dreamy Mushrise Park"
            check_1 = 0xB032
            check_2 = 0xB033
            attack_id = 0xE028
            attack_name = "Luiginary Ball"
        if i[6] == 0xB037 or i[6] == 0xB038:
            addon = "Dozing Sands"
            check_1 = 0xB037
            check_2 = 0xB038
            attack_id = 0xE021
            attack_name = "Fire Flower"
        if i[6] == 0xB039 or i[6] == 0xB03A:
            addon = "Dreamy Dozing Sands"
            check_1 = 0xB039
            check_2 = 0xB03A
            attack_id = 0xE029
            attack_name = "Luiginary Stack"
        if i[6] == 0xB03B or i[6] == 0xB03C:
            addon = "Wakeport"
            check_1 = 0xB03B
            check_2 = 0xB03C
            attack_id = 0xE024
            attack_name = "Bye-Bye Cannon"
        if i[6] == 0xB03D or i[6] == 0xB03E:
            addon = "Mount Pajamaja"
            check_1 = 0xB03D
            check_2 = 0xB03E
            attack_id = 0xE020
            attack_name = "Dropchopper"
        if i[6] == 0xB03F or i[6] == 0xB040:
            addon = "Dreamy Mount Pajamaja"
            check_1 = 0xB03F
            check_2 = 0xB040
            attack_id = 0xE02A
            attack_name = "Luiginary Hammer"
        if i[6] == 0xB041 or i[6] == 0xB042:
            addon = "Driftwood Shores"
            check_1 = 0xB041
            check_2 = 0xB042
            attack_id = 0xE022
            attack_name = "Bomb Derby"
        if i[6] == 0xB043 or i[6] == 0xB044:
            addon = "Dreamy Driftwood Shores"
            check_1 = 0xB043
            check_2 = 0xB044
            attack_id = 0xE02B
            attack_name = "Luiginary Flame"
        if i[6] == 0xB045 or i[6] == 0xB046:
            addon = "Lofty Mount Pajamaja"
            check_1 = 0xB045
            check_2 = 0xB046
            attack_id = 0xE025
            attack_name = "Slingsniper"
        if i[6] == 0xB047 or i[6] == 0xB048:
            addon = "Dreamy Wakeport"
            check_1 = 0xB047
            check_2 = 0xB048
            attack_id = 0xE02C
            attack_name = "Luiginary Wall"
        if i[6] == 0xB049 or i[6] == 0xB04A:
            addon = "Somnom Woods"
            check_1 = 0xB049
            check_2 = 0xB04A
            attack_id = 0xE023
            attack_name = "Jet-Board Bash"
        if i[6] == 0xB04B or i[6] == 0xB04C:
            addon = "Dreamy Somnom Woods"
            check_1 = 0xB04B
            check_2 = 0xB04C
            attack_id = 0xE02D
            attack_name = "Luiginary Typhoon"
        if i[6] == 0xB059 or i[6] == 0xB05A:
            addon = "Mushrise Park Caves"
            check_1 = 0xB059
            check_2 = 0xB05A
            attack_id = 0xE01F
            attack_name = "Green Shell"
        if i[6] == 0xB05B or i[6] == 0xB05C:
            addon = "Neo Bowser Castle"
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
            addon = "Luiginary Ball"
        if i[6] == 0xE00E:
            addon = "Luiginary Stack Spring Jump"
        if i[6] == 0xE00F:
            addon = "Luiginary Stack Ground Pound"
        if i[6] == 0xE010:
            addon = "Luiginary Cone Jump"
        if i[6] == 0xE011:
            addon = "Luiginary Cone Tornado"
        if i[6] == 0xE012:
            addon = "Luiginary Ball Hookshot"
        if i[6] == 0xE013:
            addon = "Luiginary Ball Hammer"
        if i[6] == 0xE075:
            addon = "Deep Pi'illo Castle"
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
        elif i[6] == 0xC960 or i[6] == 0xE075 or i[6] == 0xC3B9 or i[6] == 0xC47E:
            item = "access to [Color #2C65FF]" + addon
        elif (i[6] == 0xCABF or i[6] == 0xC369 or i[6] == 0xE004 or i[6] == 0xE005 or (0xE00D <= i[6] <= 0xE013)):
            item = "the [Color #2C65FF]" + addon
        elif 0xB030 <= i[6] <= 0xB05C:
            item = "an Attack Piece\nfor [Color #2C65FF]" + addon
        elif i[6] == 0xE001 or i[6] == 0xE002 or i[6] == 0xE00A:
            item = "[Color #2C65FF]" + addon
        elif addon[0:1] == 'A' or addon[0:1] == 'E' or addon[0:1] == 'I' or addon[0:1] == 'O' or addon[0:1] == 'U' or addon[0:2] == 'HP':
            item = "an [Color #2C65FF]" + addon
        else:
            item = "a [Color #2C65FF]" + addon
        actor = 0x00
        if i[0] == 7:
            actor = 0
            while script.header.actors[actor][2] != 0xF70016:
                actor += 1
        @subroutine(subs=script.subroutines, hdr=script.header)
        def get_item(sub: Subroutine):
            if i[0] == 0 or i[0] == 1:
                set_actor_attribute(len(script.header.actors), 0x30, 0.0)
                try:
                    emit_command(0x008C, [len(script.header.actors), script.header.sprite_groups.index(0x0001), 0x0000, 0x01])
                except ValueError:
                    emit_command(0x008C, [len(script.header.actors), len(script.header.sprite_groups), 0x0000, 0x01])
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
                    "You got the final [Color #2C65FF]" + addon + "[Color #000000]![Pause 90]",
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
                    "You've unlocked the [Color #2C65FF]" + attack_name + "[Color #000000]![Pause 90]",
                    offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
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
                say(None, TextboxSoundsPreset.SILENT, "You got [Color #2C65FF]" + str(coin_amount) + "[Color #000000]coin(s)![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                branch('label_0')
            elif (i[-1] < 0xC020 or i[-1] >= 0xC0A0) and i[-1] > 10:
                say(None, TextboxSoundsPreset.SILENT, "You got " + item + "[Color #000000]![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                branch('label_0')
            elif i[-2] < 0xC020 or i[-2] >= 0xC0A0:
                say(None, TextboxSoundsPreset.SILENT, "You got " + item + "[Color #000000]![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                branch('label_0')

            if i[6] == 0xE001 or i[6] == 0xE002 or i[6] == 0xE004 or (0xB000 < i[6] < 0xB0E0) or (0xC343 <= i[6] <= 0xC346):
                label('label_1', manager=fevent_manager)
                if 0xE001 <= i[6] <= 0xE004:
                    Variables[i[7]] = 1.0
                    if i[6] == 0xE004:
                        Variables[0xE003] = 1.0
                        say(None, TextboxSoundsPreset.SILENT, "You got the [Color #2C65FF]Spin Jump[Color #000000]![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                    else:
                        Variables[0xE000] = 1.0
                        say(None, TextboxSoundsPreset.SILENT, "You got [Color #2C65FF]Hammers[Color #000000]![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                else:
                    say(None, TextboxSoundsPreset.SILENT, "You got " + item + "[Color #000000]![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                branch('label_0')

            if i[6] == 0xE001 or i[6] == 0xE002:
                label('label_2', manager=fevent_manager)
                Variables[i[7]] = 1.0
                Variables[invi] = 1.0
                say(None, TextboxSoundsPreset.SILENT, "You got [Color #2C65FF]" + invi_name[invi - 0xE001] + "[Color #000000]![Pause 90]", offset=(0.0, 0.0, 0.0), anim=None, post_anim=None, alignment=TextboxAlignment.TOP_CENTER)
                branch('label_0')

            label('label_0', manager=fevent_manager)

        #Gives the subroutine a unique name to prevent crashes
        sub_name = f'sub_0x{len(script.subroutines) - 1:x}'
        cast(SubroutineExt, get_item).name = sub_name

        if i[0] == 0 or i[0] == 1:
            #Updates actors if it's an overworld block
            try:
                sprite_index = script.header.sprite_groups.index(0x0000)
            except ValueError:
                try:
                    script.header.sprite_groups.index(0x0001)
                except ValueError:
                    script.header.sprite_groups.append(0x0001)
                script.header.sprite_groups.append(0x0000)
                sprite_index = len(script.header.sprite_groups) - 1
            script.header.actors.append((i[3]*0x10000 + i[2], i[4], 0xFFFF0000 + sprite_index, 0xFFFFFFFF, len(script.subroutines)-1, 0x748143))
            blockcount += 1
            if i[6] > 0xB0F0:
                block_info.append([i[6], 0.0])
            else:
                block_info.append([i[6], i[7]])
        elif i[0] == 5:
            #Updates triggers if it's a bean spot
            if i[3] > 0:
                script.header.triggers.append((((i[4]-0x10)*0x10000 + (i[2])-0x10), ((i[4]+0x10)*0x10000 + (i[2])+0x10), 0x00000000, 0x00000000,
                                               ((i[3] + 0x15) * 0x10000) + (i[3] - 1), len(script.subroutines) - 1, 0x00078022))
            else:
                script.header.triggers.append((((i[4]-0x10)*0x10000 + (i[2])-0x10), ((i[4]+0x10)*0x10000 + (i[2])+0x10), 0x00000000, 0x00000000,
                                               ((i[3] + 0x15) * 0x10000), len(script.subroutines) - 1, 0x00078022))
        prevroom = i[1]

        #Recompiles things
        update_commands_with_offsets(fevent_manager, script.subroutines, len(script.header.to_bytes(fevent_manager)))

    print("Saving...")
    #Recompiles FEvent
    fevent_manager.save_all(data_dir=input_folder)

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
