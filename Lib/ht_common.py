import pathlib
from re import sub
import urllib.request
import os
import subprocess
import zipfile

# For calling an external program.
def call_program(program: str):
    if os.name != 'nt':
        program = "wine " + program         # Non windows OS use wine.
    arr = program.split(' ')
    tmp_file = open("InstallFiles/tmp", "w")
    subprocess.call(arr, stdout=tmp_file)
    tmp_file.close()

# Get temporary data.
def get_tmp_data(read_mode):
    tmp_file = open("InstallFiles/tmp", read_mode)
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
            zip_info.filename = zip_info.filename[len(subdir)+1:]
            if zip_info.filename != "":
                #pathlib.Path(os.path.join(dest, zip_info.filename)).mkdir(parents=True, exist_ok=True)
                zip.extract(zip_info, dest)
    zip.close()