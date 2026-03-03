Welcome to the Mario and Luigi Dream Team randomizer, Pi'illomizer!

How to install:
1) Install poetry using python in the terminal: "python3 -m pip install poetry"
2) Install project dependencies in terminal: "python3 -m poetry install"
3) Run the program: "python3 -m poetry run python3 -m mldtr"

How to use:
1) Click "Open Dump", then locate to your extracted game data (note: it must have a RomFS AND an ExeFS)
2) Select whatever settings you want
3) Randomize to your heart's content

How to get RomFS and ExeFS:
1) Hold START while booting your modded 3DS to boot into GodMode9
2) Navigate to your region's title ID, in either SYSNAND SD (SD Card) or SYSNAND CTRNAND (Game card)
3) Enter the directory, then select either the .app (digital) or .3ds (cartridge) with the biggest filesize
4) Press A on it, select "NCCH Image Options", then "Extract .code". This will extract it to gm9/out
5) Move (titleid).code to your computer in the same directory as your romfs called "exefs", and rename it to code.bin
6) Enjoy!