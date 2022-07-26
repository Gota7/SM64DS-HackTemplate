#
# Script to manage the filesystem.
#   2022 Gota7.
#

import shutil
import Lib.ht_common as ht_common
import json
import os
from time import sleep

# Test to make sure that base and hack folders exist.
def fs_check_folders():
    if not os.path.exists("Base") or not os.path.exists(ht_common.get_rom_name()):
        print("ERR: Base and hack paths not found! Did you run \"setup.py\"?")
        exit(0)

# Restore from a backup.
def fs_restore_base():
    fs_check_folders()
    shutil.copyfile(os.path.join("ASM", "Overlays", "filenames", "filenamesBak.h"), os.path.join("ASM", "Overlays", "filenames", "filenames.h"))
    shutil.copyfile(os.path.join("Base", "__ROM__", "files.txt"), os.path.join(ht_common.get_rom_name(), "__ROM__", "files.txt"))

# Fetch a file from the filesystem.
def fs_get_file(file_path, binary = True):
    path = ""
    for dir in file_path.split("/"):
        if path == "":
            path = dir
        else:
            path = os.path.join(path, dir)

    # Get base and patch paths.
    fs_check_folders()
    base_path = os.path.join("Base", path)
    patch_path = os.path.join(ht_common.get_rom_name(), path)

    # Get file.
    mode = "r"
    if binary:
        mode = "rb"
    if os.path.exists(patch_path):
        return open(patch_path, mode)
    elif os.path.exists(base_path):
        return open(base_path, mode)
    else:
        print("ERR: File " + file_path + " not found!")
        exit(0)

# Write a file to the filesystem.
def fs_write_file(file_path, binary = True):
    path = ht_common.get_rom_name()
    split = file_path.split("/")
    for dir in split:
        path = os.path.join(path, dir)
        if dir != split[len(split) - 1] and not os.path.exists(path):
            os.mkdir(path)

    # Get file handle.
    mode = "w"
    if binary:
        mode = "wb"
    return open(path, mode)

# Get overlays list.
def fs_get_overlays(arm7 = False):
    if arm7:
        ov_file = fs_get_file("__ROM__/arm7Overlays.json", False)
    else:
        ov_file = fs_get_file("__ROM__/arm9Overlays.json", False)
    overlays = json.loads(ov_file.read())
    ov_file.close()
    return overlays

# Write overlays list.
def fs_write_overlays(overlays, arm7 = False):
    if arm7:
        ov_file = fs_write_file("__ROM__/arm7Overlays.json", False)
    else:
        ov_file = fs_write_file("__ROM__/arm9Overlays.json", False)
    ov_file.write(json.dumps(overlays, indent=2))
    ov_file.close()

# Get an overlay from an id.
def fs_get_overlay_from_id(ovs, id):
    for ov in ovs:
        if ov["Id"] == id:
            return ov
    return None

# Get file listing sorted by file ID. Overlays will start with @7_ID or @9_ID.
def fs_get_filelist():
    files = []
    file_list_file = fs_get_file("__ROM__/files.txt", False)
    file_list = file_list_file.readlines()
    file_list_file.close()
    for file in file_list:
        if " " in file:
            split = file.split(" ")
            files.append((split[0].strip()[3:], split[1].strip()))
    for ov in fs_get_overlays(True):
        files.append(("@7_" + str(ov["Id"]), ov["FileId"].strip()))
    for ov in fs_get_overlays(False):
        files.append(("@9_" + str(ov["Id"]), ov["FileId"].strip()))
    files.sort(key=lambda y: int(y[1][2:], 16))
    return files

# Write a list of files.
def fs_write_filelist(files):
    file_list = fs_write_file("__ROM__/files.txt", False)
    for file in files:
        if not file[0].startswith("@7_") and not file[0].startswith("@9_"):
            file_list.write("../" + file[0] + " " + file[1] + "\n")
    file_list.close()

# Get a list of OV0 and file path values.
def fs_get_ov0_filename_tuples():
    def_file = open(os.path.join("ASM", "Overlays", "filenames", "filenames.h"), "r")
    vals = []
    for line in def_file.readlines():
        if "{0x" in line:
            data = line.split("{")[1].split("}")[0].replace("\"", "").replace(" ", "").split(",")
            vals.append((int(data[0][2:], 16), data[1]))
    def_file.close()
    vals.sort(key=lambda y: y[0])
    return vals

# Write a list of OV0 and file path values.
def fs_set_ov0_filename_tuples(vals):
    vals.sort(key=lambda y: y[0])
    orig_lines_file = open(os.path.join("ASM", "Overlays", "filenames", "filenamesBak.h"), "r")
    orig_lines = orig_lines_file.readlines()
    orig_lines_file.close()
    def_file = open(os.path.join("ASM", "Overlays", "filenames", "filenames.h"), "w")
    stop_pos = 0
    for line in orig_lines:
        if "{0x" in line:
            break
        else:
            def_file.write(line)
            stop_pos += 1

    # Convert values to array.
    res = [None] * (vals[len(vals) - 1][0] + 1)
    for val in vals:
        res[val[0]] = val[1]
    for i in range(0, len(res)):
        if not res[i]:
            res[i] = "data/sound_data.sdat" # Need something to fill the gap, do sound_data.sdat since its path is hardcoded to the game.

    # Print values.
    for i in range(0, len(res)):
        if i == len(res) - 1:
            suffix = "\n"
        else:
            suffix = ",\n"
        def_file.write("        {" + hex(i) + ", \"" + res[i] + "\"}" + suffix)
    for i in range(stop_pos, len(orig_lines)):
        line = orig_lines[i]
        if not "{0x" in line:
            def_file.write(line)
    def_file.close()

    # Other one this time.
    def_file = open(os.path.join("ASM", "Overlays", "filenames", "filenamesWhole.h"), "w")
    def_file.write("#ifndef FILENAMES_H\n")
    def_file.write("#define FILENAMES_H\n")
    def_file.write("\n")
    def_file.write("const char* filenameList[] =\n")
    def_file.write("{\n")

    # Convert values to array.
    res = [None] * (vals[len(vals) - 1][0] + 1)
    for val in vals:
        res[val[0]] = val[1]
    for i in range(0, len(res)):
        if not res[i]:
            res[i] = "data/sound_data.sdat" # Need something to fill the gap, do sound_data.sdat since its path is hardcoded to the game.

    # Print values.
    for i in range(0, len(res)):
        if i == len(res) - 1:
            suffix = "\n"
        else:
            suffix = ",\n"
        def_file.write("    \"" + res[i] + "\"" + suffix)
    def_file.write("};\n")
    def_file.write("\n")
    def_file.write("#endif\n")
    def_file.close()

# Get an overlay 0 ID.
def fs_get_ov0_id(name):
    for item in fs_get_ov0_filename_tuples():
        if item[1] == name:
            return item[0]
    return -1

# Get a file name from an overlay 0 ID.
def fs_get_file_name_from_ov0_id(id):
    for item in fs_get_ov0_filename_tuples():
        if item[0] == id:
            return item[1]
    return None

# Get a free file ID.
def fs_get_first_free_id():
    id = 0
    for f in fs_get_filelist():
        if int(f[1][2:], 16) == id:
            id += 1
        else:
            break
    return id

# Get the first free OV0 ID.
def fs_get_first_free_ov0_id():
    data = fs_get_ov0_filename_tuples()
    found_items = dict()
    for dat in data:
        if dat[1] in found_items:
            return dat[0]
        else:
            found_items[dat[1]] = dat[0]
    return data[len(data) - 1][0] + 1

# Add a file to the filesystem.
def fs_add_file(name, preferred_ov0_id = -1):
    get_test = fs_get_file(name)
    get_test.close()
    if preferred_ov0_id != -1:
        ov0_id = preferred_ov0_id
        if fs_get_file_name_from_ov0_id(preferred_ov0_id):
            print("WARN: File with matching overlay 0 ID exists, skipping.")
            exit(0)
    else:
        ov0_id = fs_get_first_free_ov0_id()
    file_id = fs_get_first_free_id()
    files = fs_get_filelist()
    files.append((name, hex(file_id)))
    fs_write_filelist(files)
    ov0s = fs_get_ov0_filename_tuples()
    ov0s.append((ov0_id, name))
    fs_set_ov0_filename_tuples(ov0s)

# If a name exists.
def fs_name_exists(name):
    for file in fs_get_filelist():
        if file[0] == name:
            return True
    return False

# Rename a file in the filesystem.
def fs_rename_file(name, new_name):
    if fs_name_exists(new_name) or not fs_name_exists(name):
        print("ERR: Either the new name is already taken or the old file doesn't exist!")
        exit(0)
    files = fs_get_filelist()
    for i in range(0, len(files)):
        if files[i][0] == name:
            files[i] = (new_name, files[i][1])
            break
    fs_write_filelist(files)
    ov0s = fs_get_ov0_filename_tuples()
    for i in range(0, len(ov0s)):
        if ov0s[i][1] == name:
            ov0s[i] = (ov0s[i][0], new_name)
            break
    fs_set_ov0_filename_tuples(ov0s)
    file = fs_get_file(name)
    file2 = fs_write_file(new_name)
    file2.write(file.read())
    file.close()
    file2.close()
    path = ""
    for dir in name.split("/"):
        if path == "":
            path = dir
        else:
            path = os.path.join(path, dir)
    path = os.path.join(ht_common.get_rom_name(), path)
    if os.path.exists(path):
        os.remove(path)

# Delete a file from the filesystem.
def fs_del_file(name):
    if ht_common.user_warn():
        if fs_name_exists(name):
            files = fs_get_filelist()
            for i in range(0, len(files)):
                if files[i][0] == name:
                    files.remove(files[i])
                    break
            fs_write_filelist(files)
            ov0s = fs_get_ov0_filename_tuples()
            for i in range(0, len(ov0s)):
                if ov0s[i][1] == name:
                    ov0s.remove(ov0s[i])
                    break
            fs_set_ov0_filename_tuples(ov0s)
        path = ""
        for dir in name.split("/"):
            if path == "":
                path = dir
            else:
                path = os.path.join(path, dir)
        path = os.path.join(ht_common.get_rom_name(), path)
        if os.path.exists(path):
            os.remove(path)

# Read a command list.
def fs_read_command_list():
    ret = []
    if os.path.exists("fileOperations.txt"):
        with open("fileOperations.txt", "r") as file:
            for line in file.readlines():
                items = line.split()
                if len(items) > 0:
                    command = items[0]
                    if command == "add" or command == "addId" or command == "rename" or command == "delete":
                        second = items[1]
                    else:
                        second = int(items[1][2:], 16)
                    if len(items) > 2:
                        if command == "addId":
                            third = int(items[2][2:], 16)
                        else:
                            third = items[2]
                    else:
                        third = ""
                    ret.append((command, second, third))
    ret.sort(key = lambda y: y[1]) # Needed since files in the same dir must be near each other.
    return ret

# Write a command list.
def fs_write_command_list(commands):
    commands.sort(key = lambda y: y[1])
    lines = []
    with open("fileOperations.txt", "w") as file:
        for c in commands:
            line = c[0]
            if type(c[1]) == int:
                line += " " + hex(c[1])
            else:
                line += " " + c[1]
            if c[2] != "":
                if type(c[2]) == int:
                    line += " " + hex(c[2])
                else:
                    line += " " + c[2]
            if not line in lines: # Prevent duplicates.
                file.write(line)
                lines.append(line)

# Apply a command list.
def fs_apply_command_list(commands):
    fs_restore_base()
    for c in commands:
        if c[0] == "add":
            fs_add_file(c[1])
        elif c[0] == "addId":
            fs_add_file(c[1], c[2])
        elif c[0] == "rename":
            fs_rename_file(c[1], c[2])
        elif c[0] == "renameId":
            fs_rename_file(fs_get_file_name_from_ov0_id(c[1]), c[2])
        elif c[0] == "delete":
            fs_del_file(c[1])
        elif c[0] == "deleteId":
            fs_del_file(fs_get_file_name_from_ov0_id(c[1]))

# Test.
if __name__ == "__main__":
    print("SM64DS Hack Template File Manager:")
    print("  2022 Gota7")
    opt = 0
    options = [ "Add file.", "Add file by ov0 id.", "Rename file.", "Rename file by ov0 id.", "Delete file.", "Delete file by ov0 id.", "Convert file name to ov0 id.", "Convert ov0 id to file name.", "Exit." ]
    commands = fs_read_command_list()
    while opt != len(options):
        sleep(1)
        opt = ht_common.user_options_prompt("Filesystem Options:", options)
        if opt == 1:
            file_name = ht_common.user_prompt("File name to add (blank to cancel)")
            if file_name != "":
                commands.append(("add", file_name, ""))
        elif opt == 2:
            id = ht_common.user_prompt("Overlay 0 id for file (blank to cancel)")
            if id != "":
                if id.startswith("0x"):
                    id = int(id[2:], 16)
                else:
                    id = int(id)
                file_name = ht_common.user_prompt("File name (blank to cancel)")
                if file_name != "":
                    commands.append(("addId", file_name, id))
        elif opt == 3:
            file_name = ht_common.user_prompt("File name (blank to cancel)")
            if file_name != "":
                new_file_name = ht_common.user_prompt("New file name (blank to cancel)")
                if new_file_name != "":
                    commands.append(("rename", file_name, new_file_name))
        elif opt == 4:
            id = ht_common.user_prompt("Overlay 0 id for file (blank to cancel)")
            if id != "":
                if id.startswith("0x"):
                    id = int(id[2:], 16)
                else:
                    id = int(id)
                new_file_name = ht_common.user_prompt("New file name (blank to cancel)")
                if new_file_name != "":
                    file_name = fs_get_file_name_from_ov0_id(id)
                    if not file_name:
                        print("ERR: Can not find file with given ov0 id!")
                        exit(0)
                    else:
                        commands.append(("renameId", id, new_file_name))
        elif opt == 5:
            file_name = ht_common.user_prompt("File name to delete (blank to cancel)")
            if file_name != "":
                commands.append(("del", file_name, ""))
        elif opt == 6:
            id = ht_common.user_prompt("Overlay 0 id for file (blank to cancel)")
            if id != "":
                if id.startswith("0x"):
                    id = int(id[2:], 16)
                else:
                    id = int(id)
                file_name = fs_get_file_name_from_ov0_id(id)
                if not file_name:
                    print("ERR: Can not find file with given ov0 id!")
                    exit(0)
                else:
                    commands.append(("delId", id, ""))
        elif opt == 7:
            file_name = ht_common.user_prompt("File name (blank to cancel)")
            if file_name != "":
                id = fs_get_ov0_id(file_name)
                if id == -1:
                    print("ERR: Given file does not have an ov0 id!")
                    exit(0)
                else:
                    print(hex(id))
        elif opt == 8:
            id = ht_common.user_prompt("Overlay 0 id for file (blank to cancel)")
            if id != "":
                if id.startswith("0x"):
                    id = int(id[2:], 16)
                else:
                    id = int(id)
                file_name = fs_get_file_name_from_ov0_id(id)
                if not file_name:
                    print("ERR: Can not find file with given ov0 id!")
                    exit(0)
                else:
                    print(file_name)
        fs_write_command_list()