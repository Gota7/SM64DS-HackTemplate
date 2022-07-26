#
# Build the ROM, ASM hacks, overlays, etc.
#   2022 Gota7.
#

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
    input("ARM9 patches finished. Press Enter to continue...")

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
def build_overlays():

    # Have to delete build folder for some reason.
    ov_build_path = os.path.join("ASM", "Overlays", "build")
    if os.path.exists(ov_build_path):
        shutil.rmtree(ov_build_path)

    # Get list of JSON overlays to compile.
    for file_tuple in os.walk(os.path.join("ASM", "Overlays")):
        for file in file_tuple[2]:
            if file.endswith(".json") and file != "filenames.json":
                cc.compile_overlay(file[0:file.rfind(".")])
    fs.fs_apply_command_list(fs.fs_read_command_list())
    if os.path.exists(os.path.join("ASM", "Overlays", "filenames.json")):
        cc.compile_overlay("filenames")
    input("Overlay insertion finished. Press Enter to continue...")

# Clean overlays.
def clean_overlays():
    build_folder = os.path.join("ASM", "Overlays", "build")
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
    build_overlays()

# Clean ASM.
def clean_asm():
    clean_arm9()
    clean_overlays()

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
    print("SM64DS Hack Template Builder:")
    print("  2022 Gota7")
    opt = 0
    options = []
    base_options = [ "all.", "all ASM.", "ARM9 patches.", "overlays.", "ROM." ]
    for option in base_options:
        options.append("Build " + option)
        options.append("Clean " + option)
        options.append("Clean + Build " + option)
    disable_msg = "Disable autostart ROM on build."
    enable_msg = "Enable autostart ROM on build."
    if ht_common.get_rom_autostart():
        options.append(disable_msg)
    else:
        options.append(enable_msg)
    options.append("Ship ROM xdelta and ZIP.")
    options.append("Exit.")
    while opt != len(options):
        sleep(1)
        opt = ht_common.user_options_prompt("Build Options:", options)
        base_opt = (opt - 1) // 3
        spec = (opt - 1) % 3
        if base_opt < len(base_options):
            if base_opt == 0:
                if spec > 0:
                    clean_all()
                if spec != 1:
                    build_all()
            if base_opt == 1:
                if spec > 0:
                    clean_asm()
                if spec != 1:
                    build_asm()
            if base_opt == 2:
                if spec > 0:
                    clean_arm9()
                if spec != 1:
                    build_arm9()
            if base_opt == 3:
                if spec > 0:
                    clean_overlays()
                if spec != 1:
                    build_overlays()
            if base_opt == 4:
                if spec > 0:
                    nuke.nuke_build_folder()
                if spec != 1:
                    build_rom()
        elif opt == len(options) - 2:
            if ht_common.get_rom_autostart():
                os.remove(os.path.join("InstallFiles", "autoBoot"))
                options[len(options) - 3] = enable_msg
                print("Build: ROM autostart disabled.")
            else:
                file = open(os.path.join("InstallFiles", "autoBoot"), "w")
                file.close()
                options[len(options) - 3] = disable_msg
                print("Build: ROM autostart enabled.")
        elif opt == len(options) - 1:
            build_ship()