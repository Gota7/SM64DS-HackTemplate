import Lib.ht_common as ht_common
import os

def xdelta_make_patch(src_file, dest_file, patch_out):
    ht_common.call_program(os.path.join("InstallFiles", "xdelta.exe") + " -e -s " + src_file + " " + dest_file + " " + patch_out)

def xdelta_apply_patch(src_file, patch_file, dest_out):
    ht_common.call_program(os.path.join("InstallFiles", "xdelta.exe") + " -d -s " + src_file + " " + patch_file + " " + dest_out)