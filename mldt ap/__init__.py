# The first thing you should make for your world is an archipelago.json manifest file.
# You can reference APQuest's, but you should change the "game" field (obviously),
# and you should also change the "minimum_ap_version" - probably to the current value of Utils.__version__.

# Apart from the regular apworld code that allows generating multiworld seeds with your game,
# your apworld might have other "components" that should be launchable from the Archipelago Launcher.
# You can ignore this for now. If you are specifically interested in components, you can read components.py.
#from . import components as components

# The main thing we do in our __init__.py is importing our world class from our world.py to initialize it.
# Obviously, this world class needs to exist first. For this, read world.py.
from .world import MLDTWorld as MLDTWorld
from worlds.LauncherComponents import Component, Type, components, launch_subprocess, icon_paths


if Component is not None and Type is not None:
    def launch_client(*args):
        from .launcher import launch
        launch_subprocess(launch, name="MLDTClient", args=args)


    if icon_paths is not None:
        icon_paths["mldticon"] = f"ap:{__name__}/data/mldticon.png"


    components.append(
        Component(
            "Mario & Luigi Dream Team Client",
            func=launch_client,
            component_type=Type.CLIENT,
            description="Secondary client for Mario & Luigi Dream team.",
            icon="mldticon"
        )
    )