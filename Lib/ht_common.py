import pathlib
from re import sub
import urllib.request
import os
import subprocess
import zipfile

# For calling an external program.
def call_program(program, dir = ""):
    if os.name != 'nt':
        program = "wine " + program         # Non windows OS use wine.
    arr = program.split(' ')
    tmp_file = open(os.path.join("InstallFiles", "tmp"), "w")
    if dir != "":
        curr_dir = os.path.curdir
        os.chdir(dir)
    subprocess.call(arr, stdout=tmp_file)
    if dir != "":
        os.chdir(curr_dir)
    tmp_file.close()

# Get temporary data.
def get_tmp_data(read_mode):
    tmp_file = open(os.path.join("InstallFiles", "tmp"), read_mode)
    data = tmp_file.read()
    tmp_file.close()
    return data

# Get user yes or no prompt
def user_yn_prompt(prompt):
    print(prompt + " (y/n): ", end="")
    user_in = input()
    if user_in == "Y" or user_in == "y":
        return True
    return False

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
        raise Exception("ERR: Tools are not installed!")
    else:
        print("Checking for tools installation... OK")

# Run fireflower.
def run_fireflower():
    tools_check()
    call_program("fireflower.exe", os.path.join("Tools", "Fireflower"))