"""
Functions for dealing with file reading/writing and all other problems that arise from having
files that need to be read, moved, and otherwise interacted with.
"""

import os
import json


def parse_json(json_file_path):
    """
    Parses a JSON file and returns the object encoded in it and the bare name of the file

    :param str json_file_path: A relative or absolute path from the current directory to a file
        in JSON format
    :return: A tuple containing an object in JSON format and a string containing the name of
        the file the JSON object was drawn from with the path and .json removed
    :rtype: tuple
    """
    with open(json_file_path, 'r') as file_obj:
        raw_json = file_obj.read()
        json_obj = json.loads(raw_json)

    file_name = os.path.split(json_file_path)[1].replace('.json', '')
    return json_obj, file_name
