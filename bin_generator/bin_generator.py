import argparse
import ctypes
import hashlib
import json
import time
from os.path import exists

import jsonschema

SHA256_DIGEST_LENGTH = 32
HEADER_START_SIGNATURE = 0xcafef00d


class Header(ctypes.Structure):
    """
    ctype structure class for header structure
    """
    _fields_ = [("sig", ctypes.c_uint32),
                ("num_device", ctypes.c_uint8),
                ("hash_val", ctypes.c_uint8 * 32),
                ("timestamp", ctypes.c_uint64)]


class Entry(ctypes.Structure):
    """
    ctype structure class for entry structure
    """
    _fields_ = [("name", ctypes.c_char * 256),
                ("mac", ctypes.c_uint64, 48),
                ("maj_ver", ctypes.c_uint64, 8),
                ("min_ver", ctypes.c_uint64, 8)]


def load_json(json_path):
    """
    Loads JSON from the path specified.
    :parameter json_path: string that specifies input JSON with path
    :returns: parsed JSON dictionary
    :raises: exception in case if path or JSON is invalid
    """
    if not json_path or not exists(json_path):
        raise Exception("Invalid JSON path provided.")
    json_file = open(json_path, 'r')
    try:
        input_file = json.load(json_file)
    except json.decoder.JSONDecodeError:
        raise Exception("Error while loading JSON.")
    return input_file


def get_mac(mac_str):
    """
    Extract 48-byte MAC from mac-string specified in input
    :param mac_str: string that specifies mac address
    :return: 48 byte MAC computed from mac string and error string if any
    """
    mac_str = mac_str.replace(":", "")
    try:
        mac_val = int(mac_str, 16)
        return mac_val, "MAC is correct"
    except ValueError as e:
        return None, e.args[0]


def get_version(version_str):
    """
    Extracts major and minor version defined in device entry
    :param version_str: string that specifies fw version in X.Y format
    :return: major and minor version. None in case of error
    """
    versions = version_str.split('.')
    if len(versions) != 2:
        print(versions)
        return [None, None]
    return [int(versions[0], 16), int(versions[1], 16)]


def get_schema():
    """
    This function gets the schema for the json to be validated
    """
    try:
        with open('user_input_schema.json', 'r') as file:
            schema = json.load(file)
        return schema
    except FileNotFoundError:
        print("JSON schema is not present")
        return None


def validate_json(json_data):
    """
    This function validates parsed json data
    :param json_data: parsed JSON dictionary object
    :return: True if json is as per schema else False
    """
    user_schema = get_schema()
    try:
        jsonschema.validate(instance=json_data, schema=user_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    return True


def create_argument_parser():
    """
    This function creates agrparse object
    :return: argparse object with required flags added
    """
    # Construct the argument parser
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-in", "--input", required=True,
                    help="Input JSON file path")
    ap.add_argument("-out", "--output", required=False,
                    help="Output bin file path")
    return ap


def create_entries_data(input_json_data):
    """
    Creates entry binary stream from parsed json data
    :param input_json_data: parsed json data
    :return: binary stream of device entries
    """
    entry_bytes_array = bytearray()
    num_devices = 0
    for device in input_json_data["devices"]:
        entry = Entry()
        mac, message = get_mac(device["mac_address"])
        if mac:
            entry.mac = mac
        else:
            print("Error while parsing mac address - "+message)
            continue
        entry.name = bytes(device["name"], encoding='utf8')
        major_ver, minor_ver = get_version(device["fw_version"])
        if major_ver is not None and minor_ver is not None:
            entry.maj_ver = major_ver
            entry.min_ver = minor_ver
        else:
            print("Invalid fw_version entry for device: "+device["name"])
            continue
        entry_bytes_array += bytearray(entry)
        num_devices += 1
    return num_devices, entry_bytes_array


def create_header_data(num_devices, entry_data_bytes):
    """
    Creates entry binary stream from parsed json data
    :param num_devices: number of valid devices entry mentioned in input JSON
    :param entry_data_bytes: binary stream of device entries
    :return: binary stream of header
    """
    header = Header()
    header.sig = HEADER_START_SIGNATURE
    header.num_device = num_devices
    entry_hash = (hashlib.sha256(entry_data_bytes)).hexdigest()
    header.hash_val = (ctypes.c_uint8 * 32)(*[int(entry_hash[i:i+2], 16)\
                                              for i in range(0, SHA256_DIGEST_LENGTH * 2, 2)])
    header.timestamp = int(time.time())
    return bytearray(header)


def main():
    """
    main function
    :return: None
    """
    argument_parser = create_argument_parser()
    args = vars(argument_parser.parse_args())
    input_json = args["input"]
    output_bin = args["output"]

    try:
        input_data = load_json(input_json)
    except Exception as e:
        print("Exiting application due to Error: "+e.args[0])
        exit()

    if not validate_json(input_data):
        print("Exiting application due to Error: Invalid JSON data provided.")
        exit()

    device_count, entry_bytes = create_entries_data(input_data)
    header_bytes = create_header_data(device_count, entry_bytes)
    file_bytes = header_bytes + entry_bytes

    if output_bin is None:
        output_bin = "output.bin"
    with open(output_bin, "wb") as binary_file:
        binary_file.write(file_bytes)


if __name__ == '__main__':
    main()






