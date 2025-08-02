# Workaround for dynamic scope in Nuitka
if '__compiled__' in globals():
    _dynamicscope_test_variable = False

# Imports the necessary modules
import sys
import os
import shutil
import functools
from mldtr import randomize_music, randomize_main

#Import modules for later use
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from mnllib.dt import determine_version_from_code_bin
import random

def get_folder(window):
    # Grabs a folder
    window.romfs = fd.askdirectory(
        title='Open Dumped Game Directory',
        initialdir='/', )

    # Either allows the options to work, or says they can't
    if os.path.isfile(window.romfs + "/exefs/code.bin"):
        window.option_2.config(state="normal")
        window.songdir_button.config(state="normal")
        window.generate.config(state="normal")
    else:
        showinfo(
            "Whoops!",
            "Couldn't find your exefs"
        )
        window.option_2.config(state="disabled")
        window.option_3.config(state="disabled")
        window.songdir_button.config(state="disabled")


def get_song_folder(window):
    # Grabs a folder
    songdir = fd.askdirectory(
        title='Open Custom Song Folder',
        initialdir='/', )

    # Adds all .rsd files into the array
    for root, _, files in os.walk(songdir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path[len(file_path) - 4:len(file_path)] == ".rsd":
                if file[0:5] == "AREA_":
                    window.all_songs[0].append(file_path)
                elif file[0:7] == "BATTLE_":
                    window.all_songs[1].append(file_path)
                elif file[0:9] == "CUTSCENE_":
                    window.all_songs[2].append(file_path)
                elif file[0:5] == "MENU_":
                    window.all_songs[3].append(file_path)
                elif file[0:9] == "MINIGAME_":
                    window.all_songs[4].append(file_path)
                elif not (file[0:13] == "STRBGM_JINGLE"):
                    window.all_songs[5].append(file_path)

    # Either allows the options to work, or says they can't
    if (len(window.all_songs[0]) + len(window.all_songs[1]) + len(window.all_songs[2])
            + len(window.all_songs[3]) + len(window.all_songs[4]) + len(window.all_songs[5]) >= 52):
        window.option_3.config(state="normal")
    else:
        showinfo(
            "Whoops!",
            "Couldn't find enough .rsd files.\nYou need at least 52 to use this."
        )
        window.option_3.config(state="disabled")


def can_check(window):
    # Checks if the checkbox is available or not
    if (window.option.get() == 0 or (
            window.option.get() == 2 and (len(window.all_songs[0]) < 25 or len(window.all_songs[1]) < 6
                                          or len(window.all_songs[2]) < 15 or len(window.all_songs[3]) < 5 or len(
                window.all_songs[4]) < 1))):
        window.category_check.config(state="disabled")
        window.categorize.set(False)
    else:
        window.category_check.config(state="normal")


def help():
    # Idk why I had to make this but ok, sure
    showinfo("Categorize Help",
             "You can't categorize with no randomization.\n" +
             "Also, if your custom song directory can't be categorized, you need:\n" +
             "- At least 25 songs beginning in \"AREA_\"\n" +
             "- At least 6 songs beginning in \"BATTLE_\"\n" +
             "- At least 15 songs beginning in \"CUTSCENE_\"\n" +
             "- At least 5 songs beginning in \"MENU_\"\n" +
             "- At least one song beginning in \"MINIGAME_\"")


def randomize(window):
    #Moves the data to a copy of the folder
    region = determine_version_from_code_bin(window.romfs + "/exefs/code.bin")
    if region[0] == "E":
        title_id = "00040000000D5A00"
    elif region[0] == "P":
        title_id = "00040000000D9000"
    elif region[0] == "J":
        title_id = "0004000000060600"
    elif region[0] == "K":
        title_id = "00040000000FCD00"
    else:
        title_id = ""
    parent_folder = os.path.dirname(window.romfs) + "/"

    #Generates the seed
    seed = random.randint(0, 0xFFFFFFFF)

    #Sets seed to an input if the user input a seed
    if window.seed.get() != "":
        try:
            if int(window.seed.get(), 16) < 0x100000000:
                seed = int(window.seed.get(), 16)
        except ValueError:
            seed = int.from_bytes(window.seed.get().encode('utf-8'))

    if os.path.exists(parent_folder + title_id):
        while os.path.exists(parent_folder + title_id + "-seed" + hex(seed)):
            seed = random.randint(0, 0xFFFFFFFF)
        seed_folder = parent_folder + title_id + "-seed" + hex(seed)
    else:
        seed_folder = parent_folder + title_id
    shutil.copytree(window.romfs, seed_folder)
    old_romfs = window.romfs
    window.romfs = seed_folder

    # Sets enemy stats to what you selected
    window.enemy_stats[0] = 1
    if window.attack_mode.get() == "0.5x - Easy":
        window.enemy_stats[0] = 0.5
    elif window.attack_mode.get() == "1x - Normal":
        window.enemy_stats[0] = 1
    elif window.attack_mode.get() == "2x - Hard":
        window.enemy_stats[0] = 2
    elif window.attack_mode.get() == "3x - Very Hard":
        window.enemy_stats[0] = 3
    elif window.attack_mode.get() == "5x - Good Luck":
        window.enemy_stats[0] = 5
    elif window.attack_mode.get() == "Maxed Out - The Perfect Run":
        window.enemy_stats[0] = -1

    window.enemy_stats[1] = 2
    if window.exp_mode.get() == "0.5x - Grinder's Delight":
        window.enemy_stats[1] = 0.5
    elif window.exp_mode.get() == "1x - Normal":
        window.enemy_stats[1] = 1
    elif window.exp_mode.get() == "2x - Quick Level":
        window.enemy_stats[1] = 2
    elif window.exp_mode.get() == "3x - Quicker Level":
        window.enemy_stats[1] = 3
    elif window.exp_mode.get() == "5x - Rapid Level":
        window.enemy_stats[1] = 5
    elif window.exp_mode.get() == "10x - Enemies are Overrated":
        window.enemy_stats[1] = 10

    #Appends settings to an array
    window.random_settings = [[window.key1.get(), window.key2.get(), window.key3.get(), window.key4.get(), window.key5.get(), window.key6.get(), window.key7.get(),
                               window.key8.get(), window.key9.get(), window.key10.get(), window.key11.get(), window.key12.get(), window.key13.get(), window.key14.get(),
                               window.key15.get(), window.key16.get(), window.key17.get(), window.key18.get(), window.key19.get(), window.key20.get(), window.key21.get(),
                               window.key22.get(), window.key23.get(), window.key24.get(), window.key25.get(), window.key26.get(), window.key27.get(), window.key28.get()],
                              [window.mini_nerf.get(), window.ball_nerf.get(), 0],
                              [window.boss1.get(), window.boss2.get(), window.boss3.get(), window.boss4.get(), window.boss5.get(), window.boss6.get(), window.boss7.get(),
                               window.boss8.get(), window.boss9.get(), window.boss10.get(), window.boss11.get(), window.boss12.get(), window.boss13.get(), window.boss14.get(),
                               window.boss15.get(), window.boss16.get()]]

    # Begins randomization
    randomize_main.randomize_data(window.romfs, window.enemy_stats, window.random_settings, seed)
    if window.option.get() == 2:
        print("Randomizing custom music...")
        randomize_music.import_random(5, window.romfs, window.all_songs, window.categorize.get())
    if window.option.get() == 1:
        print("Randomizing music...")
        randomize_music.shuffle(window.romfs, window.categorize.get())

    #When it's complete, sets romfs back to the base folder and gives a success message
    window.romfs = old_romfs
    print("Done!")
    showinfo("Yay!", "Success!")


# Shows credits
def credit():
    # Credits for the license and my peers who helped me
    showinfo("Categorize Help",
             "This program is made under the GNU General Public License v3.0.\n" +
             "UI design and general coding: Dimitri Bee\n" +
             "FMap data and some cutscene flags: Pixiuchu\n" +
             "Mnlscript and some pointers: DimiDimit\n\n")

def main():
    # Create the window
    window = tk.Tk()
    window.title("Pi'illomizer")
    window.resizable(False, False)
    window.geometry("450x450")

    # Initialize some variables
    window.romfs = tk.StringVar()
    window.option = tk.IntVar()
    nubValues = ["No Randomization", 0,
                 "Base Game Songs Only", 1,
                 "Songs from Directory", 2]
    window.all_songs = [[], [], [], [], [], []]
    window.categorize = tk.BooleanVar()
    window.enemy_stats = [1, 2]
    window.attack_mode = tk.StringVar()
    window.attack_mode.set("1x - Normal")
    window.attack_options = ["0.5x - Easy", "1x - Normal", "2x - Hard", "3x - Very Hard", "5x - Good Luck",
                             "Maxed Out - The Perfect Run"]
    window.exp_mode = tk.StringVar()
    window.exp_mode.set("2x - Quick Level")
    window.exp_options = ["0.5x - Grinder's Delight", "1x - Normal", "2x - Quick Level", "3x - Quicker Level","5x - Rapid Level",
                          "10x - Enemies are Overrated"]
    window.key1 = tk.DoubleVar()
    window.key2 = tk.DoubleVar()
    window.key3 = tk.DoubleVar()
    window.key4 = tk.DoubleVar()
    window.key5 = tk.DoubleVar()
    window.key6 = tk.DoubleVar()
    window.key7 = tk.DoubleVar()
    window.key8 = tk.DoubleVar()
    window.key9 = tk.DoubleVar()
    window.key10 = tk.DoubleVar()
    window.key11 = tk.DoubleVar()
    window.key12 = tk.DoubleVar()
    window.key13 = tk.DoubleVar()
    window.key14 = tk.DoubleVar()
    window.key15 = tk.DoubleVar()
    window.key16 = tk.DoubleVar()
    window.key17 = tk.DoubleVar()
    window.key18 = tk.DoubleVar()
    window.key19 = tk.DoubleVar()
    window.key20 = tk.DoubleVar()
    window.key21 = tk.DoubleVar()
    window.key22 = tk.DoubleVar()
    window.key23 = tk.DoubleVar()
    window.key24 = tk.DoubleVar()
    window.key25 = tk.DoubleVar()
    window.key26 = tk.DoubleVar()
    window.key27 = tk.DoubleVar()
    window.key28 = tk.DoubleVar()
    window.mini_nerf = tk.IntVar()
    window.ball_nerf = tk.IntVar()

    window.boss1 = tk.IntVar()
    window.boss2 = tk.IntVar()
    window.boss3 = tk.IntVar()
    window.boss4 = tk.IntVar()
    window.boss5 = tk.IntVar()
    window.boss6 = tk.IntVar()
    window.boss7 = tk.IntVar()
    window.boss8 = tk.IntVar()
    window.boss9 = tk.IntVar()
    window.boss10 = tk.IntVar()
    window.boss11 = tk.IntVar()
    window.boss12 = tk.IntVar()
    window.boss13 = tk.IntVar()
    window.boss14 = tk.IntVar()
    window.boss15 = tk.IntVar()
    window.boss16 = tk.IntVar()

    window.seed = tk.StringVar()

    #Creates tabs
    window.menu = ttk.Notebook(window)
    tabMain = ttk.Frame(window.menu)
    tabEnemy = ttk.Frame(window.menu)
    tabMusic = ttk.Frame(window.menu)

    #Names tabs
    window.menu.add(tabMain, text = "Main")
    window.menu.add(tabEnemy, text = "Enemy")
    window.menu.add(tabMusic, text = "Music")
    window.menu.pack(expand = 1, fill = "both", pady=40)

    # Press button to open RomFS
    window.romfs_button = ttk.Button(
        window,
        text='Open Dump',
        command = functools.partial(get_folder, window)
    )
    window.romfs_button.place(x=10, y=10)

    # Generates the file
    window.generate = ttk.Button(
        window,
        text = 'Generate',
        command = functools.partial(randomize, window),
        state = "disabled"
    )
    window.generate.place(x=185, y=410)

    #Shows credits if clicked on
    window.show_credits = ttk.Button(
        window,
        text = 'Credits',
        command = credit
    )
    window.show_credits.place(x=360, y=10)

    #Lets you decide options for enemy attack
    window.key_label = ttk.Label(tabEnemy, text = "Multiplier for enemy attack:")
    window.key_label.place(x=30, y=175)
    window.enemy_attack = ttk.OptionMenu(
        tabEnemy,
        window.attack_mode,
        window.attack_options[1],
        *window.attack_options
    )
    window.enemy_attack.place(x=25, y=200)

    #Lets you decide options for experience gained in battle
    window.key_label = ttk.Label(tabEnemy, text = "Multiplier for experience:")
    window.key_label.place(x=255, y=175)
    window.enemy_exp = ttk.OptionMenu(
        tabEnemy,
        window.exp_mode,
        window.exp_options[2],
        *window.exp_options
    )
    window.enemy_exp.place(x=250, y=200)

    # Press button to open songs
    window.songdir_button = ttk.Button(
        tabMusic,
        text='Open Custom Song Folder',
        command = functools.partial(get_song_folder, window),
        state = "disabled"
    )
    window.songdir_button.place(x=240, y=130)

    #Press dot for randomization option
    window.option_1 = ttk.Radiobutton(
        tabMusic,
        text = nubValues[0],
        variable = window.option,
        value = nubValues[1],
        command = functools.partial(can_check, window)
    )
    window.option_1.place(x=50, y=30)

    window.option_2 = ttk.Radiobutton(
        tabMusic,
        text = nubValues[2],
        variable = window.option,
        value = nubValues[3],
        command = functools.partial(can_check, window)
    )
    window.option_2.place(x=50, y=80)

    window.option_3 = ttk.Radiobutton(
        tabMusic,
        text = nubValues[4],
        variable = window.option,
        value = nubValues[5],
        command = functools.partial(can_check, window),
        state = "disabled"
    )
    window.option_3.place(x=50, y=130)

    #Checkmark for whether the randomized songs should be categorized or not
    window.category_check = ttk.Checkbutton(
        tabMusic,
        text = "Categorize",
        variable = window.categorize,
        onvalue = True,
        offvalue = False,
        state = "disabled"
    )
    window.category_check.place(x=180, y=195)

    #Buttons for the different ability options
    window.key_label = ttk.Label(tabMain, text = "Key Items you want to EXCLUDE:")
    window.key_label.place(x=129, y=20)
    window.hammer_check = ttk.Checkbutton(
        tabMain,
        text = "Hammers",
        variable = window.key1,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.hammer_check.place(x=12, y=50)

    window.mini_check = ttk.Checkbutton(
        tabMain,
        text = "Mini Mario",
        variable = window.key2,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.mini_check.place(x=129, y=50)

    window.mole_check = ttk.Checkbutton(
        tabMain,
        text = "Mole Mario",
        variable = window.key3,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.mole_check.place(x=246, y=50)

    window.spin_check = ttk.Checkbutton(
        tabMain,
        text = "Spin Jump",
        variable = window.key4,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.spin_check.place(x=359, y=50)

    window.drill_check = ttk.Checkbutton(
        tabMain,
        text = "Side Drill",
        variable = window.key5,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.drill_check.place(x=12, y=75)

    window.ball_hop_check = ttk.Checkbutton(
        tabMain,
        text = "Ball Hop",
        variable = window.key6,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.ball_hop_check.place(x=129, y=75)

    window.works_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Works",
        variable = window.key7,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.works_check.place(x=246, y=75)

    window.ball_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Ball",
        variable = window.key8,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.ball_check.place(x=359, y=75)

    window.stack_jump_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Stack Jump",
        variable = window.key9,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.stack_jump_check.place(x=12, y=100)

    window.stack_pound_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Stack Pound",
        variable = window.key10,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.stack_pound_check.place(x=129, y=100)

    window.cone_jump_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Cone Jump",
        variable = window.key11,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.cone_jump_check.place(x=246, y=100)

    window.cone_storm_check = ttk.Checkbutton(
        tabMain,
        text = "Cone Storm",
        variable = window.key12,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.cone_storm_check.place(x=359, y=100)

    window.ball_hookshot_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Ball Hook",
        variable = window.key13,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.ball_hookshot_check.place(x=12, y=125)

    window.ball_throw_check = ttk.Checkbutton(
        tabMain,
        text = "Luigi Ball Throw",
        variable = window.key14,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.ball_throw_check.place(x=129, y=125)

    window.deep_castle_check = ttk.Checkbutton(
        tabMain,
        text = "Deep Castle",
        variable = window.key15,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.deep_castle_check.place(x=246, y=125)

    window.blimp_check = ttk.Checkbutton(
        tabMain,
        text = "Bridge",
        variable = window.key16,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.blimp_check.place(x=359, y=125)

    window.gate_check = ttk.Checkbutton(
        tabMain,
        text = "Mushrise Gate",
        variable = window.key17,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.gate_check.place(x=12, y=150)

    window.dozite0_check = ttk.Checkbutton(
        tabMain,
        text = "Dozite 0",
        variable = window.key18,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.dozite0_check.place(x=129, y=150)

    window.dozite1_check = ttk.Checkbutton(
        tabMain,
        text = "Dozite 1",
        variable = window.key19,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.dozite1_check.place(x=246, y=150)

    window.dozite2_check = ttk.Checkbutton(
        tabMain,
        text = "Dozite 2",
        variable = window.key20,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.dozite2_check.place(x=359, y=150)

    window.dozite3 = ttk.Checkbutton(
        tabMain,
        text = "Dozite 3",
        variable = window.key21,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.dozite3.place(x=12, y=175)

    window.dozite4 = ttk.Checkbutton(
        tabMain,
        text = "Dozite 4",
        variable = window.key22,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.dozite4.place(x=129, y=175)

    window.wakeport_check = ttk.Checkbutton(
        tabMain,
        text = "Wakeport",
        variable = window.key23,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.wakeport_check.place(x=246, y=175)

    window.pajamaja_check = ttk.Checkbutton(
        tabMain,
        text = "Mt Pajamaja",
        variable = window.key24,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.pajamaja_check.place(x=359, y=175)

    window.egg1_check = ttk.Checkbutton(
        tabMain,
        text = "Dream Egg 1",
        variable = window.key25,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.egg1_check.place(x=12, y=200)

    window.egg2_check = ttk.Checkbutton(
        tabMain,
        text = "Dream Egg 2",
        variable = window.key26,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.egg2_check.place(x=129, y=200)

    window.egg3_check = ttk.Checkbutton(
        tabMain,
        text = "Dream Egg 3",
        variable = window.key27,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.egg3_check.place(x=246, y=200)

    window.neo_castle_check = ttk.Checkbutton(
        tabMain,
        text = "Neo Castle",
        variable = window.key28,
        onvalue = 1.0,
        offvalue = 0.0,
    )
    window.neo_castle_check.place(x=359, y=200)

    #Settings to reduce Mini Mario requirements
    window.mini_nerf_check = ttk.Checkbutton(
        tabMain,
        text = "Reduce Mini Mario Requirements",
        variable = window.mini_nerf,
        onvalue = 1,
        offvalue = 0
    )
    window.mini_nerf_check.place(x=16, y=250)

    #Settings to make the Ball Hop skip less
    window.ball_nerf_check = ttk.Checkbutton(
        tabMain,
        text = "Nerf Ball Hop",
        variable = window.ball_nerf,
        onvalue = 1,
        offvalue = 0
    )
    window.ball_nerf_check.place(x=240, y=250)

    #Settings for the bosses
    window.key_label = ttk.Label(tabEnemy, text = "Bosses you want to EXCLUDE:")
    window.key_label.place(x=150, y=20)
    window.boss1_check = ttk.Checkbutton(
        tabEnemy,
        text = "Smoldergeist",
        variable = window.boss1,
        onvalue = 1,
        offvalue = 0
    )
    window.boss1_check.place(x=12, y=50)

    window.boss2_check = ttk.Checkbutton(
        tabEnemy,
        text = "Dreamy Mario",
        variable = window.boss2,
        onvalue = 1,
        offvalue = 0
    )
    window.boss2_check.place(x=120, y=50)

    window.boss3_check = ttk.Checkbutton(
        tabEnemy,
        text = "Grobot",
        variable = window.boss3,
        onvalue = 1,
        offvalue = 0
    )
    window.boss3_check.place(x=225, y=50)

    window.boss4_check = ttk.Checkbutton(
        tabEnemy,
        text = "Bowser & Antasma",
        variable = window.boss4,
        onvalue = 1,
        offvalue = 0
    )
    window.boss4_check.place(x=320, y=50)

    window.boss5_check = ttk.Checkbutton(
        tabEnemy,
        text = "Torkscrew",
        variable = window.boss5,
        onvalue = 1,
        offvalue = 0
    )
    window.boss5_check.place(x=12, y=75)

    window.boss6_check = ttk.Checkbutton(
        tabEnemy,
        text = "Drilldozer",
        variable = window.boss6,
        onvalue = 1,
        offvalue = 0
    )
    window.boss6_check.place(x=120, y=75)

    window.boss7_check = ttk.Checkbutton(
        tabEnemy,
        text = "Big Massif",
        variable = window.boss7,
        onvalue = 1,
        offvalue = 0
    )
    window.boss7_check.place(x=225, y=75)

    window.boss8_check = ttk.Checkbutton(
        tabEnemy,
        text = "Mammoshka",
        variable = window.boss8,
        onvalue = 1,
        offvalue = 0
    )
    window.boss8_check.place(x=320, y=75)

    window.boss9_check = ttk.Checkbutton(
        tabEnemy,
        text = "Mount Pajamaja",
        variable = window.boss9,
        onvalue = 1,
        offvalue = 0
    )
    window.boss9_check.place(x=12, y=100)

    window.boss10_check = ttk.Checkbutton(
        tabEnemy,
        text = "Elite Trio",
        variable = window.boss10,
        onvalue = 1,
        offvalue = 0
    )
    window.boss10_check.place(x=120, y=100)

    window.boss11_check = ttk.Checkbutton(
        tabEnemy,
        text = "Wiggler & Popple",
        variable = window.boss11,
        onvalue = 1,
        offvalue = 0
    )
    window.boss11_check.place(x=200, y=100)

    window.boss12_check = ttk.Checkbutton(
        tabEnemy,
        text = "Earthwake",
        variable = window.boss12,
        onvalue = 1,
        offvalue = 0
    )
    window.boss12_check.place(x=320, y=100)

    window.boss13_check = ttk.Checkbutton(
        tabEnemy,
        text = "Pi'illodium",
        variable = window.boss13,
        onvalue = 1,
        offvalue = 0
    )
    window.boss13_check.place(x=12, y=125)

    window.boss14_check = ttk.Checkbutton(
        tabEnemy,
        text = "Zeekeeper",
        variable = window.boss14,
        onvalue = 1,
        offvalue = 0
    )
    window.boss14_check.place(x=120, y=125)

    window.boss15_check = ttk.Checkbutton(
        tabEnemy,
        text = "Giant Bowser",
        variable = window.boss15,
        onvalue = 1,
        offvalue = 0
    )
    window.boss15_check.place(x=225, y=125)

    window.boss16_check = ttk.Checkbutton(
        tabEnemy,
        text = "Antasma",
        variable = window.boss16,
        onvalue = 1,
        offvalue = 0
    )
    window.boss16_check.place(x=320, y=125)

    #Explains how the custom music categorization works
    window.category_info = ttk.Button(
        tabMusic,
        text = '?',
        command = help
    )
    window.category_info.place(x=185, y=220)

    #Lets you input a custom seed
    window.seed_label = ttk.Label(window, text = "Custom Seed:")
    window.seed_label.place(x=184, y=370)
    window.custom_seed = ttk.Entry(
        window,
        textvariable = window.seed
    )
    window.custom_seed.place(x=160, y=390)

    #Run the application loop
    window.mainloop()