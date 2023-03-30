#
# Build the ROM, ASM hacks, overlays, etc.
#   2022 Gota7.
#
import argparse

import Lib.ht_common as ht_common
import Lib.compiler as cc
from Lib.xdelta import xdelta_make_patch
import fileManager as fs
import nuke
import os
import shutil
from sys import stderr, stdout
import sys
from time import sleep
import zipfile

# Build ROM.
from utils import load_libraries_definition


def build_rom():
    rom_name = ht_common.get_rom_name()
    if not os.path.exists("Base") or not os.path.exists("Conversions") or not os.path.exists(rom_name):
        print("ERR: Base ROM and hack folders are not present! Did you run \"setup.py\" first?")
        exit(0)
    fs.fs_apply_command_list(fs.fs_read_command_list())
    # Linux hack - use Ndst-Lin.
    if sys.platform == "linux" or sys.platform == "linux2":
        ht_common.run_ndst("-n " + os.path.join("..", "Base") + " " + os.path.join("..", ht_common.get_rom_name()) + " " + os.path.join("..", "Conversions") + " " + os.path.join("..", ht_common.get_rom_name()) + ".nds")
        curr_dir = os.getcwd()
        os.chdir("Editor")
        ninja_file = open("build.ninja", "r")
        ninja_data = ninja_file.read()
        ninja_file.close()
        ninja_data = ninja_data.replace("./Ndst ", "./Ndst-Lin.elf ")
        ninja_file = open("build.ninja", "w")
        ninja_file.write(ninja_data)
        ninja_file.close()
        os.chdir(curr_dir)
        ht_common.call_program_nowine("ninja", "Editor", stdout, stderr)
    else:
        ht_common.run_ndst("-n " + ht_common.get_abs_dir("Base") + " " + ht_common.get_abs_dir(rom_name) + " " + ht_common.get_abs_dir("Conversions") + " " + os.path.join("..", ht_common.get_rom_name()) + ".nds")
        ht_common.call_program("ninja.exe", "Editor", stdout, stderr)
    print("Build: ROM built.")
    if ht_common.get_rom_autostart():
        print("Build: Opening ROM...")
        if sys.platform == "linux" or sys.platform == "linux2":
            ht_common.call_program_nowine("xdg-open " + rom_name + ".nds")
        else:
            os.startfile(rom_name + ".nds")

# Build xdelta.
def build_xdelta():
    if not os.path.exists("EUR.nds"):
        print("ERR: Original EUR baserom not found!")
        exit(0)
    rom_name = ht_common.get_rom_name()
    xdelta_make_patch("EUR.nds", rom_name + ".nds", rom_name + ".xdelta")

# Ship file.
def build_ship():
    build_xdelta()
    rom_name = ht_common.get_rom_name()
    zip = zipfile.ZipFile(rom_name + ".zip", "w", zipfile.ZIP_DEFLATED, False)
    zip.writestr("README.txt", "Instructions:\n1. Open xdeltaUI.exe\n2. For \"Patch\", select " + rom_name + ".xdelta.\n3. For \"Source File\", select an unmodified/unopened with SM64DSe EUR ROM (MD5SUM: 867b3d17ad268e10357c9754a77147e5).\n4. Select what you want for the \"Output File\" (.nds).\n5. Hit Patch!\n\nAlternatively, you can run \"xdelta.exe -d -s EUR.nds" + " " + rom_name + ".xdelta " + rom_name + ".nds\".")
    zip.write(os.path.join("InstallFiles", "xdelta.exe"), "xdelta.exe")
    zip.write(os.path.join("InstallFiles", "xdeltaUI.exe"), "xdeltaUI.exe")
    zip.write(rom_name + ".xdelta", rom_name + ".xdelta")
    print("Build: Built " + rom_name + ".xdelta and " + rom_name + ".zip.\nSend the ZIP file out to whoever you want to have play!")

# Setup fireflower build.
def setup_fireflower_for_building():
    if not os.path.exists("Base.nds"):
        print("ERR: Base.nds is not found! Did you run \"setup.py\"?")
        exit(0)
    path = os.path.join("ASM", "fireflower_data")
    if not os.path.exists(path):
        os.mkdir(path)
        ht_common.call_program(os.path.join("ASM", "toolchain", "Fireflower", "nds-extract.exe") + " Base.nds " + os.path.join(path, "data"))

# Build ARM9.
def build_arm9():

    # Safety checks and run fireflower..
    setup_fireflower_for_building()
    ovs = ht_common.run_fireflower()
    if not os.path.exists(ht_common.get_rom_name()):
        print("ERR: Hack folder does not exist! Did you forget to run \"setup.py\"?")
        exit(0)
    rom_info_folder = os.path.join(ht_common.get_rom_name(), "__ROM__")
    if not os.path.exists(rom_info_folder):
        os.mkdir(rom_info_folder)
    arm9_folder = os.path.join(rom_info_folder, "Arm9")
    if not os.path.exists(arm9_folder):
        os.mkdir(arm9_folder)

    # Copy arm9 and modified overlays.
    shutil.copyfile(os.path.join("ASM", "fireflower_data", "data", "arm9.bin"), os.path.join(rom_info_folder, "arm9.bin"))
    nuke.nuke_rom_build_bin()
    for ov in ovs:
        shutil.copyfile(os.path.join("ASM", "fireflower_data", "data", "overlay9", "overlay9_" + str(ov) + ".bin"), os.path.join(rom_info_folder, "Arm9", str(ov) + ".bin"))
        nuke.nuke_rom_build_bin(ov)

        # Patch overlay flags.
        overlays = fs.fs_get_overlays()

        # Find the target overlay and modify flags to 0 to prevent decompression.
        for overlay in overlays:
            if overlay["Id"] == ov:
                overlay["Flags"] = "0x0"
                break

        # Set arm9Overlays.json.
        fs.fs_write_overlays(overlays)

    # Build a sample ROM for testing without assets if needed.
    ht_common.call_program(os.path.join("toolchain", "Fireflower", "nds-build.exe") + " build_rules.txt " + os.path.join("fireflower_data", "Sample.nds"), "ASM")

# Clean ARM9.
def clean_arm9():
    path = os.path.join("ASM", "fireflower_data")
    if os.path.exists(path):
        shutil.rmtree(path)
    for ov in range(0, 103):
        ov_path = os.path.join(ht_common.get_rom_name(), "__ROM__", "Arm9", str(ov) + ".bin")
        if os.path.exists(ov_path):
            os.remove(ov_path)
    ov_file_path = os.path.join(ht_common.get_rom_name(), "__ROM__", "arm9Overlays.json")
    if os.path.exists(ov_file_path):
        os.remove(ov_file_path)
        print("WARNING: Overlays configuration file has been removed, you need to rebuild overlays if custom overlays are used!")


# Build overlays.
def build_libraries():
    # Have to delete build folder for some reason.
    ov_build_path = os.path.join("ASM", "libraries", "build")
    if os.path.exists(ov_build_path):
        shutil.rmtree(ov_build_path)

    base_folder: str = os.path.join("ASM", "libraries")

    # First load the libraries that we will build (overlays&dl)
    system_libraries = load_libraries_definition(os.path.join(base_folder, "system-libraries.json"))
    user_libraries = load_libraries_definition(os.path.join(base_folder, "user-libraries.json"))

    excluded: [str] = []
    for library in (system_libraries + user_libraries):
        if library['type'] == 'dl':
            excluded.append(library['id_name'])

    # First get all the commands and filter the element which are not built yet (the dls)
    command_list = fs.fs_read_command_list()
    command_list.sort(key=lambda x: x[1] not in excluded)

    # Get list of JSON overlays to compile.
    fs.fs_apply_command_list(command_list)

    for library in user_libraries + system_libraries:
        cc.compile_overlay(library)

    fs.fs_apply_command_list(fs.fs_read_command_list())


# Clean overlays.
def clean_libraries():
    build_folder = os.path.join("ASM", "libraries", "build")
    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    ov_path = os.path.join(ht_common.get_rom_name(), "__ROM__", "Arm9")
    if os.path.exists(ov_path):
        for ovs in os.walk(ov_path):
            for ov in ovs[2]:
                id = ov.split(".")[0]
                if id.isnumeric():
                    num = int(id)
                    if num > 154:
                        os.remove(os.path.join(ovs[0], ov))
    ov_file_path = os.path.join(ht_common.get_rom_name(), "__ROM__", "arm9Overlays.json")
    if os.path.exists(ov_file_path):
        os.remove(ov_file_path)
        print("WARNING: Overlays configuration file has been removed, you need to rebuild arm9 patches if arm9 patches are used!")
    print("WARNING: If DLs were used, there is no way for this tool to ensure their removal from the filesystem!")

# Build ASM.
def build_asm():
    build_arm9()
    build_libraries()

# Clean ASM.
def clean_asm():
    clean_arm9()
    clean_libraries()

# Build all.
def build_all():
    build_asm()
    build_rom()

# Clean all.
def clean_all():
    clean_asm()
    nuke.nuke_build_folder()

# Main method.
if __name__ == "__main__":
    # create the parser object
    parser = argparse.ArgumentParser(description='SM64DS Hack Template Builder, by Gota7.')

    base_options = ["all", "asm", "ARM9-patches", "libraries", "ROM"]
    parser.add_argument('--build', dest='build', choices=base_options, help='Will build the given element. Example --build=ROM or --build=all.')
    parser.add_argument('--clean', dest='clean', choices=base_options, help='Will clean the given element. Example --clean=asm or --clean=all.')
    parser.add_argument('--auto-boot', type=lambda s: s.lower() in ['true', '1', 't', 'y', 'yes'], default=None, required=False, help='Enable or disable autostart ROM on build (Persistent option). Example --autoBoot=true, or --autoBoot=false')
    parser.add_argument('--ship-with-xdelta', action='store_true', help='Enable the feature')

    # parse the command line arguments
    args = parser.parse_args()

    to_build = args.build
    to_clean = args.clean

    if args.auto_boot is not None:
        if args.auto_boot:
            file = open(os.path.join("InstallFiles", "autoBoot"), "w")
            file.close()
            print("Build: ROM autostart enabled.")
        else:
            os.remove(os.path.join("InstallFiles", "autoBoot"))
            print("Build: ROM autostart disabled.")

    if to_clean == "all":
        clean_all()
    elif to_clean == "asm":
        clean_asm()
    elif to_clean == "ARM9-patches":
        clean_arm9()
    elif to_clean == "libraries":
        clean_libraries()
    elif to_clean == "ROM":
        nuke.nuke_build_folder()

    if to_clean == "all":
        build_all()
    elif to_clean == "asm":
        build_asm()
    elif to_clean == "ARM9-patches":
        build_arm9()
    elif to_clean == "libraries":
        build_libraries()
    elif to_clean == "ROM":
        build_rom()

    if args.ship_with_xdelta:
        build_ship()

    if to_build is None and to_clean is None and args.auto_boot is None and not args.ship_with_xdelta:
        parser.print_help()