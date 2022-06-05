#
# For compiling code to do code hacks.
#   2022 Gota7.
#

import json
import os

def gen_ninja_file(src_folder, cpp_files, c_files, s_files, build_folder):

    # Get JSON config.
    config_path = os.path.join("ASM", "fireflowerConfig.json")
    config_file = open(config_path, "r")
    config = json.loads(config_file.read())
    config_file.close()
    buildfile = []

    # Define rules. # TODO: ADD -MMD and -MMF for .d files!
    buildfile.append("rule cx\n")
    buildfile.append("  command = ../toolchain/ff-gcc/bin/arm-none-eabi-gcc.exe -I../include " + config["build"]["flags"]["c++"] + " " + config["build"]["flags"]["arm9"] + " -c $in -o $out\n")
    buildfile.append("\n")
    buildfile.append("rule cc\n")
    buildfile.append("  command = ../toolchain/ff-gcc/bin/arm-none-eabi-gcc.exe -I../include " + config["build"]["flags"]["c"] + " " + config["build"]["flags"]["arm9"] + " -c $in -o $out\n")
    buildfile.append("\n")
    buildfile.append("rule as\n")
    buildfile.append("  command = ../toolchain/ff-gcc/bin/arm-none-eabi-gcc.exe -I../include " + config["build"]["flags"]["asm"] + " " + config["build"]["flags"]["arm9"] + " -c $in -o $out\n")
    buildfile.append("\n")
    # TODO: LD RULE!!!

    # TODO: GEN BUILD COMMANDS!!!

    # Save the build file.
    ninja_file = open(os.path.join("ASM", "Overlays", "build.ninja"), "w")
    ninja_file.writelines(buildfile)
    ninja_file.close()

if __name__ == "__main__":
    gen_ninja_file("", [], [], [], "")