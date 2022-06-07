#
# Script to manage the filesystem.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
import json
import os

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

# Get a free file ID.
def fs_get_first_free_id():
    id = 0
    for f in fs_get_filelist():
        if int(f[1][2:], 16) == id:
            id += 1
        else:
            break
    return id

# Test.
if __name__ == "__main__":
    print(hex(fs_get_first_free_id()))