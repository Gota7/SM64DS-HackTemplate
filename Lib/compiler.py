#
# For compiling code to do code hacks.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
import fileManager as fs
import json
import nuke
import os
import shutil
import struct
import sys

# Change a file extension.
def change_ext_to(path, ext):
    if "." in path:
        return path[0 : path.rfind(".")] + ext
    else:
        return path + ext

# Generate a ninja build file. The src and build folders should be absolute, and the other files relative to it.
def gen_ninja_file(src_folder, cpp_files, c_files, s_files, build_folder, code_addr = 0x02400000):

    # Get JSON config.
    config_path = os.path.join("ASM", "fireflowerConfig.json")
    config_file = open(config_path, "r")
    config = json.loads(config_file.read())
    config_file.close()
    buildfile = []

    # Define rules.
    base_path = ht_common.get_abs_dir("ASM").replace("\\", "/")
    include_path = ht_common.get_abs_dir(os.path.join("ASM", "include")).replace("\\", "/")
    symbols_x = ht_common.get_abs_dir(os.path.join("ASM", "Overlays")).replace("\\", "/") + "/symbols.x"
    linker_x = ht_common.get_abs_dir(os.path.join("ASM", "Overlays")).replace("\\", "/") + "/linker.x"
    newcode_map = build_folder + "/newcode.map"
    lib_path = base_path + "/toolchain/ff-gcc/lib/gcc/arm-none-eabi/10.3.1"
    buildfile.append("rule cxx\n")
    buildfile.append("  command = " + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-gcc.exe -I" + include_path + " " + config["build"]["flags"]["c++"] + " " + config["build"]["flags"]["arm9"] + " -c $in -o $out\n")
    buildfile.append("\n")
    buildfile.append("rule cc\n")
    buildfile.append("  command = " + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-gcc.exe -I" + include_path + " " + config["build"]["flags"]["c"] + " " + config["build"]["flags"]["arm9"] + " -c $in -o $out\n")
    buildfile.append("\n")
    buildfile.append("rule as\n")
    buildfile.append("  command = " + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-gcc.exe -I" + include_path + " " + config["build"]["flags"]["asm"] + " " + config["build"]["flags"]["arm9"] + " -c $in -o $out\n")
    buildfile.append("\n")
    buildfile.append("rule ld\n")
    buildfile.append("  command = " + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-ld.exe " + " -T " + linker_x + " -T " + symbols_x + " -g -Map " + newcode_map + " -Ttext " + hex(code_addr) + " -L" + lib_path + " @tmp.rsp -o $out\n")
    buildfile.append("  rspfile = tmp.rsp\n")
    buildfile.append("  rspfile_content = $in\n")
    buildfile.append("rule symbol_dump\n")
    buildfile.append("  command = cmd /C \"" + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-objdump.exe -t $in\" > $out\n")
    buildfile.append("rule make_bin\n")
    buildfile.append("  command = " + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-objcopy.exe -O binary $in $out\n")
    buildfile.append("\n")

    # Generate object files.
    o_files = []
    for cpp in cpp_files:
        o_file = build_folder + "/" + change_ext_to(cpp, ".o")
        buildfile.append("build " + o_file + ": cxx " + src_folder + "/" + cpp + "\n")
        #buildfile.append("  d = " + build_folder + "/deps/" + change_ext_to(cpp, ".d") + "\n")
        o_files.append(o_file)
    for c in c_files:
        o_file = build_folder + "/" + change_ext_to(c, ".o")
        buildfile.append("build " + o_file + ": cc " + src_folder + "/" + c + "\n")
        #buildfile.append("  d = " + build_folder + "/deps/" + change_ext_to(c, ".d") + "\n")
        o_files.append(o_file)
    for s in s_files:
        o_file = build_folder + "/" + change_ext_to(s, ".o")
        buildfile.append("build " + o_file + ": as " + src_folder + "/" + s + "\n")
        #buildfile.append("  d = " + build_folder + "/deps/" + change_ext_to(s, ".d") + "\n")
        o_files.append(o_file)

    # Generate ELF and symbol map.
    file_listing = ""
    for o in o_files:
        file_listing += " " + o
    if file_listing == "":
        file_listing = " "
    buildfile.append("build " + build_folder + "/newcode.elf: ld" + file_listing + "\n")
    buildfile.append("build " + build_folder + "/newcode.sym: symbol_dump " + build_folder + "/newcode.elf\n")

    # Generate newcode.bin.
    buildfile.append("build " + build_folder + "/newcode.bin: make_bin " + build_folder + "/newcode.elf\n")

    # Save the build file.
    ninja_file = open(os.path.join("ASM", "Overlays", "build.ninja"), "w")
    ninja_file.writelines(buildfile)
    ninja_file.close()

# Compile an overlay.
def compile_overlay(ov_name):

    # Get symbols from 9x first.
    symbols_file_path = os.path.join("ASM", "symbols9.x")
    symbols_file = open(symbols_file_path, "r")
    symbols = symbols_file.readlines()
    symbols_file.close()

    # Get symbols from patches ELF if it exists.
    obj_copy = os.path.join("ASM", "toolchain", "ff-gcc", "bin", "arm-none-eabi-objdump.exe")
    elf_path = os.path.join("ASM", "fireflower_data", "build", "arm9.elf")
    symbols_file_path = os.path.join("ASM", "fireflower_data", "build", "arm9.sym")
    if (os.path.exists(elf_path)):
        symbols = []
        ht_common.call_program(obj_copy + " -t " + elf_path)
        for symbol in ht_common.get_tmp_data("r").split('\n'):
            data = symbol.split()
            if (len(data) == 5 or len(data) == 6):
                #if not "*ABS*" in data[2] and not "*ABS*" in data[3]:
                symbol_name = data[len(data) - 1]
                if not symbol_name.startswith(".") and not "*ABS*" in symbol_name:
                    addr = int(data[0], 16)
                    symbols += symbol_name + "\t\t\t = " + hex(addr) + ";\n"
        symbols_file_path = os.path.join("ASM", "Overlays", "symbols.x")
        symbols_file = open(symbols_file_path, "w")
        symbols_file.writelines(symbols)
        symbols_file.close()

    # First, get the settings.
    ov_folder = os.path.join("ASM", "Overlays")
    ov_settings_path = os.path.join(ov_folder, ov_name + ".json")
    if not os.path.exists(ov_settings_path):
        print("ERR: Overlay settings file does not exist!")
        exit(0)
    ov_settings_file = open(ov_settings_path, "r")
    ov_settings = json.loads(ov_settings_file.read())
    ov_settings_file.close()

    # Parse settings.
    type = ov_settings["type"]
    id_name = ov_settings["id_name"]
    code_addr = 0x02400000
    is_overlay = type == "overlay"
    if is_overlay:
        code_addr = int(ov_settings["code_addr"][2:], 16)

    # Get files.
    cpp_files = []
    c_files = []
    s_files = []
    for file in ov_settings["files"]:
        if file.endswith(".cpp"):
            cpp_files.append(file)
        elif file.endswith(".c"):
            c_files.append(file)
        else:
            s_files.append(file)

    # Build folder.
    build_folder = os.path.join(ov_folder, "build")
    if not os.path.exists(build_folder):
        os.mkdir(build_folder)

    # Build the ninja file.
    gen_ninja_file(ht_common.get_abs_dir(ov_folder).replace("\\", "/").replace(":", "$:"), cpp_files, c_files, s_files, ht_common.get_abs_dir(build_folder).replace("\\", "/").replace(":", "$:"), code_addr)

    # Run ninja.
    ht_common.call_program(os.path.join("Editor", "ninja.exe") + " -f " + os.path.join(ov_folder, "build.ninja"), "", sys.stdout, sys.stderr)

    # Hack folder check.
    if not os.path.exists(ht_common.get_rom_name()):
        print("ERR: Hack folder does not exist! Did you forget to run \"setup.py\"?")
        exit(0)

    # Overlay tools.
    if is_overlay:

        # Check for valid ID.
        if not id_name.isnumeric():
            print("ERR: Overlay ID is invalid!")
            exit(0)

        # Find location of init symbol.
        init_loc = -1
        symbols = open(os.path.join(build_folder, "newcode.sym"), "r")
        lines = symbols.readlines()
        symbols.close()
        for line in lines:
            if "_Z4initv" == line.split(' ')[-1].strip(): # Space to ensure authenticity.
                init_loc = int(line[0:8], 16)
                break
        if (init_loc == -1):
            print("WARN: Can not find init function for " + ov_name + "!")
            init_loc = 0

        # Get newcode and save overlay.
        newcode_file = open(os.path.join(build_folder, "newcode.bin"), "rb")
        newcode = newcode_file.read()
        newcode_file.close()
        ov_path = os.path.join(ht_common.get_rom_name(), "__ROM__", "Arm9")
        if not os.path.exists(ov_path):
            os.makedirs(ov_path)
        ov_path = os.path.join(ov_path, id_name + ".bin")
        ov = open(ov_path, "wb")
        ov.write(newcode)
        while ov.tell() % 4:
            ov.write(bytearray(1))
        static_init_start = ov.tell() + code_addr
        ov.write(struct.pack("<I", init_loc))
        ram_size = static_init_end = ov.tell()
        static_init_end += code_addr
        ov.close()

        # Adjust overlay settings.
        overlays = fs.fs_get_overlays()

        # Find the proper overlay.
        ov = None
        for overlay in overlays:
            if overlay["Id"] == int(id_name):
                ov = overlay
                file_id = ov["FileId"]
                break

        # Add overlay if it doesn't exist.
        if not ov:
            ov = dict()
            ov["Id"] = int(id_name)
            overlays.append(ov)
            file_id = hex(fs.fs_get_first_free_id())

        # Modify the overlay.
        ov["RAMAddress"] = hex(code_addr)
        ov["RAMSize"] = hex(ram_size)
        ov["BSSSize"] = hex(0)
        ov["StaticInitStart"] = hex(static_init_start)
        ov["StaticInitEnd"] = hex(static_init_end)
        ov["FileId"] = file_id
        ov["Flags"] = hex(0)

        # Set arm9Overlays.json.
        fs.fs_write_overlays(overlays)

        # Make sure to clean to allow proper insertion.
        nuke.nuke_rom_build_bin(int(id_name))

    # DL.
    else:
        print("ERR: Currently not supported! Sorry!")
        exit(0)