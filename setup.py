import Lib.ht_common as ht_common
import os
import shutil

# Extract a base ROM. TODO: CHECKSUMS!!!
def extract_base():
    if os.path.exists("Base"):
        print("WARNING: Base ROM folder already exists!")
        if not ht_common.user_warn():
            return
        shutil.rmtree("Base")
    ht_common.run_ndst("-e " + os.path.join("..", "Base.nds") + " " + os.path.join("..", "Conversions") + " " + os.path.join("..", "Base"))

# Main method.
if __name__ == "__main__":
    extract_base()