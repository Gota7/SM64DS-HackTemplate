#
# General functions that are used throughout the template.
#   2022 Gota7.
#

import os
import hashlib
import urllib.request
import subprocess
import sys
import zipfile

# Get the hash of a file.
def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

# Remove a dir if empty.
def remove_empty_dir(path):
    try:
        os.rmdir(path)
    except OSError:
        pass

# Remove empty directories.
def remove_empty_dirs(path):
    for root, dirnames, filenames in os.walk(path, topdown=False):
        for dirname in dirnames:
            remove_empty_dir(os.path.realpath(os.path.join(root, dirname)))

# For calling an external program.
def call_program(program, dir = "", out = None, err = None):
    if os.name != 'nt':
        program = "wine " + program     # Non-Windows OS use WINE.
    arr = program.split(' ')
    tmp_file = open(os.path.join("InstallFiles", "tmp"), "w")
    tmp2_file = open(os.path.join("InstallFiles", "tmp2"), "w")
    if dir != "":
        curr_dir = os.getcwd()
        os.chdir(dir)
    if not out:
        out = tmp_file
    if not err:
        err = tmp2_file
    subprocess.call(arr, stdout=out, stderr=err)
    if dir != "":
        os.chdir(curr_dir)
    tmp_file.close()
    tmp2_file.close()

# For calling an external program without wine.
def call_program_nowine(program, dir = "", out = None, err = None):
    arr = program.split(' ')
    tmp_file = open(os.path.join("InstallFiles", "tmp"), "w")
    tmp2_file = open(os.path.join("InstallFiles", "tmp2"), "w")
    if dir != "":
        curr_dir = os.getcwd()
        os.chdir(dir)
    if not out:
        out = tmp_file
    if not err:
        err = tmp2_file
    subprocess.call(arr, stdout=out, stderr=err)
    if dir != "":
        os.chdir(curr_dir)
    tmp_file.close()
    tmp2_file.close()

# Get temporary data.
def get_tmp_data(read_mode):
    tmp_file = open(os.path.join("InstallFiles", "tmp"), read_mode)
    data = tmp_file.read()
    tmp_file.close()
    return data

# Get temporary 2 data.
def get_tmp2_data(read_mode):
    tmp_file = open(os.path.join("InstallFiles", "tmp2"), read_mode)
    data = tmp_file.read()
    tmp_file.close()
    return data

# Get the absolute directory of a path.
def get_abs_dir(path):
    call_program("cmd.exe /C cd", path)
    return get_tmp_data("r").strip()

# Get a user prompt.
def user_prompt(prompt):
    print(prompt + ": ", end = "")
    return input()

# Get user yes or no prompt.
def user_yn_prompt(prompt):
    print(prompt + " (y/n): ", end="")
    user_in = input()
    if user_in == "Y" or user_in == "y":
        return True
    return False

# Prompt the user with options.
def user_options_prompt(prompt, options):
    print(prompt)
    op_num = 1
    for option in options:
        print("  " + str(op_num) + ". " + option)
        op_num += 1
    print("Selection: ", end="")
    user_in = input()
    if user_in.isnumeric():
        num = int(user_in)
        if num < 1 or num > len(options):
            print("ERR: Invalid selection.")
            return -1
        else:
            return num
    print("ERR: Invalid selection.")
    return -1

# Warn the user of something dangerous.
def user_warn():
    print("WARNING: The task you want to do can be potentially destructive if you don't know what you are doing!")
    print("Continue anyways? (Type \"YES\" to continue): ", end="")
    return input() == "YES"

# Download a zip file and extract a subdirectory from it into a folder.
def download_zip(url, subdir, dest):
    filehandle, _ = urllib.request.urlretrieve(url)
    zip = zipfile.ZipFile(filehandle, 'r')
    os.mkdir(dest)
    for zip_info in zip.infolist():
        if zip_info.filename.startswith(subdir):
            prefix = len(subdir) + 1
            if prefix == 1:
                prefix = 0
            zip_info.filename = zip_info.filename[prefix:]
            if zip_info.filename != "":
                #pathlib.Path(os.path.join(dest, zip_info.filename)).mkdir(parents=True, exist_ok=True)
                zip.extract(zip_info, dest)
    zip.close()

# If all the tools are installed.
def tools_check():
    if not os.path.exists(os.path.join("InstallFiles", "toolsInstalled")):
        print("ERR: Tools are not installed! You should run \"toolsInstall.py\" first.")
        exit(0)

# Get the name of the ROM.
def get_rom_name():
    if os.path.exists("romName.txt"):
        file = open("romName.txt", "r")
        name = file.read()
        file.close()
        return name
    return "DummyNameThatNoOneWouldEverReasonablyUse"

# If to autostart ROM after build
def get_rom_autostart():
    return os.path.exists(os.path.join("InstallFiles", "autoBoot"))

# Run fireflower.
def run_fireflower():
    tools_check()
    curr_dir = os.getcwd()
    os.chdir(os.path.join("ASM", "toolchain", "Fireflower"))
    program = "fireflower.exe"
    if os.name != 'nt':
        program = "wine " + program     # Non-Windows OS use WINE.
    p = subprocess.Popen(program, shell=True, stdout=subprocess.PIPE)
    ovs = []
    while True:
        inline = p.stdout.readline().decode('utf-8')
        if not inline:
            break
        if "Saving overlay ov9_" in inline:
            ovs.append(int(inline.split("ov9_")[1].split(" ")[0]))
        sys.stdout.write(inline)
        sys.stdout.flush()
    os.chdir(curr_dir)
    return ovs

# Run ndst.
def run_ndst(args):
    tools_check()
    if sys.platform == "linux" or sys.platform == "linux2":
        linux_path = os.path.join("Editor", "Ndst-Lin.elf")
        if not os.path.exists(linux_path):
            print("Downloading Ndst for Linux...")
            download = urllib.request.urlretrieve("https://github.com/Gota7/Ndst/releases/download/3.2/Ndst", linux_path)
            os.system("chmod +x " + linux_path)
        call_program_nowine("./Ndst-Lin.elf " + args, "Editor")
    else:
        call_program("Ndst.exe " + args, "Editor")