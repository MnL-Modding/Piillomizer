from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAll, Rule

if TYPE_CHECKING:
    from .world import MLDTWorld

HAS_KEY = Has("Key")  # Hmm, what could this be? A little foreshadowing perhaps? :) You'll find out if you keep reading!


def set_all_rules(world: MLDTWorld) -> None:
    # In order for AP to generate an item layout that is actually possible for the player to complete,
    # we need to define rules for our Entrances and Locations.
    # Note: Regions do not have rules, the Entrances connecting them do!
    # We'll do entrances first, then locations, and then finally we set our victory condition.

    #Sets the second progressive hammer to a random hammer if that option is chosen
    if world.options.second_hammer == -1:
        world.options.second_hammer.value = world.random.randint(0, 1)
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: MLDTWorld) -> None:
    # First, we need to actually grab our entrances. Luckily, there is a helper method for this.
    blimport_to_piillo_castle = world.get_entrance("Blimport to Pi'illo Castle")
    blimport_to_underground = world.get_entrance("Blimport to Blimport Underground")
    blimport_to_mushrise_park = world.get_entrance("Blimport to Mushrise Park")
    blimport_to_mount_pajamaja = world.get_entrance("Blimport to Mount Pajamaja")
    piillo_castle_to_deep = world.get_entrance("Pi'illo Castle to Pi'illo Castle Dream's Deep")
    mushrise_park_to_hammer = world.get_entrance("Mushrise Park to Hammer Area")
    mushrise_park_to_gate = world.get_entrance("Mushrise Park to Dozing/Driftwood Outskirts")
    mushrise_park_to_wakeport = world.get_entrance("Mushrise Park to Wakeport")
    mushrise_park_to_somnom = world.get_entrance("Mushrise Park to Somnom Woods")
    mushrise_park_to_neo_castle = world.get_entrance("Mushrise Park to Neo Bowser Castle")
    past_gate_to_tracks = world.get_entrance("Dozing/Driftwood Outskirts to Dozing Track Area")
    past_gate_to_dreamstone = world.get_entrance("Dozing/Driftwood Outskirts to Dozing Ultibed")
    past_gate_to_driftwood = world.get_entrance("Dozing/Driftwood Outskirts to Driftwood Dreampoints")
    wakeport_to_ultibed = world.get_entrance("Wakeport to Wakeport Ultibed")
    pajamaja_entrance_to_base = world.get_entrance("Mount Pajamaja Entrance to Mount Pajamaja Base")
    pajamaja_entrance_to_peak = world.get_entrance("Mount Pajamaja Entrance to Mount Pajamaja Peak")
    pajamaja_base_to_middle = world.get_entrance("Mount Pajamaja Base to Mount Pajamaja Middle")
    pajamaja_middle_to_peak = world.get_entrance("Mount Pajamaja Middle to Mount Pajamaja Peak")
    pajamaja_peak_to_dreampoint = world.get_entrance("Mount Pajamaja Peak to Mount Pajamaja Summit Dream")
    driftwood_to_egg = world.get_entrance("Driftwood Shore Dreampoints to Driftwood Shore Eggs")
    somnom_to_tracks = world.get_entrance("Somnom Woods Entrance to Somnom Woods Tracks")
    somnom_tracks_to_past_tracks = world.get_entrance("Somnom Woods Tracks to Somnom Woods After Tracks")
    neo_bowser_entrance_to_spin = world.get_entrance("Neo Bowser Castle Entrance to Neo Bowser Castle Spin")
    neo_bowser_spin_to_flame = world.get_entrance("Neo Bowser Castle Spin to Neo Bowser Castle Flames")
    neo_bowser_flame_to_dream = world.get_entrance("Neo Bowser Castle Flames to Neo Bowser Castle Dream")

    hammers = Has("Progressive Hammers")
    mini_mario = Has("Progressive Hammers", count=(2 + world.options.second_hammer))
    mole_mario = Has("Progressive Hammers", count=(3 - world.options.second_hammer))
    spin_jump = Has("Progressive Spin")
    side_drill = Has("Progressive Spin", count=2)
    ball_hop = Has("Ball Hop")
    luigi_works = Has("Luiginary Works")
    luigi_ball = Has("Luiginary Ball")
    luigi_stack_spring = Has("Luiginary Stack Spring Jump")
    luigi_stack_pound = Has("Luiginary Stack Ground Pound")
    luigi_cone_jump = Has("Luiginary Cone Jump")
    luigi_cone_storm = Has("Luiginary Cone Storm")
    luigi_ball_hammer = Has("Luiginary Ball Throw")
    luigi_ball_hookshot = Has("Luiginary Ball Hookshot")
    has_piillo_key = Has("Pi'illo Castle Key")
    has_bridge = Has("Blimport Bridge")
    has_gate = Has("Mushrise Park Gate")
    has_first_dozite = Has("First Dozite")
    has_dozites = Has("Dozite 1") & Has("Dozite 2") & Has("Dozite 3") & Has("Dozite 4")
    has_wakeport_access = Has("Access to Wakeport")
    has_pajamaja_access = Has("Access to Mount Pajamaja")
    has_egg = Has("Dream Egg")
    has_neo_bowser_access = Has("Access to Neo Bowser Castle")

    blimport_to_piillo_castle_logic = has_piillo_key
    blimport_to_underground_logic = has_bridge
    blimport_to_mushrise_park_logic = has_bridge
    blimport_to_mount_pajamaja_logic = mini_mario
    piillo_castle_to_deep_logic = has_piillo_key & luigi_works & luigi_ball & luigi_stack_spring & luigi_ball_hammer & luigi_ball_hookshot
    mushrise_park_to_hammer_logic = has_bridge & hammers
    mushrise_park_to_gate_logic = has_bridge & has_gate
    mushrise_park_to_wakeport_logic = has_bridge & has_wakeport_access
    mushrise_park_to_somnom_logic = has_bridge & ball_hop & mini_mario
    mushrise_park_to_neo_castle_logic = has_bridge & ball_hop & mini_mario & has_neo_bowser_access
    past_gate_to_tracks_logic = has_bridge & has_gate & has_first_dozite & (mini_mario | mole_mario)
    past_gate_to_dreamstone_logic = has_bridge & has_gate & has_first_dozite & has_dozites
    past_gate_to_driftwood_logic = has_bridge & has_gate & mini_mario & spin_jump
    wakeport_to_ultibed_logic = has_piillo_key & has_bridge & has_wakeport_access & has_gate & has_first_dozite & has_dozites & has_pajamaja_access & mini_mario & mole_mario & side_drill & ball_hop & luigi_works & luigi_ball & luigi_ball_hammer & luigi_stack_spring & luigi_cone_jump
    pajamaja_entrance_to_base_logic = has_pajamaja_access & mini_mario
    pajamaja_entrance_to_peak_logic = has_pajamaja_access & mini_mario & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump
    pajamaja_base_to_middle_logic = has_pajamaja_access & mini_mario & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump
    pajamaja_middle_to_peak_logic = has_pajamaja_access & mini_mario & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump
    pajamaja_peak_to_dreampoint_logic = has_pajamaja_access & mini_mario & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump & luigi_cone_storm
    driftwood_to_egg_logic = has_bridge & has_gate & mini_mario & spin_jump & luigi_works & has_egg
    somnom_to_tracks_logic = has_bridge & mini_mario & side_drill & luigi_works
    somnom_tracks_to_past_tracks_logic = has_bridge & mini_mario & mole_mario & side_drill & luigi_works
    neo_bowser_entrance_to_spin_logic = has_bridge & mini_mario & has_neo_bowser_access & spin_jump
    neo_bowser_spin_to_flame_logic = has_bridge & mini_mario & has_neo_bowser_access & spin_jump & luigi_works
    neo_bowser_flame_to_dream_logic = has_bridge & mini_mario & has_neo_bowser_access & spin_jump & luigi_works & luigi_ball & luigi_stack_spring & luigi_stack_pound & luigi_cone_jump & luigi_ball_hammer & luigi_ball_hookshot
    
    if world.options.reduce_mini:
        blimport_to_mount_pajamaja_logic = None
        mushrise_park_to_somnom_logic = has_bridge & ball_hop & hammers
        mushrise_park_to_neo_castle_logic = has_bridge & ball_hop & has_neo_bowser_access
        past_gate_to_driftwood_logic = has_bridge & has_gate & hammers & spin_jump
        pajamaja_entrance_to_base_logic = has_pajamaja_access & hammers
        pajamaja_entrance_to_peak_logic = has_pajamaja_access & hammers & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump
        pajamaja_base_to_middle_logic = has_pajamaja_access & hammers & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump
        pajamaja_middle_to_peak_logic = has_pajamaja_access & hammers & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump
        pajamaja_peak_to_dreampoint_logic = has_pajamaja_access & hammers & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump & luigi_cone_storm
        driftwood_to_egg_logic = has_bridge & has_gate & hammers & spin_jump & luigi_works & has_egg
        somnom_to_tracks_logic = has_bridge & hammers & side_drill & luigi_works
        somnom_tracks_to_past_tracks_logic = has_bridge & mole_mario & side_drill & luigi_works
        neo_bowser_entrance_to_spin_logic = has_bridge & hammers & has_neo_bowser_access & spin_jump
        neo_bowser_spin_to_flame_logic = has_bridge & hammers & has_neo_bowser_access & spin_jump & luigi_works
        neo_bowser_flame_to_dream_logic = has_bridge & hammers & has_neo_bowser_access & spin_jump & luigi_works & luigi_ball & luigi_stack_spring & luigi_stack_pound & luigi_cone_jump & luigi_ball_hammer & luigi_ball_hookshot
    
    if not world.options.reduce_ball_skips:
        past_gate_to_tracks_logic = has_bridge & has_gate & (ball_hop | has_first_dozite) & (mini_mario | mole_mario)
        past_gate_to_dreamstone_logic = has_bridge & has_gate & ((has_first_dozite & has_dozites) | ball_hop)
        pajamaja_entrance_to_base_logic = (has_pajamaja_access | ball_hop) & mini_mario
        pajamaja_entrance_to_peak_logic = ((has_pajamaja_access & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump) | ball_hop) & mini_mario
        pajamaja_base_to_middle_logic = ((has_pajamaja_access & luigi_works & luigi_stack_spring & luigi_cone_jump) | ball_hop) & side_drill & mini_mario
        pajamaja_middle_to_peak_logic = ((has_pajamaja_access & luigi_works & luigi_stack_spring & luigi_cone_jump) | ball_hop) & side_drill & mini_mario
        pajamaja_peak_to_dreampoint_logic = ((has_pajamaja_access & side_drill) | (ball_hop & spin_jump)) & mini_mario & luigi_works & luigi_stack_spring & luigi_cone_jump & luigi_cone_storm

    if world.options.reduce_mini and not world.options.reduce_ball_skips:
        blimport_to_mount_pajamaja_logic = None
        pajamaja_entrance_to_base_logic = (has_pajamaja_access | ball_hop) & hammers
        pajamaja_entrance_to_peak_logic = ((has_pajamaja_access & side_drill & luigi_works & luigi_stack_spring & luigi_cone_jump) | ball_hop) & hammers
        pajamaja_base_to_middle_logic = ((has_pajamaja_access & luigi_works & luigi_stack_spring & luigi_cone_jump) | ball_hop) & side_drill & hammers
        pajamaja_middle_to_peak_logic = ((has_pajamaja_access & luigi_works & luigi_stack_spring & luigi_cone_jump) | ball_hop) & side_drill & hammers
        pajamaja_peak_to_dreampoint_logic = ((has_pajamaja_access & side_drill) | (ball_hop & spin_jump)) & hammers & luigi_works & luigi_stack_spring & luigi_cone_jump & luigi_cone_storm

    world.set_rule(blimport_to_piillo_castle, blimport_to_piillo_castle_logic)
    world.set_rule(blimport_to_underground, blimport_to_underground_logic)
    world.set_rule(blimport_to_mushrise_park, blimport_to_mushrise_park_logic)
    if not world.options.reduce_mini:
        world.set_rule(blimport_to_mount_pajamaja, blimport_to_mount_pajamaja_logic)
    world.set_rule(piillo_castle_to_deep, piillo_castle_to_deep_logic)
    world.set_rule(mushrise_park_to_hammer, mushrise_park_to_hammer_logic)
    world.set_rule(mushrise_park_to_gate, mushrise_park_to_gate_logic)
    world.set_rule(mushrise_park_to_wakeport, mushrise_park_to_wakeport_logic)
    world.set_rule(mushrise_park_to_somnom, mushrise_park_to_somnom_logic)
    world.set_rule(mushrise_park_to_neo_castle, mushrise_park_to_neo_castle_logic)
    world.set_rule(past_gate_to_tracks, past_gate_to_tracks_logic)
    world.set_rule(past_gate_to_dreamstone, past_gate_to_dreamstone_logic)
    world.set_rule(past_gate_to_driftwood, past_gate_to_driftwood_logic)
    world.set_rule(wakeport_to_ultibed, wakeport_to_ultibed_logic)
    world.set_rule(pajamaja_entrance_to_base, pajamaja_entrance_to_base_logic)
    world.set_rule(pajamaja_entrance_to_peak, pajamaja_entrance_to_peak_logic)
    world.set_rule(pajamaja_base_to_middle, pajamaja_base_to_middle_logic)
    world.set_rule(pajamaja_middle_to_peak, pajamaja_middle_to_peak_logic)
    world.set_rule(pajamaja_peak_to_dreampoint, pajamaja_peak_to_dreampoint_logic)
    world.set_rule(driftwood_to_egg, driftwood_to_egg_logic)
    world.set_rule(somnom_to_tracks, somnom_to_tracks_logic)
    world.set_rule(somnom_tracks_to_past_tracks, somnom_tracks_to_past_tracks_logic)
    world.set_rule(neo_bowser_entrance_to_spin, neo_bowser_entrance_to_spin_logic)
    world.set_rule(neo_bowser_spin_to_flame, neo_bowser_spin_to_flame_logic)
    world.set_rule(neo_bowser_flame_to_dream, neo_bowser_flame_to_dream_logic)

    # Now, let's make some rules!
    # First, let's handle the transition from the overworld to the bottom right room,
    # which requires slashing a bush with the Sword.
    # For this, we need a rule that says "player has a Sword".
    # We can use a "Has"-type rule from the rule_builder module for this.
    #can_destroy_bush = Has("Sword")

    # Now we can set our "can_destroy_bush" rule to the entrance which requires slashing a bush to clear the path.
    # The easiest way to do this is by calling world.set_rule, which works for both Locations and Entrances.
    #world.set_rule(overworld_to_bottom_right_room, can_destroy_bush)

    # Conditions can also depend on event items.
    #button_pressed = Has("Top Left Room Button Pressed")
    #world.set_rule(right_room_to_final_boss_room, button_pressed)

    # Some entrance rules may only apply if the player enabled certain options.
    # In our case, if the hammer option is enabled, we need to add the Hammer requirement to the Entrance from
    # Overworld to the Top Middle Room.
    #if world.options.hammer:
    #    overworld_to_top_middle_room = world.get_entrance("Overworld to Top Middle Room")
    #    can_smash_brick = Has("Hammer")
    #    world.set_rule(overworld_to_top_middle_room, can_smash_brick)

    # So far, we've been using "Has" from the Rule Builder to make our rules.
    # There is another way to make rules that you will see in a lot of older worlds.
    # A rule can just be a function that takes a "state" argument and returns a bool.
    # As a demonstration of what that looks like, let's do it with our final Entrance rule:
    #world.set_rule(overworld_to_top_left_room, lambda state: state.has("Key", world.player))
    # This style is not really recommended anymore, though.
    # Notice how you have to explicitly capture world.player here so that the rule applies to the correct player?
    # Well, Rule Builder does this part for you, inside of world.set_rule.
    # This doesn't just result in shorter code, it also means you can define rules statically (at the module level).
    # APQuest opts to create its Rule objects locally, but just to show what this would look like,
    # we'll re-set the "Overworld to Top Left Room" rule to a constant defined at the top of this file:
    #world.set_rule(overworld_to_top_left_room, HAS_KEY)

    # Beyond these structural advantages,
    # Rule Builder also allows the core AP code to do a lot of under-the-hood optimizations.
    # Rule Builder is quite comprehensive, and even if you have really esoteric rules,
    # you can make custom rules by subclassing CustomRule.

def set_all_location_rules(world: MLDTWorld) -> None:
    # Location rules work no differently from Entrance rules.
    # Most of our locations are chests that can simply be opened by walking up to them.
    # Thus, their logical requirements are covered by the Entrance rules of the Entrances that were required to
    # reach the region that the chest sits in.
    # However, our two enemies work differently.
    # Entering the room with the enemy is not enough, you also need to have enough combat items to be able to defeat it.
    # So, we need to set requirements on the Locations themselves.
    # Since combat is a bit more complicated, we'll use this chance to cover some advanced access rule concepts.

    hammers = Has("Progressive Hammers")
    mini_mario = Has("Progressive Hammers", count=(2 + world.options.second_hammer))
    mole_mario = Has("Progressive Hammers", count=(3 - world.options.second_hammer))
    spin_jump = Has("Progressive Spin")
    side_drill = Has("Progressive Spin", count=2)
    ball_hop = Has("Ball Hop")
    luigi_works = Has("Luiginary Works")
    luigi_ball = Has("Luiginary Ball")
    luigi_stack_spring = Has("Luiginary Stack Spring Jump")
    luigi_stack_pound = Has("Luiginary Stack Ground Pound")
    luigi_cone_jump = Has("Luiginary Cone Jump")
    luigi_cone_storm = Has("Luiginary Cone Storm")
    luigi_ball_hammer = Has("Luiginary Ball Throw")
    luigi_ball_hookshot = Has("Luiginary Ball Hookshot")
    has_piillo_key = Has("Pi'illo Castle Key")
    has_bridge = Has("Blimport Bridge")
    has_gate = Has("Mushrise Park Gate")
    has_first_dozite = Has("First Dozite")
    has_dozites = Has("Dozite 1") & Has("Dozite 2") & Has("Dozite 3") & Has("Dozite 4")
    has_wakeport_access = Has("Access to Wakeport")
    has_pajamaja_access = Has("Access to Mount Pajamaja")
    has_two_eggs = Has("Dream Egg", count=2)
    has_all_eggs = Has("Dream Egg", count=3)
    has_neo_bowser_access = Has("Access to Neo Bowser Castle")
    
    #The logic info for each location
    # [Location ID within region, logic]
    location_logic_info = [[[12, mole_mario], [13, mole_mario], [14, mole_mario], [15, mole_mario], [16, mole_mario], [17, mole_mario]],
                           
                           [[4, ball_hop], [8, has_bridge], [9, has_bridge], [11, has_bridge], [21, has_bridge & ball_hop],
                            [22, has_bridge & ball_hop], [23, has_bridge & ball_hop], [24, has_bridge & ball_hop], [25, has_bridge & ball_hop]],

                           [], #Just because a region doesn't have any extra logic needed, doesn't mean we should leave it out
                           
                           [[1, luigi_works], [2, luigi_works], [3, luigi_works], [4, luigi_works], [5, luigi_works], [6, luigi_works],
                            [7, luigi_works], [8, luigi_works], [9, luigi_works], [10, luigi_works], [11, luigi_works], [12, luigi_works],
                            [13, luigi_works], [14, luigi_works], [15, luigi_works], [16, luigi_works], [17, luigi_works], [18, luigi_works],
                            [19, luigi_works], [20, luigi_works], [21, luigi_works], [22, luigi_works], [23, luigi_works], [24, luigi_works],
                            [25, luigi_works], [26, luigi_works], [27, luigi_works], [28, luigi_works], [29, luigi_works], [30, luigi_works],
                            [31, luigi_works], [32, luigi_works], [33, luigi_works], [34, luigi_works], [35, luigi_works], [36, luigi_works],
                            [37, luigi_works], [38, luigi_works], [39, luigi_works], [40, luigi_works], [41, luigi_works], [42, luigi_works]],
                            
                           [[1, ball_hop], [2, ball_hop], [4, hammers | spin_jump | ball_hop], [5, hammers], [6, hammers],
                            [7, hammers], [10, has_gate & mini_mario], [11, hammers], [18, side_drill], [19, side_drill],
                            [22, hammers], [23, hammers], [24, luigi_works], [25, luigi_works], [26, luigi_works], [27, luigi_works],
                            [28, luigi_works], [29, luigi_works], [30, luigi_works], [31, luigi_works], [32, luigi_works], [33, luigi_works],
                            [34, luigi_works], [35, luigi_works], [36, luigi_works], [37, luigi_works], [38, luigi_works],
                            [39, luigi_works], [40, luigi_works], [41, luigi_works], [42, luigi_works], [43, luigi_works],
                            [44, luigi_works], [45, luigi_works], [46, luigi_works], [47, luigi_works], [48, luigi_works],
                            [50, luigi_works], [51, luigi_works], [52, luigi_works], [53, spin_jump], [54, luigi_works], [55, mini_mario], 
                            [56, spin_jump | ball_hop], [57, spin_jump & ball_hop], [58, ball_hop], [59, mini_mario], [60, mini_mario],
                            [61, mole_mario], [62, mole_mario], [63, mole_mario], [64, mole_mario], [65, mole_mario & has_gate], 
                            [66, mole_mario], [67, mole_mario], [68, mole_mario], [69, mole_mario], [70, mole_mario], 
                            [71, (spin_jump | ball_hop) & mole_mario], [72, mole_mario], [73, mole_mario], [74, mole_mario],
                            [75, mole_mario], [76, mole_mario], [77, (spin_jump | ball_hop) & mole_mario], 
                            [78, (spin_jump | ball_hop) & mole_mario], [79, mole_mario], [80, mini_mario & mole_mario], [81, mini_mario & mole_mario & ball_hop]],
                            
                           [[19, ball_hop & mini_mario], [20, side_drill & ball_hop], [21, side_drill & ball_hop], [22, side_drill & ball_hop],
                            [23, side_drill & ball_hop], [24, side_drill & ball_hop], [25, side_drill & ball_hop], [30, ball_hop],
                            [31, (spin_jump | ball_hop) & mole_mario], [32, mole_mario & side_drill & ball_hop], [33, mole_mario & side_drill & ball_hop], 
                            [34, mole_mario & side_drill & ball_hop], [35, mole_mario & side_drill & ball_hop]],
                            
                           [[2, mole_mario], [3, mini_mario], [4, mole_mario], [5, mini_mario], [6, has_first_dozite], [7, mole_mario], 
                            [9, mini_mario], [11, mini_mario], [12, mini_mario], [13, mini_mario], [14, mini_mario], [15, mini_mario], [16, mini_mario], [17, mini_mario],
                            [19, spin_jump | ball_hop], [20, (mini_mario & side_drill) | ball_hop], [21, (side_drill | ball_hop) & mini_mario],
                            [22, (mini_mario & side_drill) | (hammers & ball_hop)], [23, (mini_mario & side_drill) | (hammers & ball_hop)],
                            [30, has_first_dozite & ball_hop], [31, has_first_dozite], [34, luigi_works], [35, (mini_mario & side_drill) | (hammers & ball_hop)],
                            [36, (mini_mario & side_drill) | (hammers & ball_hop)], [37, (mini_mario & side_drill) | (hammers & ball_hop)],
                            [38, (mini_mario & side_drill) | (hammers & ball_hop)], [39, ball_hop & luigi_works], [40, ball_hop & luigi_works],
                            [41, mole_mario], [42, mole_mario], [43, mole_mario], [44, mole_mario], [45, mole_mario], [46, mole_mario & side_drill],
                            [47, mole_mario & (side_drill | ball_hop)], [48, mole_mario], [49, mole_mario], [50, has_first_dozite & mole_mario & ball_hop]],
                            
                           [[1, mole_mario], [2, mole_mario], [3, mole_mario], [4, mole_mario], [17, mini_mario], [18, mini_mario],
                            [19, mini_mario], [20, mini_mario], [21, mini_mario], [22, mini_mario], [24, mini_mario], [25, ball_hop],
                            [26, mole_mario], [29, mini_mario], [30, ball_hop], [32, luigi_works], [33, luigi_works], [34, luigi_works],
                            [35, luigi_works], [38, luigi_works], [39, luigi_works], [44, mole_mario], [45, mole_mario], [46, mole_mario],
                            [47, mole_mario], [48, mole_mario], [51, mini_mario],
                            [52, mole_mario], [53, mole_mario], [54, mole_mario], [55, mole_mario], [56, mole_mario], [57, mole_mario],
                            [58, mole_mario], [59, mole_mario], [60, mole_mario], [61, mole_mario], [62, mole_mario], [63, mole_mario],
                            [64, mole_mario], [65, mole_mario], [66, mole_mario], [67, mole_mario], [68, mole_mario], [69, mole_mario],
                            [70, mole_mario], [71, mole_mario], [72, mole_mario]],
                            
                           [[1, spin_jump & ball_hop], [2, spin_jump & ball_hop], [4, ball_hop], [5, ball_hop], [6, luigi_works], [7, luigi_works],
                            [8, luigi_works], [9, luigi_works], [10, luigi_works], [11, luigi_works], [12, luigi_works], [13, luigi_works],
                            [14, luigi_works], [15, luigi_works], [16, luigi_works], [17, luigi_works], [18, luigi_works], [19, luigi_works],
                            [20, luigi_works], [21, luigi_works & luigi_stack_pound], [22, luigi_works & luigi_stack_pound],
                            [23, luigi_works & luigi_stack_pound], [24, luigi_works & luigi_stack_pound], [25, side_drill & ball_hop & luigi_works],
                            [26, side_drill & ball_hop & luigi_works], [27, side_drill & ball_hop & luigi_works], [28, side_drill & ball_hop & luigi_works],
                            [31, ball_hop], [32, side_drill & ball_hop], [33, side_drill & ball_hop], [34, side_drill & ball_hop],
                            [35, side_drill & ball_hop], [36, side_drill & ball_hop], [37, ball_hop], [38, ball_hop],
                            [39, mole_mario & ball_hop], [40, mole_mario & ball_hop], [41, mole_mario], [42, mole_mario & side_drill & ball_hop],
                            [43, mole_mario & ball_hop]],
                            
                           [[6, mini_mario], [7, mini_mario], [8, mini_mario], [10, mini_mario], [12, hammers], [13, hammers], [19, spin_jump],
                            [25, mole_mario & luigi_works], [26, mole_mario & luigi_works], [27, mole_mario & luigi_works], [28, mole_mario & luigi_works],
                            [29, mole_mario & luigi_works], [30, mole_mario & luigi_works], [31, mole_mario & luigi_works], [32, mole_mario & luigi_works],
                            [33, mole_mario & luigi_works], [34, mole_mario & luigi_works], [35, mole_mario & luigi_works], [36, mole_mario & luigi_works],
                            [37, mole_mario & luigi_works], [38, mole_mario & luigi_works], [39, mole_mario & luigi_works], [40, mole_mario & luigi_works],
                            [41, mole_mario & luigi_works], [42, mole_mario & luigi_works], [43, mole_mario & luigi_works], [44, mole_mario & luigi_works],
                            [45, mole_mario & luigi_works], [46, mole_mario & luigi_works & luigi_stack_spring],
                            [47, mole_mario & luigi_works & luigi_stack_spring], [48, mole_mario & luigi_works & luigi_stack_spring & luigi_stack_pound],
                            [49, mole_mario & luigi_works & luigi_stack_spring & luigi_stack_pound], [50, hammers], [51, hammers],
                            [52, mole_mario & luigi_works & luigi_stack_spring & luigi_stack_pound], [53, mini_mario | ball_hop],
                            [54, mole_mario], [55, mole_mario], [56, mole_mario], [57, mole_mario], [58, mole_mario]],

                           [],
                           
                           [[1, mini_mario]],
                           
                           [[3, spin_jump], [4, spin_jump | ball_hop], [5, mini_mario], [6, mini_mario], [9, spin_jump], [11, spin_jump], [13, spin_jump | ball_hop],
                            [17, spin_jump], [18, spin_jump | ball_hop], [19, spin_jump], [20, spin_jump], [21, spin_jump], [22, spin_jump], [23, spin_jump],
                            [24, spin_jump], [25, spin_jump], [26, spin_jump & ball_hop], [27, spin_jump & ball_hop], [28, spin_jump], [29, spin_jump],
                            [30, spin_jump & ball_hop], [31, spin_jump & ball_hop], [32, spin_jump | ball_hop], [33, spin_jump | ball_hop],
                            [34, (spin_jump | ball_hop) & luigi_stack_spring & luigi_works], [35, (spin_jump | ball_hop) & luigi_cone_jump & luigi_stack_spring & luigi_works],
                            [36, (spin_jump | ball_hop) & luigi_cone_jump & luigi_stack_spring & luigi_works], [37, (spin_jump | ball_hop) & luigi_cone_jump & luigi_stack_spring & luigi_works],
                            [38, (spin_jump | ball_hop) & luigi_cone_jump & luigi_stack_spring & luigi_works], [39, (spin_jump | ball_hop) & luigi_cone_jump & luigi_stack_spring & luigi_works],
                            [40, spin_jump | ball_hop], [41, spin_jump | ball_hop], [42, spin_jump | ball_hop],
                            [45, mole_mario & spin_jump], [46, mole_mario & spin_jump], [47, mole_mario & side_drill], [48, mole_mario & side_drill],
                            [49, mole_mario & spin_jump], [50, (spin_jump | ball_hop) & mole_mario], [51, mole_mario & spin_jump], [52, mole_mario & spin_jump],
                            [53, mole_mario & spin_jump], [54, mole_mario & spin_jump], [55, mole_mario & spin_jump], [56, mole_mario & spin_jump & ball_hop]],
                            
                           [[4, luigi_works & luigi_cone_jump], [11, ball_hop], [12, ball_hop], [17, ball_hop], [18, ball_hop], [19, ball_hop], [20, ball_hop],
                            [21, ball_hop], [23, ball_hop & luigi_works], [24, ball_hop & luigi_works],
                            [25, mole_mario], [26, mole_mario], [27, mole_mario], [28, mole_mario], [29, mole_mario & ball_hop], [30, mole_mario],
                            [31, mole_mario], [32, mole_mario & ball_hop], [33, mole_mario & ball_hop]],
                            
                           [[3, luigi_works & luigi_cone_jump], [4, luigi_works & luigi_cone_jump],
                            [7, mole_mario & ball_hop & luigi_works & luigi_cone_jump], [8, mole_mario & spin_jump & luigi_works & luigi_cone_jump], 
                            [9, mole_mario & spin_jump & luigi_works & luigi_cone_jump]],

                           [],
                           
                           [[1, side_drill | ball_hop], [2, side_drill], [8, mini_mario], [11, mini_mario & ball_hop], [12, side_drill], [13, side_drill], [14, side_drill],
                            [16, side_drill], [20, luigi_works], [21, luigi_works], [22, side_drill & luigi_works & luigi_cone_jump],
                            [23, side_drill], [24, side_drill], [25, side_drill], [26, side_drill], [27, side_drill], [28, mini_mario & spin_jump & ball_hop],
                            [29, mini_mario & mole_mario], [30, mini_mario & mole_mario], [31, side_drill & mole_mario], [32, side_drill & mole_mario],
                            [33, mole_mario], [34, mole_mario]],
                            
                           [[8, has_two_eggs], [9, has_two_eggs], [10, has_two_eggs], [11, has_two_eggs], [12, has_two_eggs & luigi_cone_jump],
                            [13, has_two_eggs & luigi_cone_jump], [14, has_two_eggs & luigi_cone_jump], [15, has_two_eggs & luigi_cone_jump],
                            [16, has_two_eggs & luigi_cone_jump], [17, has_two_eggs & luigi_cone_jump], [18, has_two_eggs & luigi_cone_jump],
                            [19, has_two_eggs & luigi_cone_jump], [20, has_all_eggs & luigi_stack_spring & luigi_stack_pound & luigi_cone_jump],
                            [21, has_all_eggs & luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [25, has_two_eggs],
                            [26, has_all_eggs & luigi_cone_jump], [27, has_two_eggs], [28, has_two_eggs]],
                            
                           [[7, spin_jump], [8, spin_jump], [9, spin_jump], [10, side_drill], [11, side_drill], [12, side_drill], [13, side_drill], [14, side_drill],
                            [15, spin_jump], [16, spin_jump], [17, spin_jump], [18, side_drill & luigi_works], [19, spin_jump], [20, spin_jump],
                            [21, mole_mario], [22, mole_mario], [23, spin_jump & mole_mario], [24, side_drill & mole_mario]],
                            
                           [[9, mole_mario], [10, mole_mario], [14, mole_mario], [15, mole_mario], [16, mini_mario & mole_mario], [17, mini_mario & mole_mario], [18, mole_mario],
                            [29, mole_mario], [30, mole_mario], [31, mole_mario], [32, mole_mario], [33, mole_mario], [34, mole_mario], [35, mole_mario],
                            [36, mole_mario], [37, mole_mario], [38, mole_mario], [39, mole_mario], [40, mole_mario], [41, mole_mario], [42, mole_mario], [43, mole_mario]],
                            
                           [[1, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [17, luigi_stack_spring & luigi_stack_pound], [20, luigi_stack_spring & luigi_stack_pound],
                            [22, luigi_stack_spring & luigi_stack_pound], [24, luigi_stack_spring & luigi_stack_pound], [25, luigi_stack_spring & luigi_cone_jump],
                            [26, luigi_stack_spring & luigi_stack_pound], [28, luigi_stack_spring & luigi_stack_pound], [29, luigi_stack_spring & luigi_stack_pound],
                            [30, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [31, luigi_stack_spring & luigi_stack_pound],
                            [32, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [33, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump],
                            [34, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [35, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump],
                            [36, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [37, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump],
                            [38, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [39, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump],
                            [40, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [41, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump],
                            [42, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump], [43, luigi_stack_spring & luigi_stack_pound & luigi_cone_jump]],
                            
                           [[1, spin_jump], [2, spin_jump], [5, spin_jump], [8, spin_jump], [11, mini_mario], [12, mini_mario], [13, mini_mario], [14, mini_mario],
                            [20, hammers], [24, hammers], [25, luigi_works & hammers & spin_jump], [26, luigi_works & hammers & spin_jump], [27, luigi_works & hammers & spin_jump],
                            [28, luigi_works & hammers & spin_jump], [29, luigi_works & hammers & spin_jump], [30, luigi_works & hammers & spin_jump], [31, luigi_works & hammers & spin_jump],
                            [32, luigi_works & hammers & spin_jump], [33, luigi_works & hammers & spin_jump], [34, luigi_works & hammers & spin_jump], [35, luigi_works & hammers & spin_jump],
                            [36, luigi_works & hammers & spin_jump], [37, luigi_works & hammers & spin_jump], [38, luigi_works & hammers & spin_jump], [39, luigi_works & hammers & spin_jump],
                            [40, luigi_works & hammers & spin_jump], [41, luigi_works & hammers & spin_jump], [42, luigi_works & hammers & spin_jump], [43, luigi_works & hammers & spin_jump],
                            [44, mole_mario], [45, mole_mario], [46, mole_mario]],
                            
                           [[15, hammers], [16, hammers], [18, hammers], [19, hammers], [20, hammers], [30, hammers, luigi_works], [31, hammers, luigi_works],
                            [32, hammers, luigi_works], [33, hammers, luigi_works], [34, hammers, luigi_works], [35, hammers, luigi_works], [36, hammers, luigi_works],
                            [37, hammers, luigi_works], [38, hammers, luigi_works],
                            [39, mole_mario], [40, mole_mario], [41, mole_mario], [42, mole_mario], [43, mole_mario], [44, mole_mario]],
                            
                           [[7, mini_mario], [8, mini_mario],
                            [16, mole_mario], [17, mole_mario], [18, mole_mario], [19, mole_mario], [20, mole_mario], [21, mole_mario], [22, mole_mario],
                            [23, mole_mario], [24, mole_mario]],
                            
                           []]
    
    #Updates certain indexes in the location info if reduce mini mario requirements is turned on
    if world.options.reduce_mini:
        del location_logic_info[4][46]
        location_logic_info[4][61] = [80, mole_mario]
        location_logic_info[4][62] = [81, mole_mario & ball_hop]
        del location_logic_info[6][7]
        del location_logic_info[6][7]
        del location_logic_info[6][7]
        location_logic_info[6][13] = [22, hammers & (ball_hop | side_drill)]
        location_logic_info[6][14] = [23, hammers & (ball_hop | side_drill)]
        location_logic_info[6][19] = [35, hammers & (ball_hop | side_drill)]
        location_logic_info[6][20] = [36, hammers & (ball_hop | side_drill)]
        location_logic_info[6][21] = [37, hammers & (ball_hop | side_drill)]
        location_logic_info[6][22] = [38, hammers & (ball_hop | side_drill)]
        location_logic_info[6][30] = [46, mole_mario & side_drill]
        location_logic_info[6][31] = [47, mole_mario & (ball_hop | side_drill)]
    
    #Sets the logic to the locations
    for r in range(len(location_logic_info)):
        for e in location_logic_info[r]:
            #print(list(world.location_name_to_id.values()))
            location_name = list(world.location_name_to_id.keys())[list(world.location_name_to_id.values()).index(e[0] + (r*100))] #Gets the location name from the ID
            current_location = world.get_location(location_name)
            world.set_rule(current_location, e[1])

    # In "set_all_entrance_rules", we had a rule for a location that doesn't always exist.
    # In this case, we had to check for its existence (by checking the player's chosen options) before setting the rule.
    # Other times, you may have a situation where a location can have two different rules depending on the options.
    # In our case, the enemy in the right room has more health if hard mode is selected,
    # so ontop of the Sword, the player will either need one more health or a Shield in hard mode.
    # First, let's make our sword condition.
    #can_defeat_basic_enemy: Rule = Has("Sword")

    # Next, we'll check whether hard mode has been chosen in the player options.
    #if world.options.hard_mode:
        # We'll make the condition for "Has a Shield or a Health Upgrade".
        # We can chain two "Has" conditions together with the | operator to make "Has Shield or has Health Upgrade".
    #    can_withstand_a_hit = Has("Shield") | Has("Health Upgrade")

        # Now, we chain this rule to our Sword rule.
        # Since we want both conditions to be true, in this case, we have to chain them in an "and" way.
        # For this, we can use the & operator.
    #    can_defeat_basic_enemy = can_defeat_basic_enemy & can_withstand_a_hit

    # Finally, we set our rule onto the Right Room Enemy Drop location.
    #right_room_enemy = world.get_location("Right Room Enemy Drop")
    #world.set_rule(right_room_enemy, can_defeat_basic_enemy)

    # For the final boss, we also need to chain multiple conditions.
    # First of all, you always need a Sword and a Shield.
    # So far, we used the | and & operators to chain "Has" rules.
    # Instead, we can also use HasAny for an or-chain of items, or HasAll for an and-chain of items.
    #has_sword_and_shield: Rule = HasAll("Sword", "Shield")

    # In hard mode, the player also needs both Health Upgrades to survive long enough to defeat the boss.
    # For this, we can use the optional "count" parameter for "Has".
    #has_both_health_upgrades = Has("Health Upgrade", count=2)

    # Previously, we used an "if world.options.hard_mode" condition to check if we should apply the extra requirement.
    # However, if you're comfortable with boolean logic, there is another way.
    # OptionFilter is a rule component which isn't a "Rule" on its own, but when used in a boolean expression with
    # rules, it acts like True if the option has the specified value, and acts like False otherwise.
    #hard_mode_is_off = OptionFilter(HardMode, False)

    # So with this option-checking rule component in hand, we can write our boss condition like this:
    #can_defeat_final_boss = has_sword_and_shield & (hard_mode_is_off | has_both_health_upgrades)
    # If you're not as comfortable with boolean logic, it might be somewhat confusing why this is correct.
    # There is nothing wrong with using "if" conditions to check for options, if you find that easier to understand.

    # Finally, we apply the rule to our "Final Boss Defeated" event location.
    #final_boss = world.get_location("Final Boss Defeated")
    #world.set_rule(final_boss, can_defeat_final_boss)


def set_completion_condition(world: MLDTWorld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # For this, we can use world.set_completion_rule.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.set_completion_rule(HasAll("Sword", "Shield"))

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.set_completion_rule(Has("Victory"))


# One final comment about rules:
# If your world exclusively uses Rule Builder rules (like APQuest), it's worth trying CachedRuleBuilderWorld.
# CachedRuleBuilderWorld is a subclass of World that has a bunch of caching magic to make rules faster.
# Just have your world class subclass CachedRuleBuilderWorld instead of World:
#   class APQuestWorld(CachedRuleBuilderWorld): ...
# This may speed up your world, or it may make it slower.
# The exact factors are complex and not well understood, but there is no harm in trying it.
# Generate a few seeds and see if there is a noticeable difference!
# If you're wondering, author has checked: APQuest is too simple to see any benefits, so we'll stick with "World".
