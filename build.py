#
# Build the ROM, ASM hacks, overlays, etc.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
import nuke
import os
from sys import stderr, stdout
import sys
from time import sleep

# Build ROM.
def build_rom():
    if not os.path.exists("Base") or not os.path.exists("Conversions") or not os.path.exists(ht_common.get_rom_name()):
        print("ERR: Base ROM and hack folders are not present! Did you run \"setup.py\" first?")
        exit(0)
    ht_common.run_ndst("-n " + os.path.join("..", "Base") + " " + os.path.join("..", ht_common.get_rom_name()) + " " + os.path.join("..", "Conversions") + " " + os.path.join("..", ht_common.get_rom_name()) + ".nds")
    # Linux hack - use Ndst-Lin.
    if sys.platform == "linux" or sys.platform == "linux2":
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
        ht_common.call_program("ninja.exe", "Editor", stdout, stderr)
    print("Build: ROM built.")
    if ht_common.get_rom_autostart():
        print("Build: Opening ROM...")
        if sys.platform == "linux" or sys.platform == "linux2":
            ht_common.call_program_nowine("xdg-open " + ht_common.get_rom_name() + ".nds")
        else:
            os.startfile(ht_common.get_rom_name() + ".nds")

# Build ARM9.
def build_arm9():
    pass

# Clean ARM9.
def clean_arm9():
    pass

# Build overlays.
def build_overlays():
    pass

# Clean overlays.
def clean_overlays():
    pass

# Build ASM.
def build_asm():
    pass

# Clean ASM.
def clean_asm():
    pass

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
        elif opt == len(options) - 1:
            if ht_common.get_rom_autostart():
                os.remove(os.path.join("InstallFiles", "autoBoot"))
                options[len(options) - 2] = enable_msg
                print("Build: ROM autostart disabled.")
            else:
                file = open(os.path.join("InstallFiles", "autoBoot"), "w")
                file.close()
                options[len(options) - 2] = disable_msg
                print("Build: ROM autostart enabled.")