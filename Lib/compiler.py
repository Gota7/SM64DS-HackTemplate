#
# For compiling code to do code hacks.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
import json
import os

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
    buildfile.append("  command = " + base_path + "/toolchain/ff-gcc/bin/arm-none-eabi-ld.exe -T " + symbols_x + " -g -Map " + newcode_map + " -Ttext " + hex(code_addr) + " -L" + lib_path + " @tmp.rsp -o $out\n")
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