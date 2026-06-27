from collections.abc import Mapping
from typing import Any

# Imports of base Archipelago modules must be absolute.
from worlds.AutoWorld import World
import os

# Imports of your world's files must be relative.
from . import items, locations, regions, rules, web_world, client
from . import options as mldt_options  # rename due to a name conflict with World.options

# APQuest will go through all the parts of the world api one step at a time,
# with many examples and comments across multiple files.
# If you'd rather read one continuous document, or just like reading multiple sources,
# we also have this document specifying the entire world api:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md

# The world class is the heart and soul of an apworld implementation.
# It holds all the data and functions required to build the world and submit it to the multiworld generator.
# You could have all your world code in just this one class, but for readability and better structure,
# it is common to split up world functionality into multiple files.
# This implementation in particular has the following additional files, each covering one topic:
# regions.py, locations.py, rules.py, items.py, options.py and web_world.py.
# It is recommended that you read these in that specific order, then come back to the world class.
class MLDTWorld(World):
    """
    Mario and Luigi Dream Team is a massive 3DS Mario and Luigi RPG
    It's infamous for many tutorials, but luckily this randomizer removes them
    """

    # The docstring should contain a description of the game, to be displayed on the WebHost.

    # You must override the "game" field to say the name of the game.
    game = "Mario and Luigi Dream Team"

    # The version that's required for it to run can be found in archipelago.json

    # The WebWorld is a definition class that governs how this world will be displayed on the website.
    web = web_world.MLDTWebWorld()

    # This is how we associate the options defined in our options.py with our world.
    # (Note: options.py has been imported as "apquest_options" at the top of this file to avoid a name conflict)
    options_dataclass = mldt_options.MLDTOptions
    options: mldt_options.MLDTOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).

    # Our world class must have a static location_name_to_id and item_name_to_id defined.
    # We define these in regions.py and items.py respectively, so we just set them here.
    item_name_to_id = items.ITEM_NAME_TO_ID
    location_name_to_id = locations.LOCATION_NAME_TO_ID

    # There is always one region that the generator starts from & assumes you can always go back to.
    # This defaults to "Menu", but you can change it by overriding origin_region_name.
    origin_region_name = "Blimport"

    # Our world class must have certain functions ("steps") that get called during generation.
    # The main ones are: create_regions, set_rules, create_items.
    # For better structure and readability, we put each of these in their own file.
    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)
        #self.location_name_to_id = locations.LOCATION_NAME_TO_ID
        #print(self.location_name_to_id)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    # Our world class must also have a create_item function that can create any one of our items by name at any time.
    # We also put this in a different file, the same one that create_items is in.
    def create_item(self, name: str) -> items.MLDTItem:
        return items.create_item_with_correct_classification(self, name)

    # For features such as item links and panic-method start inventory, AP may ask your world to create extra filler.
    # The way it does this is by calling get_filler_item_name.
    # For this purpose, your world *must* have at least one infinitely repeatable item (usually filler).
    # You must override this function and return this infinitely repeatable item's name.
    # In our case, we defined a function called get_random_filler_item_name for this purpose in our items.py.
    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    # There may be data that the game client will need to modify the behavior of the game.
    # This is what slot_data exists for. Upon every client connection, the slot's slot_data is sent to the client.
    # slot_data is just a dictionary using basic types, that will be converted to json when sent to the client.
    def fill_slot_data(self) -> Mapping[str, Any]:
        # If you need access to the player's chosen options on the client side, there is a helper for that.
        return self.options.as_dict(
            "second_hammer", "reduce_mini", "reduce_ball_skips"
        )

    def generate_output(self, output_directory: str) -> None:
        data = {
            "seed": self.multiworld.seed_name,  # to verify the server's multiworld
            "slot": self.multiworld.player_name[self.player],  # to connect to server
            "items": {location.name: location.item.name
                    if location.item.player == self.player else "Remote"
                    for location in self.multiworld.get_filled_locations(self.player)},
            # store start_inventory from player's .yaml
            # make sure to mark as not remote_start_inventory when connecting if stored in rom/mod
            "starter_items": [item.name for item in self.multiworld.precollected_items[self.player]],
        }

        region_names = ["Blimport", "Pi'illo Castle", "Pi'illo Castle Dream's Deep",
                        "Under Blimport Bridge", "Mushrise Park Main Area", "Mushrise Park Hammer Regions",
                        "Dozing Sands/Driftwood Shore Outskirts", "Dozing Sands Track Area", "Dozing Sands Dreamstone Area",
                        "Wakeport", "Wakeport Ultibed", "Mount Pajamaja Before Base", "Mount Pajamaja Base",
                        "Mount Pajamaja Middle", "Mount Pajamaja Peak", "Mount Pajamaja Summit Dreampoint",
                        "Driftwood Shore Dreampoint Area", "Driftwood Shore Dream Egg Dream", "Somnom Woods Before Tracks",
                        "Somnom Woods Track Area", "Somnom Woods After Tracks", "Neo Bowser Castle Before First Progressive Spin",
                        "Neo Bowser Castle After First Porgressive Spin", "Neo Bowser Castle Flame Pipe Area", "Neo Bowser Castle Bowser's Dream"]
        item_names = [["Progressive Hammers", "Progressive Spin", "Ball Hop", "Luiginary Works", "Luiginary Ball",
                       "Luiginary Stack Spring Jump", "Luiginary Stack Ground Pound", "Luiginary Cone Jump", "Luiginary Cone Storm",
                        "Luiginary Ball Hookshot", "Luiginary Ball Throw", "Pi'illo Castle Key", "Blimport Bridge",
                       "Mushrise Park Gate", "First Dozite", "Dozite 1", "Dozite 2", "Dozite 3", "Dozite 4", "Access to Wakeport",
                       "Access to Mount Pajamaja", "Dream Egg", "Access to Neo Bowser Castle"],
                      ["Mushroom", "Super Mushroom", "Ultra Mushroom", "Max Mushroom", "Nut", "Super Nut", "Ultra Nut", "Max Nut",
                       "Syrup Jar", "Supersyrup Jar", "Ultrasyrup Jar", "Max Syrup Jar", "Candy", "Super Candy", "Ultra Candy", "Max Candy",
                       "1-Up Mushroom", "1-Up Deluxe", "Refreshing Herb", "Heart Bean", "Bros Bean", "Power Bean", "Defense Bean",
                       "Speed Bean", "Stache Bean", "Taunt Ball", "Shock Bomb", "Boo Biscuit", "Secret Box",
                       "Heart Bean DX", "Bros Bean DX", "Power Bean DX", "Defense Bean DX", "Speed Bean DX", "Stache Bean DX"],
                      ["Coin", "5 Coin", "10 Coin", "50 Coin", "100 Coin", "10x1 Coin", "10x5 Coin", "10x10 Coin", "10x50 Coin", "10x100 Coin"],
                      ["Run-Down Boots", "Discount Boots", "So-So Boots", "Picnic Boots", "Bare Boots", "Iron-Ball Boots", "Steady Boots",
                        "Snare Boots", "Coin Boots", "Super Boots", "EXP Boots", "Knockout Boots", "Heart Boots", "Elite Boots", 
                        "Antiair Boots", "Action Boots", "Bros. Boots", "Singular Boots", "Glass Boots", "Coin Boots DX", "Iron-Ball Boots DX", 
                        "Celebrity Boots", "EXP Boots DX", "Antiair Boots DX", "Bare Boots DX", "Star Boots", "Dark Boots", "Crystal Boots", 
                        "Farmer Boots", "Master Boots", "Excellent Boots", "Expert Boots", "Hiking Boots", "Birthday Boots", "MINI Boots",
                        
                        "Run-Down Hammer", "Discount Hammer", "So-So Hammer", "Picnic Hammer", "Bare Hammer", "Iron-Ball Hammer",
                        "Steady Hammer", "Fighter Hammer", "Sap Hammer", "Super Hammer", "Soft Hammer", "Knockout Hammer", "Flame Hammer",
                        "Elite Hammer", "Blunt Hammer", "Action Hammer", "Spin Hammer", "Singular Hammer", "Glass Hammer", "Sap Hammer DX",
                        "Iron-Ball Hammer DX", "Celebrity Hammer", "Flame Hammer DX", "Blunt Hammer DX", "Bare Hammer DX",
                        "Star Hammer", "Dark Hammer", "Crystal Hammer", "Soft Hammer DX", "Master Hammer", "Excellent Hammer",
                        "Expert Hammer", "Golden Hammer", "Birthday Hammer", "MINI Hammer",
                  
                        "Thin Wear", "Picnic Wear", "Cozy Wear", "So-So Wear", "Payback Wear", "Singular Wear", "Rally Wear", "Charge Wear",
                        "Super Wear", "Fighter Wear", "Koopa Troopa Wear", "Celebrity Wear", "Counter Wear", "Safety Wear", "Fancy Wear",
                        "Hero Wear", "Bros. Wear", "Metal Wear", "Snare Wear", "Heart Wear", "Energy Wear", "Star Wear", "Ironclad Wear",
                        "King Wear", "Angel Wear", "Pro Wear", "Legendary Wear", "Expert Wear", "Golden Wear", "Birthday Wear",
                        
                        "Thick Gloves", "Shell Gloves", "Metal Gloves", "HP Gloves", "HP Gloves DX", "BP Gloves", "BP Gloves DX", "POW Gloves",
                        "POW Gloves DX", "Speed Gloves", "Stache Gloves", "Lucky Gloves", "Lucky Gloves DX", "Gift Gloves", "Gift Gloves DX",
                        "Charge Gloves", "Charge Gloves DX", "Strike Gloves", "Mushroom Gloves", "1-Up Gloves", "Master Gloves", "Rookie Gloves",
                        "Perfect POW Gloves", "Perfect Bro Gloves", "Coin Bro Gloves", "Coin Bro Gloves DX", "EXP Bro Gloves", "EXP Bro Gloves DX",
                        "Bottomless Gloves", "MINI Gloves", 
                        
                        "HP Scarf", "HP Scarf DX", "BP Scarf", "BP Scarf DX", "POW Scarf", "POW Scarf DX", "Speed Scarf", "Stache Scarf",
                        "Bros. Ring", "HP Bangle", "HP Bangle DX", "BP Bangle", "BP Bangle DX", "Angel Bangle", "HP Knockout Bangle",
                        "BP Knockout Bangle", "Healthy Ring", "Guard Shell", "Guard Shell DX", "Rally Belt", "Counter Belt", "POW Mush Jam",
                        "DEF Mush Jam", "Duplex Crown", "UNUSED", "Mushroom Amulet", "Birthday Ring", "Mini Ring (UNUSED)", "Silver Statue",
                        "Gold Statue"]]
        key_ids = [0xE002 - self.options.second_hammer, 0xE004, 0xE005, 0xE00A, 0xE00D, 0xE00F, 0xE00E, 0xE010, 0xE011, 0xE012, 0xE013,
                   0xE075, 0xC369, 0xCABF, 0xE0A0, 0xC343, 0xC344, 0xC345, 0xC346, 0xC960, 0xC3B9, 0xB0F7, 0xC47E]
        recomp_data = []
        name_data = []

        #Appends the settings
        first_byte = 0
        if self.options.reduce_mini:
            first_byte += 0x10
        if self.options.reduce_ball_skips:
            first_byte += 0x1
        recomp_data.append(first_byte)
        recomp_data.append(self.options.second_hammer * 4)
        recomp_data.append(0x00)
        recomp_data.append(0x00)
        recomp_data.append(0x00)
        recomp_data.append(0x00)
        recomp_data.append(0x00)
        recomp_data.append(0x00)

        #Appends the item info
        r = 0
        pr = 0
        l = 0
        for location in self.multiworld.get_locations(self.player):
            if location.item.name != "Victory":
                pr = r
                r = region_names.index(location.parent_region.name)
                recomp_data.append(r)
                if r != pr:
                    l = 0
                    pr = r
                recomp_data.append(l)
                l += 1
                if location.item.player == self.player:
                    try:
                        to_write = key_ids[item_names[0].index(location.item.name)]
                    except ValueError:
                        try:
                            to_write = (item_names[1].index(location.item.name) * 2) + 0x2000
                        except ValueError:
                            try:
                                to_write = (item_names[3].index(location.item.name) * 2) + 0x6000
                            except ValueError:
                                try:
                                    to_write = (item_names[2].index(location.item.name) * 2)
                                except ValueError:
                                    if location.item.name == "Attack Piece":
                                        to_write = 0xA000
                                    else:
                                        to_write = 0xFFFF
                    recomp_data.append(to_write // 0x100)
                    recomp_data.append(to_write % 0x100)
                else:
                    recomp_data.append(0x10 + (len(location.item.name) // 0x100))
                    recomp_data.append(len(location.item.name) % 0x100)
                    name_data.append([location.item.name, location.item.player])

        for name in name_data:
            recomp_data.append(name[1])
            for char in name[0]:
                raw_char = ord(char)
                recomp_data.append(raw_char)
        
        #Adds the player names to the file
        recomp_data.append(len(self.multiworld.player_name.items()))
        for pn, name in self.multiworld.player_name.items():
            recomp_data.append(len(name))
            #print(recomp_data[-1])
            for char in name:
                recomp_data.append(ord(char))
        
        #Adds the key item order to the file, adding 0xFF so it knows when to stop
        for sphere in self.multiworld.get_spheres():
            for location in sphere:
                try:
                    if location.item.player == self.player:
                        recomp_data.append(item_names[0].index(location.item.name))
                except ValueError:
                    pass
        recomp_data.append(0xFF)

        #Creates an order for the attacks
        attack_used = []
        first_attack = self.random.randint(0, 14)
        while first_attack >= 9:
            first_attack = self.random.randint(0, 14)
        recomp_data.append(first_attack * 0x10)
        attack_used.append(first_attack)
        for a in range(14):
            next_attack = self.random.randint(0, 14)
            while next_attack in attack_used:
                next_attack += 1
                if next_attack > 14:
                    next_attack = 0
            if a % 2 == 0:
                recomp_data[-1] += next_attack
            else:
                recomp_data.append(0)
                recomp_data[-1] += next_attack * 0x10
            attack_used.append(next_attack)

        # add needed option results to the dictionary
        #data.update(self.options.as_dict("final_boss_hp", "difficulty", "fix_xyz_glitch"))
        # Point to worlds/mygame/data/mod_template
        src = os.path.join(os.path.dirname(__file__), "data", "mod_template")
        # generate output path
        mod_name = self.multiworld.get_out_file_name_base(self.player)
        out_file = os.path.join(output_directory, mod_name + ".bin")
        # generate the file
        with open(out_file, "wb") as file:
            for i in recomp_data:
                file.write(int.to_bytes(i))