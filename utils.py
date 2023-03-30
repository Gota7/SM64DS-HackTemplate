import json
import pathlib
import collections.abc

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

