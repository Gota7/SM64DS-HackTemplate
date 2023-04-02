import json
import pathlib
import collections.abc
import os
import shutil
import fnmatch


error_template = "The library definition at index {index} does not have the '{field}' field. "


def load_libraries_definition(filename: str):
    path = pathlib.Path(filename)
    if not path.exists() or not path.is_file():
        raise Exception(f"Something went wrong while loading libraries definitions from the file {filename}: does not exist or is not a file.")

    with open(path, 'r') as file:
        content: str = file.read()
        parsed_content = json.loads(content)
        if not isinstance(parsed_content, collections.abc.Sequence):
            raise Exception(f"The file {filename} is not a json array, therefore cannot be used as libraries definition.")

        for index, library in enumerate(parsed_content):
            # Ensure all the required field are in the definition
            for field in ['type', 'id_name', 'files']:
                if field not in library:
                    raise Exception(error_template.format(index=index, field=field))

            if library['type'] == 'overlay' and 'code_addr' not in library:
                raise Exception(error_template.format(index=index, field='code_addr') + "It is required when the type is 'overlay'")

            # We check that every files in the 'files' array exist
            files = library['files']
            # Ensure it is an array
            if not isinstance(files, collections.abc.Sequence):
                Exception(f"The 'files' field is not a json array. Therefore is invalid.")

            parent = path.parent
            for file in files:
                children = parent.joinpath(file)
                if not children.exists() or not children.is_file():
                    raise Exception(f"The files definition '{children}' does not exist or is not a file.")
        return parsed_content


def copy_with_ignore(source_folder, destination_folder):
    """
    Copy files and directories from source folder to destination folder,
    ignoring any paths specified in a .ignore file in the source folder.
    """
    # Load ignore patterns from .ignore file
    ignore_patterns = []
    ignore_file = os.path.join(source_folder, ".ignore")
    if os.path.exists(ignore_file):
        with open(ignore_file, "r") as f:
            ignore_patterns = [line.strip() for line in f.readlines() if
                               line.strip() and not line.strip().startswith('#')]

    print("ignore_patterns", ignore_patterns)

    # Walk through the source folder, copying files and directories
    for root, dirs, files in os.walk(source_folder):
        # Check if current directory should be ignored
        relative_path = os.path.relpath(root, source_folder)
        if any(pattern[-1] == "/" and relative_path.startswith(pattern[:-1]) for pattern in ignore_patterns):
            print("ignored", relative_path)
            continue

        # Create corresponding directory in destination folder
        dest_dir = os.path.join(destination_folder, relative_path)
        os.makedirs(dest_dir, exist_ok=True)

        # Copy non-ignored files to destination folder
        for filename in files:
            if any(fnmatch.fnmatchcase(filename, pattern) for pattern in ignore_patterns):
                continue

            if filename == ".ignore":
                continue

            source_file = os.path.join(root, filename)
            dest_file = os.path.join(dest_dir, filename)
            shutil.copy2(source_file, dest_file)