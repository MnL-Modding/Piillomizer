from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

# In this file, we define the options the player can pick.
# The most common types of options are Toggle, Range and Choice.

# Options will be in the game's template yaml.
# They will be represented by checkboxes, sliders etc. on the game's options page on the website.
# (Note: Options can also be made invisible from either of these places by overriding Option.visibility.
#  APQuest doesn't have an example of this, but this can be used for secret / hidden / advanced options.)

# For further reading on options, you can also read the Options API Document:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md


# The first type of Option we'll discuss is the Toggle.
# A toggle is an option that can either be on or off. This will be represented by a checkbox on the website.
# The default for a toggle is "off".
# If you want a toggle to be on by default, you can use the "DefaultOnToggle" class instead of the "Toggle" class.

class Hammer(Choice):
    """
    Allows you to choose what your second progressive hammer is
    """

    display_name = "Hammer"

    option_random_hammer = -1
    option_mini_mario = 0
    option_mole_mario = 1

    # Choice options must define an explicit default value.
    default = option_random_hammer
    
class ReduceMini(Choice):
    """
    Automatically hits the switches to enter Mount Pajamaja, Somnom Woods/Neo Bowser Castle, and Driftwood Shore
    """

    display_name = "Reduce Mini Mario Requirements"

    option_on = True
    option_off = False

    # Choice options must define an explicit default value.
    default = option_off
    
class ReduceBall(Choice):
    """
    Removes some major Ball Hop skips in Mount Pajamaja and Dozing Sands (that negate 6 key items)
    """

    display_name = "Reduce Ball Hop Skips"

    option_on = True
    option_off = False

    # Choice options must define an explicit default value.
    default = option_on

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class MLDTOptions(PerGameCommonOptions):
    second_hammer: Hammer
    reduce_mini: ReduceMini
    reduce_ball_skips: ReduceBall


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Gameplay Options",
        [Hammer, ReduceMini, ReduceBall],
    ),
]

# Finally, we can define some option presets if we want the player to be able to quickly choose a specific "mode".
option_presets = {
    "normal": {
        "second_hammer": -1,
        "reduce_mini": False,
        "reduce_ball_skips": True
    },
    "creator's preset": {
        "second_hammer": 1,
        "reduce_mini": True,
        "reduce_ball_skips": True
    },
}
