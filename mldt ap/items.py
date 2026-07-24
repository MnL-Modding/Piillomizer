from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import MLDTWorld

#NOTE: Eventually I'll add the random hammer option. I'll need to do world.random.randint() if I want to do it properly

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID = {
    "Progressive Hammers": 1,
    "Progressive Spin": 2,
    "Ball Hop": 3,
    "Luiginary Works": 4,
    "Luiginary Ball": 5,
    "Luiginary Stack Spring Jump": 6,
    "Luiginary Stack Ground Pound": 7,
    "Luiginary Cone Jump": 8,
    "Luiginary Cone Storm": 9,
    "Luiginary Ball Hookshot": 10,
    "Luiginary Ball Throw": 11,
    "Pi'illo Castle Key": 12,
    "Blimport Bridge": 13,
    "Mushrise Park Gate": 14,
    "First Dozite": 15,
    "Dozite 1": 16,
    "Dozite 2": 17,
    "Dozite 3": 18,
    "Dozite 4": 19,
    "Access to Wakeport": 20,
    "Access to Mount Pajamaja": 21,
    "Dream Egg": 22,
    "Access to Neo Bowser Castle": 23,
    "Coin": 24,
    "5 Coin": 25,
    "10 Coin": 26,
    "50 Coin": 27,
    "100 Coin": 28,
    "10x1 Coin": 29,
    "10x5 Coin": 30,
    "10x10 Coin": 31,
    "10x50 Coin": 32,
    "10x100 Coin": 33,
    "Mushroom": 34,
    "Super Mushroom": 35,
    "Ultra Mushroom": 36,
    "Max Mushroom": 37,
    "Nut": 38,
    "Super Nut": 39,
    "Ultra Nut": 40,
    "Max Nut": 41,
    "Syrup Jar": 42,
    "Supersyrup Jar": 43,
    "Ultrasyrup Jar": 44,
    "Max Syrup Jar": 45,
    "Candy": 46,
    "Super Candy": 47,
    "Ultra Candy": 48,
    "Max Candy": 49,
    "1-Up Mushroom": 50,
    "1-Up Deluxe": 51,
    "Refreshing Herb": 52,
    "Heart Bean": 53,
    "Bros Bean": 54,
    "Power Bean": 55,
    "Defense Bean": 56,
    "Speed Bean": 57,
    "Stache Bean": 58,
    "Taunt Ball": 59,
    "Shock Bomb": 60,
    "Boo Biscuit": 61,
    "Secret Box": 62,
    "Heart Bean DX": 63,
    "Bros Bean DX": 64,
    "Power Bean DX": 65,
    "Defense Bean DX": 66,
    "Speed Bean DX": 67,
    "Stache Bean DX": 68,
    "Run-Down Boots": 69,
    "Discount Boots": 70,
    "So-So Boots": 71,
    "Picnic Boots": 72,
    "Bare Boots": 73,
    "Iron-Ball Boots": 74,
    "Steady Boots": 75,
    "Snare Boots": 76,
    "Coin Boots": 77,
    "Super Boots": 78,
    "EXP Boots": 79,
    "Knockout Boots": 80,
    "Heart Boots": 81,
    "Elite Boots": 82,
    "Antiair Boots": 83,
    "Action Boots": 84,
    "Bros. Boots": 85,
    "Singular Boots": 86,
    "Glass Boots": 87,
    "Coin Boots DX": 88,
    "Iron-Ball Boots DX": 89,
    "Celebrity Boots": 90,
    "EXP Boots DX": 91,
    "Antiair Boots DX": 92,
    "Bare Boots DX": 93,
    "Star Boots": 94,
    "Dark Boots": 95,
    "Crystal Boots": 96,
    "Farmer Boots": 97,
    "Master Boots": 98,
    "Excellent Boots": 99,
    "Expert Boots": 100,
    "Hiking Boots": 101,
    "Birthday Boots": 102,
    "MINI Boots": 103,
    "Run-Down Hammer": 104,
    "Discount Hammer": 105,
    "So-So Hammer": 106,
    "Picnic Hammer": 107,
    "Bare Hammer": 108,
    "Iron-Ball Hammer": 109,
    "Steady Hammer": 110,
    "Fighter Hammer": 111,
    "Sap Hammer": 112,
    "Super Hammer": 113,
    "Soft Hammer": 114,
    "Knockout Hammer": 115,
    "Flame Hammer": 116,
    "Elite Hammer": 117,
    "Blunt Hammer": 118,
    "Action Hammer": 119,
    "Spin Hammer": 120,
    "Singular Hammer": 121,
    "Glass Hammer": 122,
    "Sap Hammer DX": 123,
    "Iron-Ball Hammer DX": 124,
    "Celebrity Hammer": 125,
    "Flame Hammer DX": 126,
    "Blunt Hammer DX": 127,
    "Bare Hammer DX": 128,
    "Star Hammer": 129,
    "Dark Hammer": 130,
    "Crystal Hammer": 131,
    "Soft Hammer DX": 132,
    "Master Hammer": 133,
    "Excellent Hammer": 134,
    "Expert Hammer": 135,
    "Golden Hammer": 136,
    "Birthday Hammer": 137,
    "MINI Hammer": 138,
    "Thin Wear": 139,
    "Picnic Wear": 140,
    "Cozy Wear": 141,
    "So-So Wear": 142,
    "Payback Wear": 143,
    "Singular Wear": 144,
    "Rally Wear": 145,
    "Charge Wear": 146,
    "Super Wear": 147,
    "Fighter Wear": 148,
    "Koopa Troopa Wear": 149,
    "Celebrity Wear": 150,
    "Counter Wear": 151,
    "Safety Wear": 152,
    "Fancy Wear": 153,
    "Hero Wear": 154,
    "Bros. Wear": 155,
    "Metal Wear": 156,
    "Snare Wear": 157,
    "Heart Wear": 158,
    "Energy Wear": 159,
    "Star Wear": 160,
    "Ironclad Wear": 161,
    "King Wear": 162,
    "Angel Wear": 163,
    "Pro Wear": 164,
    "Legendary Wear": 165,
    "Expert Wear": 166,
    "Golden Wear": 167,
    "Birthday Wear": 168,
    "Thick Gloves": 169,
    "Shell Gloves": 170,
    "Metal Gloves": 171,
    "HP Gloves": 172,
    "HP Gloves DX": 173,
    "BP Gloves": 174,
    "BP Gloves DX": 175,
    "POW Gloves": 176,
    "POW Gloves DX": 177,
    "Speed Gloves": 178,
    "Stache Gloves": 179,
    "Lucky Gloves": 180,
    "Lucky Gloves DX": 181,
    "Gift Gloves": 182,
    "Gift Gloves DX": 183,
    "Charge Gloves": 184,
    "Charge Gloves DX": 185,
    "Strike Gloves": 186,
    "Mushroom Gloves": 187,
    "1-Up Gloves": 188,
    "Master Gloves": 189,
    "Rookie Gloves": 190,
    "Perfect POW Gloves": 191,
    "Perfect Bro Gloves": 192,
    "Coin Bro Gloves": 193,
    "Coin Bro Gloves DX": 194,
    "EXP Bro Gloves": 195,
    "EXP Bro Gloves DX": 196,
    "Bottomless Gloves": 197,
    "MINI Gloves": 198,
    "HP Scarf": 199,
    "HP Scarf DX": 200,
    "BP Scarf": 201,
    "BP Scarf DX": 202,
    "POW Scarf": 203,
    "POW Scarf DX": 204,
    "Speed Scarf": 205,
    "Stache Scarf": 206,
    "Bros. Ring": 207,
    "HP Bangle": 208,
    "HP Bangle DX": 209,
    "BP Bangle": 210,
    "BP Bangle DX": 211,
    "Angel Bangle": 212,
    "HP Knockout Bangle": 213,
    "BP Knockout Bangle": 214,
    "Healthy Ring": 215,
    "Guard Shell": 216,
    "Guard Shell DX": 217,
    "Rally Belt": 218,
    "Counter Belt": 219,
    "POW Mush Jam": 220,
    "DEF Mush Jam": 221,
    "Duplex Crown": 222,
    "UNUSED": 223,
    "Mushroom Amulet": 224,
    "Birthday Ring": 225,
    "Mini Ring (UNUSED)": 226,
    "Silver Statue": 227,
    "Gold Statue": 228,
    "Attack Piece": 255
}

# Items should have a defined default classification.
# In our case, we will make a dictionary from item name to classification.
DEFAULT_ITEM_CLASSIFICATIONS = {
    "Progressive Hammers": ItemClassification.progression,
    "Progressive Spin": ItemClassification.progression,
    #"Sword": ItemClassification.progression | ItemClassification.useful,  # Items can have multiple classifications.
    "Ball Hop": ItemClassification.progression,
    "Luiginary Works": ItemClassification.progression,
    "Luiginary Ball": ItemClassification.progression,
    "Luiginary Stack Spring Jump": ItemClassification.progression,
    "Luiginary Stack Ground Pound": ItemClassification.progression,
    "Luiginary Cone Jump": ItemClassification.progression,
    "Luiginary Cone Storm": ItemClassification.progression,
    "Luiginary Ball Throw": ItemClassification.progression,
    "Luiginary Ball Hookshot": ItemClassification.progression,
    "Pi'illo Castle Key": ItemClassification.progression,
    "Blimport Bridge": ItemClassification.progression,
    "Mushrise Park Gate": ItemClassification.progression,
    "First Dozite": ItemClassification.progression,
    "Dozite 1": ItemClassification.progression,
    "Dozite 2": ItemClassification.progression,
    "Dozite 3": ItemClassification.progression,
    "Dozite 4": ItemClassification.progression,
    "Access to Wakeport": ItemClassification.progression,
    "Access to Mount Pajamaja": ItemClassification.progression,
    "Dream Egg": ItemClassification.progression,
    "Access to Neo Bowser Castle": ItemClassification.progression,
    "Coin": ItemClassification.filler,
    "5 Coin": ItemClassification.filler,
    "10 Coin": ItemClassification.filler,
    "50 Coin": ItemClassification.filler,
    "100 Coin": ItemClassification.filler,
    "10x1 Coin": ItemClassification.filler,
    "10x5 Coin": ItemClassification.filler,
    "10x10 Coin": ItemClassification.filler,
    "10x50 Coin": ItemClassification.filler,
    "10x100 Coin": ItemClassification.filler,
    "Mushroom": ItemClassification.filler,
    "Super Mushroom": ItemClassification.filler,
    "Ultra Mushroom": ItemClassification.filler,
    "Max Mushroom": ItemClassification.filler,
    "Nut": ItemClassification.filler,
    "Super Nut": ItemClassification.filler,
    "Ultra Nut": ItemClassification.filler,
    "Max Nut": ItemClassification.filler,
    "Syrup Jar": ItemClassification.filler,
    "Supersyrup Jar": ItemClassification.filler,
    "Ultrasyrup Jar": ItemClassification.filler,
    "Max Syrup Jar": ItemClassification.filler,
    "Candy": ItemClassification.filler,
    "Super Candy": ItemClassification.filler,
    "Ultra Candy": ItemClassification.filler,
    "Max Candy": ItemClassification.filler,
    "1-Up Mushroom": ItemClassification.filler,
    "1-Up Deluxe": ItemClassification.filler,
    "Refreshing Herb": ItemClassification.filler,
    "Heart Bean": ItemClassification.filler,
    "Bros Bean": ItemClassification.filler,
    "Power Bean": ItemClassification.filler,
    "Defense Bean": ItemClassification.filler,
    "Speed Bean": ItemClassification.filler,
    "Stache Bean": ItemClassification.filler,
    "Taunt Ball": ItemClassification.filler,
    "Shock Bomb": ItemClassification.filler,
    "Boo Biscuit": ItemClassification.filler,
    "Secret Box": ItemClassification.filler,
    "Heart Bean DX": ItemClassification.filler,
    "Bros Bean DX": ItemClassification.filler,
    "Power Bean DX": ItemClassification.filler,
    "Defense Bean DX": ItemClassification.filler,
    "Speed Bean DX": ItemClassification.filler,
    "Stache Bean DX": ItemClassification.filler,
    "Run-Down Boots": ItemClassification.filler,
    "Discount Boots": ItemClassification.filler,
    "So-So Boots": ItemClassification.filler,
    "Picnic Boots": ItemClassification.filler,
    "Bare Boots": ItemClassification.filler,
    "Iron-Ball Boots": ItemClassification.filler,
    "Steady Boots": ItemClassification.filler,
    "Snare Boots": ItemClassification.filler,
    "Coin Boots": ItemClassification.filler,
    "Super Boots": ItemClassification.filler,
    "EXP Boots": ItemClassification.filler,
    "Knockout Boots": ItemClassification.filler,
    "Heart Boots": ItemClassification.filler,
    "Elite Boots": ItemClassification.filler,
    "Antiair Boots": ItemClassification.filler,
    "Action Boots": ItemClassification.filler,
    "Bros. Boots": ItemClassification.filler,
    "Singular Boots": ItemClassification.filler,
    "Glass Boots": ItemClassification.filler,
    "Coin Boots DX": ItemClassification.filler,
    "Iron-Ball Boots DX": ItemClassification.filler,
    "Celebrity Boots": ItemClassification.filler,
    "EXP Boots DX": ItemClassification.filler,
    "Antiair Boots DX": ItemClassification.filler,
    "Bare Boots DX": ItemClassification.filler,
    "Star Boots": ItemClassification.filler,
    "Dark Boots": ItemClassification.filler,
    "Crystal Boots": ItemClassification.filler,
    "Farmer Boots": ItemClassification.filler,
    "Master Boots": ItemClassification.filler,
    "Excellent Boots": ItemClassification.filler,
    "Expert Boots": ItemClassification.filler,
    "Hiking Boots": ItemClassification.filler,
    "Birthday Boots": ItemClassification.filler,
    "MINI Boots": ItemClassification.filler,
    "Run-Down Hammer": ItemClassification.filler,
    "Discount Hammer": ItemClassification.filler,
    "So-So Hammer": ItemClassification.filler,
    "Picnic Hammer": ItemClassification.filler,
    "Bare Hammer": ItemClassification.filler,
    "Iron-Ball Hammer": ItemClassification.filler,
    "Steady Hammer": ItemClassification.filler,
    "Fighter Hammer": ItemClassification.filler,
    "Sap Hammer": ItemClassification.filler,
    "Super Hammer": ItemClassification.filler,
    "Soft Hammer": ItemClassification.filler,
    "Knockout Hammer": ItemClassification.filler,
    "Flame Hammer": ItemClassification.filler,
    "Elite Hammer": ItemClassification.filler,
    "Blunt Hammer": ItemClassification.filler,
    "Action Hammer": ItemClassification.filler,
    "Spin Hammer": ItemClassification.filler,
    "Singular Hammer": ItemClassification.filler,
    "Glass Hammer": ItemClassification.filler,
    "Sap Hammer DX": ItemClassification.filler,
    "Iron-Ball Hammer DX": ItemClassification.filler,
    "Celebrity Hammer": ItemClassification.filler,
    "Flame Hammer DX": ItemClassification.filler,
    "Blunt Hammer DX": ItemClassification.filler,
    "Bare Hammer DX": ItemClassification.filler,
    "Star Hammer": ItemClassification.filler,
    "Dark Hammer": ItemClassification.filler,
    "Crystal Hammer": ItemClassification.filler,
    "Soft Hammer DX": ItemClassification.filler,
    "Master Hammer": ItemClassification.filler,
    "Excellent Hammer": ItemClassification.filler,
    "Expert Hammer": ItemClassification.filler,
    "Golden Hammer": ItemClassification.filler,
    "Birthday Hammer": ItemClassification.filler,
    "MINI Hammer": ItemClassification.filler,
    "Thin Wear": ItemClassification.filler,
    "Picnic Wear": ItemClassification.filler,
    "Cozy Wear": ItemClassification.filler,
    "So-So Wear": ItemClassification.filler,
    "Payback Wear": ItemClassification.filler,
    "Singular Wear": ItemClassification.filler,
    "Rally Wear": ItemClassification.filler,
    "Charge Wear": ItemClassification.filler,
    "Super Wear": ItemClassification.filler,
    "Fighter Wear": ItemClassification.filler,
    "Koopa Troopa Wear": ItemClassification.filler,
    "Celebrity Wear": ItemClassification.filler,
    "Counter Wear": ItemClassification.filler,
    "Safety Wear": ItemClassification.filler,
    "Fancy Wear": ItemClassification.filler,
    "Hero Wear": ItemClassification.filler,
    "Bros. Wear": ItemClassification.filler,
    "Metal Wear": ItemClassification.filler,
    "Snare Wear": ItemClassification.filler,
    "Heart Wear": ItemClassification.filler,
    "Energy Wear": ItemClassification.filler,
    "Star Wear": ItemClassification.filler,
    "Ironclad Wear": ItemClassification.filler,
    "King Wear": ItemClassification.filler,
    "Angel Wear": ItemClassification.filler,
    "Pro Wear": ItemClassification.filler,
    "Legendary Wear": ItemClassification.filler,
    "Expert Wear": ItemClassification.filler,
    "Golden Wear": ItemClassification.filler,
    "Birthday Wear": ItemClassification.filler,
    "Thick Gloves": ItemClassification.filler,
    "Shell Gloves": ItemClassification.filler,
    "Metal Gloves": ItemClassification.filler,
    "HP Gloves": ItemClassification.filler,
    "HP Gloves DX": ItemClassification.filler,
    "BP Gloves": ItemClassification.filler,
    "BP Gloves DX": ItemClassification.filler,
    "POW Gloves": ItemClassification.filler,
    "POW Gloves DX": ItemClassification.filler,
    "Speed Gloves": ItemClassification.filler,
    "Stache Gloves": ItemClassification.filler,
    "Lucky Gloves": ItemClassification.filler,
    "Lucky Gloves DX": ItemClassification.filler,
    "Gift Gloves": ItemClassification.filler,
    "Gift Gloves DX": ItemClassification.filler,
    "Charge Gloves": ItemClassification.filler,
    "Charge Gloves DX": ItemClassification.filler,
    "Strike Gloves": ItemClassification.filler,
    "Mushroom Gloves": ItemClassification.filler,
    "1-Up Gloves": ItemClassification.filler,
    "Master Gloves": ItemClassification.filler,
    "Rookie Gloves": ItemClassification.filler,
    "Perfect POW Gloves": ItemClassification.filler,
    "Perfect Bro Gloves": ItemClassification.filler,
    "Coin Bro Gloves": ItemClassification.filler,
    "Coin Bro Gloves DX": ItemClassification.filler,
    "EXP Bro Gloves": ItemClassification.filler,
    "EXP Bro Gloves DX": ItemClassification.filler,
    "Bottomless Gloves": ItemClassification.filler,
    "MINI Gloves": ItemClassification.filler,
    "HP Scarf": ItemClassification.filler,
    "HP Scarf DX": ItemClassification.filler,
    "BP Scarf": ItemClassification.filler,
    "BP Scarf DX": ItemClassification.filler,
    "POW Scarf": ItemClassification.filler,
    "POW Scarf DX": ItemClassification.filler,
    "Speed Scarf": ItemClassification.filler,
    "Stache Scarf": ItemClassification.filler,
    "Bros. Ring": ItemClassification.filler,
    "HP Bangle": ItemClassification.filler,
    "HP Bangle DX": ItemClassification.filler,
    "BP Bangle": ItemClassification.filler,
    "BP Bangle DX": ItemClassification.filler,
    "Angel Bangle": ItemClassification.filler,
    "HP Knockout Bangle": ItemClassification.filler,
    "BP Knockout Bangle": ItemClassification.filler,
    "Healthy Ring": ItemClassification.filler,
    "Guard Shell": ItemClassification.filler,
    "Guard Shell DX": ItemClassification.filler,
    "Rally Belt": ItemClassification.filler,
    "Counter Belt": ItemClassification.filler,
    "POW Mush Jam": ItemClassification.filler,
    "DEF Mush Jam": ItemClassification.filler,
    "Duplex Crown": ItemClassification.filler,
    "UNUSED": ItemClassification.filler,
    "Mushroom Amulet": ItemClassification.filler,
    "Birthday Ring": ItemClassification.filler,
    "Mini Ring (UNUSED)": ItemClassification.filler,
    "Silver Statue": ItemClassification.filler,
    "Gold Statue": ItemClassification.filler,
    "Attack Piece": ItemClassification.useful
}


# Each Item instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Item class and override the "game" field.
class MLDTItem(Item):
    game = "Mario and Luigi Dream Team"


# Ontop of our regular itempool, our world must be able to create arbitrary amounts of filler as requested by core.
# To do this, it must define a function called world.get_filler_item_name(), which we will define in world.py later.
# For now, let's make a function that returns the name of a random filler item here in items.py.
def get_random_filler_item_name(world: MLDTWorld) -> str:
    # APQuest has an option called "trap_chance".
    # This is the percentage chance that each filler item is a Math Trap instead of a Confetti Cannon.
    # For this purpose, we need to use a random generator.

    # IMPORTANT: Whenever you need to use a random generator, you must use world.random.
    # This ensures that generating with the same generator seed twice yields the same output.
    # DO NOT use a bare random object from Python's built-in random module.
    #if world.random.randint(0, 99) < world.options.trap_chance:
    #    return "Math Trap"
    return "Coin"


def create_item_with_correct_classification(world: MLDTWorld, name: str) -> MLDTItem:
    # Our world class must have a create_item() function that can create any of our items by name at any time.
    # So, we make this helper function that creates the item by name with the correct classification.
    # Note: This function's content could just be the contents of world.create_item in world.py directly,
    # but it seemed nicer to have it in its own function over here in items.py.
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    # It is perfectly normal and valid for an item's classification to differ based on the player's options.
    # In our case, Health Upgrades are only relevant to logic (and thus labeled as "progression") in hard mode.
    #if name == "Health Upgrade" and world.options.hard_mode:
    #    classification = ItemClassification.progression

    return MLDTItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: MLDTWorld) -> None:
    # This is the function in which we will create all the items that this world submits to the multiworld item pool.
    # There must be exactly as many items as there are locations.
    # In our case, there are either six or seven locations.
    # We must make sure that when there are six locations, there are six items,
    # and when there are seven locations, there are seven items.

    # Creating items should generally be done via the world's create_item method.
    # First, we create a list containing all the items that always exist.

    itempool: list[Item] = [
        world.create_item("Progressive Hammers"),
        world.create_item("Progressive Hammers"),
        world.create_item("Progressive Hammers"),
        world.create_item("Progressive Spin"),
        world.create_item("Progressive Spin"),
        world.create_item("Ball Hop"),
        world.create_item("Luiginary Works"),
        world.create_item("Luiginary Ball"),
        world.create_item("Luiginary Stack Spring Jump"),
        world.create_item("Luiginary Stack Ground Pound"),
        world.create_item("Luiginary Cone Jump"),
        world.create_item("Luiginary Cone Storm"),
        world.create_item("Luiginary Ball Throw"),
        world.create_item("Luiginary Ball Hookshot"),
        world.create_item("Pi'illo Castle Key"),
        world.create_item("Blimport Bridge"),
        world.create_item("Mushrise Park Gate"),
        world.create_item("First Dozite"),
        world.create_item("Dozite 1"),
        world.create_item("Dozite 2"),
        world.create_item("Dozite 3"),
        world.create_item("Dozite 4"),
        world.create_item("Access to Wakeport"),
        world.create_item("Access to Mount Pajamaja"),
        world.create_item("Dream Egg"),
        world.create_item("Dream Egg"),
        world.create_item("Dream Egg"),
        world.create_item("Access to Neo Bowser Castle"),
    ]

    item_names = ["5 Coin", "10 Coin", "50 Coin", "100 Coin", "10x1 Coin", "10x5 Coin", "10x10 Coin", "10x50 Coin", "10x100 Coin",
                  
                  "Mushroom", "Super Mushroom", "Ultra Mushroom", "Max Mushroom", "Nut", "Super Nut", "Ultra Nut", "Max Nut",
                  "Syrup Jar", "Supersyrup Jar", "Ultrasyrup Jar", "Max Syrup Jar", "Candy", "Super Candy", "Ultra Candy", "Max Candy",
                  "1-Up Mushroom", "1-Up Deluxe", "Refreshing Herb", "Heart Bean", "Bros Bean", "Power Bean", "Defense Bean",
                  "Speed Bean", "Stache Bean", "Taunt Ball", "Shock Bomb", "Boo Biscuit", "Secret Box",
                  "Heart Bean DX", "Bros Bean DX", "Power Bean DX", "Defense Bean DX", "Speed Bean DX", "Stache Bean DX",
                  
                  "Run-Down Boots", "Discount Boots", "So-So Boots", "Picnic Boots", "Bare Boots", "Iron-Ball Boots", "Steady Boots",
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
                  "Gold Statue",
                  
                  "Attack Piece"]
    
    #Vanilla item amounts
    item_amounts = [63, 61, 53, 26, 19, 29, 20, 23, 3,
                    8, 9, 18, 7, 9, 12, 11, 9, 8, 14, 19, 9, 8, 13, 19, 13, 12, 13, 22, 24, 24, 24, 24, 23, 24, 7, 7, 5, 10, 0, 0, 0, 0, 0, 0,
                    0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 
                    0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 4, 2,
                    150]
    
    #Custom item amounts
    #item_amounts = [189, 63, 61, 53, 26, 19, 29, 20, 23, 3,
    #                10, 11, 20, 9, 11, 14, 13, 11, 10, 16, 21, 11, 10, 15, 21, 15, 12, 13, 22, 24, 24, 24, 24, 23, 24, 7, 7, 5, 10, 3, 3, 3, 3, 3, 3,
    #                0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 
    #                0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0]

    for item in range(len(item_amounts)):
        for a in range(item_amounts[item]):
            #print(item_names[item])
            itempool.append(world.create_item(item_names[item]))

    # Archipelago requires that each world submits as many locations as it submits items.
    # This is where we can use our filler and trap items.
    # APQuest has two of these: The Confetti Cannon and the Math Trap.
    # (Unfortunately, Archipelago is a bit ambiguous about its terminology here:
    #  "filler" is an ItemClassification separate from "trap", but in a lot of its functions,
    #  Archipelago will use "filler" to just mean "an additional item created to fill out the itempool".
    #  "Filler" in this sense can technically have any ItemClassification,
    #  but most commonly ItemClassification.filler or ItemClassification.trap.
    #  Starting here, the word "filler" will be used to collectively refer to APQuest's Confetti Cannon and Math Trap,
    #  which are ItemClassification.filler and ItemClassification.trap respectively.)
    # Creating filler items works the same as any other item. But there is a question:
    # How many filler items do we actually need to create?
    # In regions.py, we created either six or seven locations depending on the "extra_starting_chest" option.
    # In this function, we have created five or six items depending on whether the "hammer" option is enabled.
    # We *could* have a really complicated if-else tree checking the options again, but there is a better way.
    # We can compare the size of our itempool so far to the number of locations in our world.

    # The length of our itempool is easy to determine, since we have it as a list.
    number_of_items = len(itempool)

    # The number of locations is also easy to determine, but we have to be careful.
    # Just calling len(world.get_locations()) would report an incorrect number, because of our *event locations*.
    # What we actually want is the number of *unfilled* locations. Luckily, there is a helper method for this:
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    # Now, we just subtract the number of items from the number of locations to get the number of empty item slots.
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

    # Finally, we create that many filler items and add them to the itempool.
    # To create our filler, we could just use world.create_item("Confetti Cannon").
    # But there is an alternative that works even better for most worlds, including APQuest.
    # As discussed above, our world must have a get_filler_item_name() function defined,
    # which must return the name of an infinitely repeatable filler item.
    # Defining this function enables the use of a helper function called world.create_filler().
    # You can just use this function directly to create as many filler items as you need to complete your itempool.
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    # But... is that the right option for your game? Let's explore that.
    # For some games, the concepts of "regular itempool filler" and "additionally created filler" are different.
    # These games might want / require specific amounts of specific filler items in their regular pool.
    # To achieve this, they will have to intentionally create the correct quantities using world.create_item().
    # They may still use world.create_filler() to fill up the rest of their itempool with "repeatable filler",
    # after creating their "specific quantity" filler and still having room left over.

    # But there are many other games which *only* have infinitely repeatable filler items.
    # They don't care about specific amounts of specific filler items, instead only caring about the proportions.
    # In this case, world.create_filler() can just be used for the entire filler itempool.
    # APQuest is one of these games:
    # Regardless of whether it's filler for the regular itempool or additional filler for item links / etc.,
    # we always just want a Confetti Cannon or a Math Trap depending on the "trap_chance" option.
    # We defined this behavior in our get_random_filler_item_name() function, which in world.py,
    # we'll bind to world.get_filler_item_name(). So, we can just use world.create_filler() for all of our filler.

    # Anyway. With our world's itempool finalized, we now need to submit it to the multiworld itempool.
    # This is how the generator actually knows about the existence of our items.
    world.multiworld.itempool += itempool
