#
# Script to manage the filesystem.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
import json
import os
from time import sleep

# Test to make sure that base and hack folders exist.
def fs_check_folders():
    if not os.path.exists("Base") or not os.path.exists(ht_common.get_rom_name()):
        print("ERR: Base and hack paths not found! Did you run \"setup.py\"?")
        exit(0)

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
    pass

# Get a list of OV0 and file path values.
def fs_get_ov0_filename_tuples():
    def_file = open(os.path.join("ASM", "Overlays", "filenames", "filenames.h"), "r")
    vals = []
    curr_ind = 0
    for line in def_file.readlines():
        if "\"" in line:
            vals.append((curr_ind, line.split("\"")[1]))
            curr_ind += 1
    def_file.close()
    return vals

# Write a list of OV0 and file path values.
def fs_set_ov0_filename_tuples(vals):
    vals.sort(key=lambda y: y[0])
    def_file = open(os.path.join("ASM", "Overlays", "filenames", "filenames.h"), "w")
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
    return "data/sound_data.sdat"

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
    if preferred_ov0_id == -1:
        ov0_id = preferred_ov0_id
        for ov in fs_get_ov0_filename_tuples():
            if ov[0] == ov0_id:
                print("WARN: File with matching overlay 0 ID exists, skipping.")
                exit()
    else:
        ov0_id = fs_get_first_free_ov0_id()
    file_id = fs_get_first_free_id()
    files = fs_get_filelist()
    files.append((name, file_id))
    fs_write_filelist(files)
    ov0s = fs_get_ov0_filename_tuples()
    ov0s.append((ov0_id, name))
    fs_set_ov0_filename_tuples(ov0s)

# If a name exists.
def fs_name_exists(name):
    for file in fs_get_filelist():
        if file == name:
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
            files[i][0] = new_name
            break
    fs_write_filelist(files)
    ov0s = fs_get_ov0_filename_tuples()
    for i in range(0, len(ov0s)):
        if ov0s[i][1] == name:
            ov0s[i][1] = new_name
            break
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
        pass

# Test.
if __name__ == "__main__":
    print("SM64DS Hack Template File Manager:")
    print("  2022 Gota7")
    opt = 0
    options = [ "Add file", "Add file by ov0 id", "Rename file", "Rename file by ov0 id", "Delete file", "Delete file by ov0 id", "Exit" ]
    while opt != len(options):
        sleep(1)
        opt = ht_common.user_options_prompt("Filesystem Options:", options)