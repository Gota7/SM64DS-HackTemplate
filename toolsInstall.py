#
# Script used to make sure all the necessary tools are installed.
#   2022 Gota7.
#

import Lib.ht_common as ht_common
from io import SEEK_SET
import os
import shutil

# Check for .NET 6.0 installation.
ht_common.call_program("dotnet --list-sdks")
if not "6.0" in ht_common.get_tmp_data("r"):
    print("Checking .NET 6.0... FAIL")
    print("ERR: .NET 6.0 is not installed and is needed to run Ndst!")
    exit(0)
print("Checking .NET 6.0... OK")

# Download SM64DSe.
if not os.path.exists("Editor") or ht_common.user_yn_prompt("SM64DS is already installed, reinstall?"):
    if os.path.exists("Editor"):
        shutil.rmtree("Editor")
    print("Installing SM64DSe...")
    ht_common.download_zip("https://github.com/Gota7/SM64DSe-Ultimate/archive/refs/heads/master.zip", os.path.join("SM64DSe-Ultimate-master", "bin", "Release"), "Editor")
    shutil.copyfile("InstallFiles/obj_list.txt", "Editor/obj_list.txt")
    shutil.copyfile("InstallFiles/objectdb.xml", "Editor/objectdb.xml")
print("SM64DSe installed... OK")

# Download fireflower.