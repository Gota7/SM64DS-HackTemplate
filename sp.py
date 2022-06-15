#
# SM64DS patch applier.
#   2022 Gota7.
#

import fileManager as fs
import Lib.ht_common as ht_common
import os

# Replace the ARM9. It's a bad idea.
def replace_arm9(new_file_path):
    new_file = open(new_file_path, "rb")
    old_file = fs.fs_write_file("__ROM__/arm9.bin")
    old_file.write(new_file.read())
    new_file.close()
    old_file.close()

# Rename a file.
def rename_file(old_file, new_file):
    if old_file.isnumeric():
        old_file = fs.fs_get_file_name_from_ov0_id(int(old_file))
    fs.fs_rename_file(old_file, new_file)

# Replace an overlay.
def replace_overlay(id, new_file_path):
    new_file = open(new_file_path, "rb")
    old_file = fs.fs_write_file("__ROM__/Arm9/" + str(id) + ".bin")
    old_file.write(new_file.read())
    ram_size = old_file.tell()
    new_file.close()
    old_file.close()
    ovs = fs.fs_get_overlays()
    for ov in ovs:
        if ov["Id"] == id: # Assume new version isn't compressed.
            ov["RAMSize"] = hex(ram_size)
            ov["Flags"] = hex(0)
            break
    fs.fs_write_overlays(ovs)

# Delete an overlay.
def delete_overlay(id):
    ovs = fs.fs_get_overlays()
    for i in range(0, len(ovs)):
        if ovs[i]["Id"] == id:
            ovs.remove(ovs[i])
            break
    fs.fs_write_overlays(ovs)

# Run a patch command.
def run_patch_command(patch_dir, command, args):

    # SP original version commands.
    if command == "replace":
        print("ERR: Feature not implemented yet!")
    elif command == "replace_arm9":
        print("WARN: Replacing the ARM9 is deprecated as it will be overwritten by the next ASM build!")
        replace_arm9(args[0])
    elif command == "replace_overlay":
        print("ERR: Feature not implemented yet!")
    elif command == "rename":
        rename_file(args[0], args[1])
    elif command == "import_xml":
        print("WARN: Importing level XML is unsupported and so does nothing!")
    elif command == "add_overlay":
        print("ERR: Feature not implemented yet!")
    elif command == "edit_overlay":
        print("ERR: Feature not implemented yet!")
    elif command == "replace_overlay":
        replace_overlay(int(args[0]), patch_dir + "/" + args[1])
    elif command == "delete_overlay":
        delete_overlay(int(args[0]))

    # SP2 commands.
    elif command == "add_file":
        print("ERR: Feature not implemented yet!")
    elif command == "export":
        print("ERR: Feature not implemented yet!")
    elif command == "export_overlay":
        print("ERR: Feature not implemented yet!")
    elif command == "export_level":
        print("ERR: Feature not implemented yet!")
    elif command == "import_level":
        print("ERR: Feature not implemented yet!")
    elif command == "export_folder":
        print("ERR: Feature not implemented yet!")
    elif command == "import_folder":
        print("ERR: Feature not implemented yet!")

# Apply a patch.
def apply_patch(patch_file_path):
    patch_file = open(patch_file_path, "r")
    patch_dir = os.path.dirname(patch_file_path)
    for line in patch_file.readlines():
        dat = line
        if "#" in dat:
            dat = dat[0:dat.index("#")]
        data = dat.split()
        args = []
        if len(data) > 1:
            args = data[1:]
        if len(data) > 0:
            run_patch_command(patch_dir, data[0].lower(), args)
    patch_file.close()
    pass

# Generate a patch. TODO!!!
def gen_patch():
    pass

# Main method.
if __name__ == "__main__":
    print("SM64DS Hack Template File Manager:")
    print("  2022 Gota7")
    opt = 0
    options = [ "Import patch.", "Export hack as patch.", "Exit." ]
    while opt != len(options):
        if opt == 1:
            patch_path = ht_common.user_prompt("Patch to import (blank to cancel)")
            if patch_path != "":
                apply_patch(patch_path)
        elif opt == 2:
            print("ERR: Feature not implemented yet!")
            exit(0)