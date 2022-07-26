#
# For setting up your SM64DS hack.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
import Lib.xdelta as xdelta
import fileManager as fs
from io import SEEK_END, SEEK_SET
import nuke
import os
import shutil
import struct

# Remove old hack.
def check_remove_old_hack():
    if os.path.exists(ht_common.get_rom_name()) or os.path.exists("Base"):
        print("WARNING: It looks like you already have a hack in progress!")
        if ht_common.user_warn():
            nuke.nuke_base()
            nuke.nuke_hack()
            if os.path.exists("Base.nds"):
                os.remove("Base.nds")
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
    if name == "" or "." in name or " " in name or "/" in name or "\\" in name or not ht_common.user_yn_prompt("Is this name ok (" + name + ")?"):
        set_rom_name()
        return
    file = open("romName.txt", "w")
    file.write(name)
    file.close()

# Make default patch.
def make_patch_default():
    if not os.path.exists(ht_common.get_rom_name()):
        os.mkdir(ht_common.get_rom_name())

# Extract a ROM to use for the patch instead. TODO: MAKE THIS WORK AND DELETE CODE HACKS, BAD OVERLAYS, IGNORE IRRELEVANT/DUPLICATE FILES, AND REMOVE DL REFERENCES!
def make_patch(rom_path):
    rom_name = ht_common.get_rom_name()
    extract_rom(rom_path, os.path.join("InstallFiles", "TmpHack"), rom_name)
    shutil.rmtree(os.path.join("InstallFiles", "TmpHack"))

    # Get new overlay list for adjusting addresses later.
    new_ovs = fs.fs_get_overlays()

    # Unfortunately, anything code, header, or file related must be removed. This will probably break some things with your ROM.
    os.remove(os.path.join(rom_name, "__ROM__", "arm7.bin"))
    os.remove(os.path.join(rom_name, "__ROM__", "arm9.bin"))
    os.remove(os.path.join(rom_name, "__ROM__", "arm7Overlays.json"))
    os.remove(os.path.join(rom_name, "__ROM__", "arm9Overlays.json"))
    os.remove(os.path.join(rom_name, "__ROM__", "files.txt"))
    os.remove(os.path.join(rom_name, "__ROM__", "header.json"))
    shutil.rmtree(os.path.join(rom_name, "ARCHIVE"))
    for i in range(0, 103):
        os.remove(os.path.join(rom_name, "__ROM__", "Arm9", str(i) + ".bin"))

    # Next step is to adjust pointers in level overlays.
    old_ovs = fs.fs_get_overlays()
    for i in range(103, 155):
        if os.path.exists(os.path.join(rom_name, "__ROM__", "Arm9", str(i) + ".bin")):

            # Get overlay data and write header.
            old_ov = open(os.path.join("Base", "__ROM__", "Arm9", str(i) + ".bin"), "rb")
            new_ov = open(os.path.join(rom_name, "__ROM__", "Arm9", str(i) + ".bin"), "rb")
            new_ov_dat = new_ov.read()
            new_ov.close()
            new_ov = open(os.path.join(rom_name, "__ROM__", "Arm9", str(i) + ".bin"), "wb")
            new_ov.seek(0, SEEK_SET)
            new_ov.write(old_ov.read(0x54)) # Write header.

            # Get file ids.
            old_ov.seek(0x68, SEEK_SET)
            file_ids = old_ov.read(0x8)
            old_ov.close()

            # Fetch addresses to adjust offsets.
            old_ovd = fs.fs_get_overlay_from_id(old_ovs, i)
            old_load_addr = int(old_ovd["RAMAddress"][2:], 16)
            new_ovd = fs.fs_get_overlay_from_id(new_ovs, i)
            new_min_addr = int(new_ovd["RAMAddress"][2:], 16)
            new_max_addr = new_min_addr + int(new_ovd["RAMSize"][2:], 16)

            # Write overlay data.
            for j in range(0x54, len(new_ov_dat), 4):
                dat = struct.unpack_from("<I", new_ov_dat, j)[0]
                if j == 0x68:
                    new_ov.write(file_ids) # OV0 IDs.
                elif j == 0x6C:
                    pass # Already taken care of above.
                elif dat >= new_min_addr and dat < new_max_addr:
                    new_ov.write(struct.pack("<I", dat - new_min_addr + old_load_addr)) # Adjust pointer.
                else:
                    new_ov.write(struct.pack("<I", dat)) # No change.

            # Adjust DL data.
            while new_ov.tell() % 4 != 0:
                new_ov.write(bytearray(1))
            dls_off = new_ov.tell()
            new_ov.seek(0x7F, SEEK_SET)
            new_ov.write(bytearray([new_ov_dat[0x7F] | 0x10]))
            new_ov.seek(0x30, SEEK_SET)
            new_ov.write(struct.pack("<I", dls_off))
            new_ov.seek(0, SEEK_END)
            new_ov.write(struct.pack("<I", 0))
            new_ov.close()

    # Now remove identical files.
    for (dirpath, dirnames, filenames) in os.walk(rom_name):
        for file in filenames:
            old_path = os.path.join(dirpath.replace(rom_name, "Base"), file)
            new_path = os.path.join(os.path.join(dirpath, file))
            if os.path.exists(old_path):
                if ht_common.sha256sum(old_path) == ht_common.sha256sum(new_path):
                    os.remove(new_path)

    # Remove anything not needed.
    ht_common.remove_empty_dirs(rom_name)

# Setup the ROM settings file.
def make_romsettings():
    ht_common.call_program("cmd.exe /C cd", "")
    base_path = ht_common.get_tmp_data("r").strip()
    rom_name = ht_common.get_rom_name()
    lines = []
    lines.append(base_path + "\\Base" + "\n")
    lines.append(base_path + "\\" + rom_name + "\n")
    lines.append(base_path + "\\Conversions" + "\n")
    lines.append(base_path + "\\" + rom_name + ".nds" + "\n")
    romsettings = open(ht_common.get_rom_name() + ".romsettings", "w")
    romsettings.writelines(lines)
    romsettings.close()
    pass

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
        if check_remove_old_hack():
            make_base_rom()
            hack_nds = ht_common.user_prompt("NDS file of hack to import data from")
            if not os.path.exists(hack_nds):
                print("ERR: Given NDS path for hack doesn't exist!")
                exit(0)
            extract_base()
            set_rom_name()
            make_patch(hack_nds)
            make_romsettings()
            print("Hack has been successfully setup!\nOpen " + ht_common.get_rom_name() + ".romsettings with SM64DSe in the editor folder to get started!")
    elif opt == 3:
        if check_remove_old_hack():
            extract_base()
            set_rom_name()
            make_patch_default()
            make_romsettings()
            print("Hack has been successfully setup!\nOpen " + ht_common.get_rom_name() + ".romsettings with SM64DSe in the editor folder to get started!")
    elif opt == 4:
        if check_remove_old_hack():
            hack_nds = ht_common.user_prompt("NDS file of hack to import data from")
            if not os.path.exists(hack_nds):
                print("ERR: Given NDS path for hack doesn't exist!")
                exit(0)
            extract_base()
            set_rom_name()
            make_patch(hack_nds)
            make_romsettings()
            print("Hack has been successfully setup!\nOpen " + ht_common.get_rom_name() + ".romsettings with SM64DSe in the editor folder to get started!")