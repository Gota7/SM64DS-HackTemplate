#
# For setting up your SM64DS hack.
#   2022 Gota7.
#

from asyncio import subprocess
import Lib.ht_common as ht_common
import Lib.xdelta as xdelta
import nuke
import os
import shutil

# Remove old hack.
def check_remove_old_hack():
    if os.path.exists(ht_common.get_rom_name()) or os.path.exists("Base"):
        print("WARNING: It looks like you already have a hack in progress!")
        if ht_common.user_warn():
            nuke.nuke_base()
            nuke.nuke_hack()
            return True
        return False
    return True

# Create the base ROM from a EUR ROM (all it does is apply the SM64DSe patches).
def make_base_rom():
    if not os.path.exists("EUR.nds"):
        print("ERR: EUR.nds is not found and is needed to make the vanilla base ROM!")
        exit(0)
    xdelta.xdelta_apply_patch("EUR.nds", os.path.join("InstallFiles", "makeBase.xdelta"), "Base.nds")
    if "XD3_INVALID_INPUT" in ht_common.get_tmp2_data("r"):
        print("ERR: EUR.nds has the incorrect checksum (are you sure it hasn't been modified?)")
        exit(0)

# Extract a ROM.
def extract_rom(rom_path, conversion_folder, out_path):
    ht_common.run_ndst("-e " + os.path.join("..", rom_path) + " " + os.path.join("..", conversion_folder) + " " + os.path.join("..", out_path))

# Extract a base ROM.
def extract_base():
    if os.path.exists("Base"):
        print("WARNING: Base ROM folder already exists!")
        if not ht_common.user_warn():
            return
        nuke.nuke_base()
    print("Extracting base ROM...")
    extract_rom("Base.nds", "Conversions", "Base")
    print("Base ROM extracted.")

# Set the ROM name.
def set_rom_name():
    print("Enter the name for your hack (no spaces or .nds): ", end="")
    name = input()
    if "." in name or " " in name or not ht_common.user_yn_prompt("Is this name ok (" + name + ")?"):
        set_rom_name()
    file = open("romName.txt", "w")
    file.write(name)
    file.close()

# Make default patch.
def make_patch_default():
    if not os.path.exists(ht_common.get_rom_name()):
        os.mkdir(ht_common.get_rom_name())

# Extract a ROM to use for the patch instead. TODO: MAKE THIS WORK AND DELETE CODE HACKS, BAD OVERLAYS, IGNORE IRRELEVANT/DUPLICATE FILES, AND REMOVE DL REFERENCES!
def make_patch(rom_path):
    pass

# Setup the ROM settings file.
def make_romsettings():
    ht_common.call_program("cd", "", True)
    base_path = ht_common.get_tmp_data("r").strip()
    rom_name = ht_common.get_rom_name()
    lines = []
    lines.append(base_path + "\\Base" + "\n")
    lines.append(base_path + "\\" + rom_name + "\n")
    lines.append(base_path + "\\Conversion" + "\n")
    lines.append(base_path + "\\" + rom_name + ".nds" + "\n")
    romsettings = open(ht_common.get_rom_name() + ".romsettings", "w")
    romsettings.writelines(lines)
    romsettings.close
    pass

import subprocess
# Main method.
if __name__ == "__main__":
    print("SM64DS Hack Template Setup:")
    print("  2022 Gota7")
    opt = ht_common.user_options_prompt("Setup Options:", [ "Use vanilla ROM as base and begin new hack.", "Use vanilla ROM as base and copy data from another hack.", "Use custom ROM as base and begin new hack (not recommended).", "Use custom ROM as base and copy data from another hack (strongly not recommended).", "Exit." ])
    if opt == 1:
        if check_remove_old_hack():
            make_base_rom()
            extract_base()
            set_rom_name()
            make_patch_default()
            make_romsettings()
            print("Hack has been successfully setup!\nOpen " + ht_common.get_rom_name() + ".romsettings with SM64DSe in the editor folder to get started!")
    elif opt == 2:
        print("ERR: Option not currently supported! Sorry!")
    elif opt == 3:
        print("ERR: Option not currently supported! Sorry!")
    elif opt == 4:
        print("ERR: Option not currently supported! Sorry!")