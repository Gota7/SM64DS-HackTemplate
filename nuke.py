from socket import SHUT_RD
import Lib.ht_common as ht_common
import os
import shutil

# Remove tools.
def nuke_tools():
    if os.path.exists(os.path.join("InstallFiles", "toolsInstalled")):
        os.remove(os.path.join("InstallFiles", "toolsInstalled"))
    if os.path.exists("Editor"):
        shutil.rmtree("Editor")
    if os.path.exists("Tools"):
        shutil.rmtree("Tools")
    print("Nuke: Tools deleted.")

# Remove base ROM folder.
def nuke_base():
    if os.path.exists("Base"):
        shutil.rmtree("Base")
    if os.path.exists("Conversions"):
        shutil.rmtree("Conversions")
    print("Nuke: Base ROM info deleted.")

# Remove build folder.
def nuke_build_folder():
    path = os.path.join("Editor", "build")
    if os.path.exists(path):
        shutil.rmtree(path)
    print("Nuke: Build folder deleted.")

# Remove __ROM__ binary (can get funky when rebuilding ROM).
def nuke_rom_build_bin(ov = -1):
    path = os.path.join("Editor", "build", "__ROM__")
    if ov != -1:
        path = os.path.join(path, "arm9.bin")
    else:
        path = os.path.join(path, "Arm9", str(ov) + ".bin")
    if os.path.exists(path):
        os.remove(path)

# Remove hack.
def nuke_hack():
    path = "Patch"
    if os.path.exists(path):
        shutil.rmtree(path)
    print("Nuke: Hack deleted.")

# Nuke ASM.
def nuke_asm():
    path = "ASM"
    if os.path.exists(path):
        shutil.rmtree(path)
    ht_common.download_zip("https://github.com/Gota7/SM64DS-HackTemplate/archive/refs/heads/main.zip", os.path.join("SM64DS-HackTemplate-main", "ASM"), "ASM")
    print("Nuke: ASM reset.")

# Remove everything.
def nuke():
    nuke_asm()
    nuke_base()
    nuke_tools()
    nuke_hack()
    print("Nuke: Everything deleted.")

# Main method.
if __name__ == "__main__":
    print("SM64DS Hack Template Nuker:")
    print("  2022 Gota7")
    opt = -1
    while opt != 7:
        opt = ht_common.user_options_prompt("\nNuke Options:", ["Delete build folder.", "Remove tools.", "Remove base ROM folder.", "Reset ASM folder.", "Delete hack.", "Nuke everything.", "Quit." ])
        if opt == 1:
            nuke_build_folder()
        elif opt == 2:
            nuke_tools()
        elif opt == 3:
            if ht_common.user_warn():
                nuke_base()
        elif opt == 4:
            if ht_common.user_warn():
                nuke_asm()
        elif opt == 5:
            if ht_common.user_warn():
                nuke_hack()
        elif opt == 6:
            if ht_common.user_warn():
                nuke()
            pass