import os
import copy
from pmiyc.constants import *
import regex as re


def extract_multiple_tags(response, interest_tags):
    """
    Extracts multiple tags from a response
    :param response:
    :param interest_tags:
    :return:
    """
    return [get_tag_contents(response, tag) for tag in interest_tags]


def get_tag_contents(response, interest_tag):
    if interest_tag not in response:
        return response
    start_index, end_index, length = get_tag_indices(response, interest_tag)
    contents = (
        response[start_index + length : end_index].lstrip(" ").rstrip(" ")
    )
    return copy.deepcopy(contents)


def get_tag_indices(response, interest_tag):
    start_index = response.find(f"<{interest_tag}>")
    end_index = response.find(f"</{interest_tag}>")
    return start_index, end_index, len(f"<{interest_tag}>")


def from_name_and_tag_to_message(name, tag):
    return f"<{tag}> {name} </{tag}>"


def text_to_dict(s):
    return {k: int(v) for k, v in (item.split(": ") for item in s.split(", "))}


def get_next_filename(prefix, folder="."):
    prefix = prefix + "_"
    if not os.path.exists(folder):
        return prefix[:-1]
    # List all files with the given prefix in the current directory
    files = [file for file in os.listdir(folder) if file.startswith(prefix)]

    # Extract the numeric part of the file names and find the maximum
    numbers = [
        int(file[len(prefix) :])
        for file in files
        if file[len(prefix) :].isdigit()
    ]

    # Determine the next integer in the sequence
    next_number = max(numbers, default=0) + 1

    # Generate the next file name
    next_filename = f"{prefix}{next_number}"

    return next_filename

def support_to_int(support):
    support = support.strip().lower()
    # using regex match each string to a number
    for key, value in SUPPORT.items():
        if re.match(key, support):
            return value
    
    return None

def advanced_parse(response, expected_keys):
    retval = {}
    for key in expected_keys:
        # Create a regex to match <key>value</key> or <key>value
        pattern = fr"<{key}>(.*?)</{key}>|<{key}>(.*)"
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            # Use group 1 if the closing tag exists, otherwise use group 2
            value = match.group(1) or match.group(2).split("<")[0]
            retval[key] = value.strip()  # Remove leading/trailing whitespace
    
    if len(retval) == 0:
        return None
    
    return retval


def get_response_str(response, visible_ranks=True):
    response_str = ""
    if response and isinstance(response, dict):
        for k, v in response.items():
            if k == RANKING_TAG and not visible_ranks:
                continue
            if k == RANKING_TAG_INT:
                continue
            response_str += f"<{k}> {v} </{k}>\n"

    return response_str
