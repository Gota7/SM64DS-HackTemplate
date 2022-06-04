#
# Script used to make sure all the necessary tools are installed.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
from io import SEEK_SET
import os
import shutil

# Wizard for installing tools.
def toolsInstall():

    # Check for .NET 6.0 installation.
    ht_common.call_program("dotnet --list-sdks")
    if not "6.0" in ht_common.get_tmp_data("r"):
        print("Checking .NET 6.0... FAIL")
        print("ERR: .NET 6.0 is not installed and is needed to run Ndst!")
        exit(0)
    print("Checking .NET 6.0... OK")

    # Download SM64DSe.
    if not os.path.exists("Editor") or ht_common.user_yn_prompt("SM64DSe is already installed, reinstall?"):
        if os.path.exists("Editor"):
            shutil.rmtree("Editor")
        print("Installing SM64DSe...")
        ht_common.download_zip("https://github.com/Gota7/SM64DSe-Ultimate/archive/refs/heads/master.zip", os.path.join("SM64DSe-Ultimate-master", "bin", "Release"), "Editor")
        shutil.copyfile(os.path.join("InstallFiles", "obj_list.txt"), os.path.join("Editor", "obj_list.txt"))
        shutil.copyfile(os.path.join("InstallFiles", "objectdb.xml"), os.path.join("Editor", "objectdb.xml"))
    print("SM64DSe installed... OK")

    # Make tools directory.
    if not os.path.exists("Tools"):
        os.mkdir("Tools")

    # Download ARM_GCC.
    arm_gcc_path = os.path.join("Tools", "ARM_GCC")
    if not os.path.exists(arm_gcc_path) or ht_common.user_yn_prompt("ARM_GCC is already installed, reinstall?"):
        if os.path.exists(arm_gcc_path):
            shutil.rmtree(arm_gcc_path)
        print("Installing ARM_GCC...")
        ht_common.download_zip("https://developer.arm.com/-/media/Files/downloads/gnu-rm/10.3-2021.10/gcc-arm-none-eabi-10.3-2021.10-win32.zip", "gcc-arm-none-eabi-10.3-2021.10", arm_gcc_path)
    print("ARM_GCC installed... OK")

    # Download fireflower.
    fireflower_path = os.path.join("Tools", "Fireflower")
    if not os.path.exists(fireflower_path) or ht_common.user_yn_prompt("Fireflower is already installed, reinstall?"):
        if os.path.exists(fireflower_path):
            shutil.rmtree(fireflower_path)
        print("Installing Fireflower...")
        ht_common.download_zip("https://github.com/MammaMiaTeam/Fireflower/releases/download/1.0/fireflower.zip", "", fireflower_path)
        shutil.copyfile(os.path.join("InstallFiles", "buildroot.txt"), os.path.join("Tools", "Fireflower", "buildroot.txt"))
    print("Fireflower installed... OK")

    # Tools have been installed.
    success = open(os.path.join("InstallFiles", "toolsInstalled"), "w")
    success.close()
    print("Tools have been successfully installed!")

# Main method.
if __name__ == "__main__":
    toolsInstall()