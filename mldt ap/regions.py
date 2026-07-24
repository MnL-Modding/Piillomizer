from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

if TYPE_CHECKING:
    from .world import APQuestWorld

# A region is a container for locations ("checks"), which connects to other regions via "Entrance" objects.
# Many games will model their Regions after physical in-game places, but you can also have more abstract regions.
# For a location to be in logic, its containing region must be reachable.
# The Entrances connecting regions can have rules - more on that in rules.py.
# This makes regions especially useful for traversal logic ("Can the player reach this part of the map?")

# Every location must be inside a region, and you must have at least one region.
# This is why we create regions first, and then later we create the locations (in locations.py).


def create_and_connect_regions(world: MLDTWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: MLDTWorld) -> None:
    # Creating a region is as simple as calling the constructor of the Region class.
    blimport = Region("Blimport", world.player, world.multiworld)
    piillo_castle = Region("Pi'illo Castle", world.player, world.multiworld)
    piillo_castle_deep = Region("Pi'illo Castle Dream's Deep", world.player, world.multiworld)
    blimport_underground = Region("Under Blimport Bridge", world.player, world.multiworld)
    mushrise_park = Region("Mushrise Park Main Area", world.player, world.multiworld)
    mushrise_hammer = Region("Mushrise Park Hammer Regions", world.player, world.multiworld)
    past_gate = Region("Dozing Sands/Driftwood Shore Outskirts", world.player, world.multiworld)
    dozing_tracks = Region("Dozing Sands Track Area", world.player, world.multiworld)
    dozing_dreampoints = Region("Dozing Sands Dreamstone Area", world.player, world.multiworld)
    wakeport = Region("Wakeport", world.player, world.multiworld)
    wakeport_ultibed = Region("Wakeport Ultibed", world.player, world.multiworld)
    mount_pajamaja_entrance = Region("Mount Pajamaja Before Base", world.player, world.multiworld)
    mount_pajamaja_base = Region("Mount Pajamaja Base", world.player, world.multiworld)
    mount_pajamaja_middle = Region("Mount Pajamaja Middle", world.player, world.multiworld)
    mount_pajamaja_peak = Region("Mount Pajamaja Peak", world.player, world.multiworld)
    mount_pajamaja_dreampoint = Region("Mount Pajamaja Summit Dreampoint", world.player, world.multiworld)
    driftwood_shore = Region("Driftwood Shore Dreampoint Area", world.player, world.multiworld)
    driftwood_shore_egg = Region("Driftwood Shore Dream Egg Dream", world.player, world.multiworld)
    somnom_woods = Region("Somnom Woods Before Tracks", world.player, world.multiworld)
    somnom_woods_tracks = Region("Somnom Woods Track Area", world.player, world.multiworld)
    somnom_woods_post_tracks = Region("Somnom Woods After Tracks", world.player, world.multiworld)
    neo_castle = Region("Neo Bowser Castle Before First Progressive Spin", world.player, world.multiworld)
    neo_castle_spin = Region("Neo Bowser Castle After First Porgressive Spin", world.player, world.multiworld)
    neo_castle_flame = Region("Neo Bowser Castle Flame Pipe Area", world.player, world.multiworld)
    neo_castle_dream = Region("Neo Bowser Castle Bowser's Dream", world.player, world.multiworld)

    # Let's put all these regions in a list.
    regions = [blimport, piillo_castle, piillo_castle_deep, blimport_underground, mushrise_park,
               mushrise_hammer, past_gate, dozing_tracks, dozing_dreampoints, wakeport,
               wakeport_ultibed, mount_pajamaja_entrance, mount_pajamaja_base,
               mount_pajamaja_middle, mount_pajamaja_peak, mount_pajamaja_dreampoint,
               driftwood_shore, driftwood_shore_egg, somnom_woods, somnom_woods_tracks, somnom_woods_post_tracks,
               neo_castle, neo_castle_spin, neo_castle_flame, neo_castle_dream]

    # Some regions may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.

    # We now need to add these regions to multiworld.regions so that AP knows about their existence.
    world.multiworld.regions += regions


def connect_regions(world: MLDTWorld) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).
    blimport = world.get_region("Blimport")
    piillo_castle = world.get_region("Pi'illo Castle")
    piillo_castle_deep = world.get_region("Pi'illo Castle Dream's Deep")
    blimport_underground = world.get_region("Under Blimport Bridge")
    mushrise_park = world.get_region("Mushrise Park Main Area")
    mushrise_hammer = world.get_region("Mushrise Park Hammer Regions")
    past_gate = world.get_region("Dozing Sands/Driftwood Shore Outskirts")
    dozing_tracks = world.get_region("Dozing Sands Track Area")
    dozing_dreampoints = world.get_region("Dozing Sands Dreamstone Area")
    wakeport = world.get_region("Wakeport")
    wakeport_ultibed = world.get_region("Wakeport Ultibed")
    mount_pajamaja_entrance = world.get_region("Mount Pajamaja Before Base")
    mount_pajamaja_base = world.get_region("Mount Pajamaja Base")
    mount_pajamaja_middle = world.get_region("Mount Pajamaja Middle")
    mount_pajamaja_peak = world.get_region("Mount Pajamaja Peak")
    mount_pajamaja_dreampoint = world.get_region("Mount Pajamaja Summit Dreampoint")
    driftwood_shore = world.get_region("Driftwood Shore Dreampoint Area")
    driftwood_shore_egg = world.get_region("Driftwood Shore Dream Egg Dream")
    somnom_woods = world.get_region("Somnom Woods Before Tracks")
    somnom_woods_tracks = world.get_region("Somnom Woods Track Area")
    somnom_woods_post_tracks = world.get_region("Somnom Woods After Tracks")
    neo_castle = world.get_region("Neo Bowser Castle Before First Progressive Spin")
    neo_castle_spin = world.get_region("Neo Bowser Castle After First Porgressive Spin")
    neo_castle_flame = world.get_region("Neo Bowser Castle Flame Pipe Area")
    neo_castle_dream = world.get_region("Neo Bowser Castle Bowser's Dream")

    # Okay, now we can get connecting. For this, we need to create Entrances.
    # Entrances are inherently one-way, but crucially, AP assumes you can always return to the origin region.
    # One way to create an Entrance is by calling the Entrance constructor.

    # An even easier way is to use the region.connect helper.

    blimport.connect(piillo_castle, "Blimport to Pi'illo Castle")
    blimport.connect(blimport_underground, "Blimport to Blimport Underground")
    blimport.connect(mushrise_park, "Blimport to Mushrise Park")
    blimport.connect(mount_pajamaja_entrance, "Blimport to Mount Pajamaja")
    piillo_castle.connect(piillo_castle_deep, "Pi'illo Castle to Pi'illo Castle Dream's Deep")
    mushrise_park.connect(mushrise_hammer, "Mushrise Park to Hammer Area")
    mushrise_park.connect(past_gate, "Mushrise Park to Dozing/Driftwood Outskirts")
    mushrise_park.connect(wakeport, "Mushrise Park to Wakeport")
    mushrise_park.connect(somnom_woods, "Mushrise Park to Somnom Woods")
    mushrise_park.connect(neo_castle, "Mushrise Park to Neo Bowser Castle")
    past_gate.connect(dozing_tracks, "Dozing/Driftwood Outskirts to Dozing Track Area")
    past_gate.connect(dozing_dreampoints, "Dozing/Driftwood Outskirts to Dozing Ultibed")
    past_gate.connect(driftwood_shore, "Dozing/Driftwood Outskirts to Driftwood Dreampoints")
    wakeport.connect(wakeport_ultibed, "Wakeport to Wakeport Ultibed")
    mount_pajamaja_entrance.connect(mount_pajamaja_base, "Mount Pajamaja Entrance to Mount Pajamaja Base")
    mount_pajamaja_entrance.connect(mount_pajamaja_peak, "Mount Pajamaja Entrance to Mount Pajamaja Peak")
    mount_pajamaja_base.connect(mount_pajamaja_middle, "Mount Pajamaja Base to Mount Pajamaja Middle")
    mount_pajamaja_middle.connect(mount_pajamaja_peak, "Mount Pajamaja Middle to Mount Pajamaja Peak")
    mount_pajamaja_peak.connect(mount_pajamaja_dreampoint, "Mount Pajamaja Peak to Mount Pajamaja Summit Dream")
    driftwood_shore.connect(driftwood_shore_egg, "Driftwood Shore Dreampoints to Driftwood Shore Eggs")
    somnom_woods.connect(somnom_woods_tracks, "Somnom Woods Entrance to Somnom Woods Tracks")
    somnom_woods_tracks.connect(somnom_woods_post_tracks, "Somnom Woods Tracks to Somnom Woods After Tracks")
    neo_castle.connect(neo_castle_spin, "Neo Bowser Castle Entrance to Neo Bowser Castle Spin")
    neo_castle_spin.connect(neo_castle_flame, "Neo Bowser Castle Spin to Neo Bowser Castle Flames")
    neo_castle_flame.connect(neo_castle_dream, "Neo Bowser Castle Flames to Neo Bowser Castle Dream")

    # Some Entrances may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    # In this case, we previously created an extra "Top Middle Room" region that we now need to connect to Overworld.
