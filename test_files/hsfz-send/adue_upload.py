#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2012 BMW Car IT GmbH
#
"""Upload an ADü object"""

import argparse
import os.path
import struct
import subprocess
import sys

SENDHSFZ_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "sendhsfz.py"
)


def sendhsfz(server, ecu, udsdata):
    """Send the UDS request and return the result"""

    process = subprocess.Popen(
        [
            sys.executable,
            SENDHSFZ_SCRIPT_PATH,
            "--server",
            server,
            "--ecu",
            str(ecu)
        ]
        + ["%02X" % x for x in udsdata],
        stdout=subprocess.PIPE
    )
    (stdout_data, _) = process.communicate()
    exit_code = process.wait()

    if exit_code != 0:
        sys.exit(-2)

    try:
        return [int(x, 16) for x in stdout_data.split()]
    except:  # pylint: disable=bare-except
        print("Invalid data received", file=sys.stderr)
        print(stdout_data, file=sys.stderr)
        sys.exit(-3)


def get_object_info(server, ecu, mid):  # pylint: disable=too-many-locals
    """Retrieve the data related to the object"""

    # ADÜ_2771, list MID
    list_mid = sendhsfz(
        server,
        ecu,
        [
            0x31,
            0x01,
            mid[0],
            mid[1],
            0x02,
            len(mid),
        ]
        + mid
    )

    if len(list_mid) < 16 or list_mid[0] != 0x71:
        print("Invalid object info response ({})".format(
            list_mid), file=sys.stderr)
        sys.exit(-9)

    list_header = list_mid[:16]
    list_data = list_mid[16:]

    _, _, _, _, _, predown, postdown, _, _, _, format_id \
        = struct.unpack(">BBHBBHHHHBB", bytes(list_header))

    memory_size = (format_id >> 4) & 0xF
    mid_size = format_id & 0xF

    if len(list_data) < mid_size+memory_size:
        print("Invalid object info response ({})".format(
            list_mid), file=sys.stderr)
        sys.exit(-10)

    mid_received = list_data[:mid_size]
    size_data = list_data[mid_size:mid_size+memory_size]
    specific_data = list_data[mid_size+memory_size:]

    if mid_received != mid:
        print("MID mismatch ({})".format(mid_received), file=sys.stderr)
        sys.exit(-4)

    mobj_size = 0
    for size_byte in size_data:
        mobj_size = (mobj_size << 8) + size_byte

    return predown, postdown, specific_data


def do_processing(server, ecu, mid, specific_data, processing_type):
    """Execute the preprocessing function"""

    # ADÜ_2773
    result = sendhsfz(
        server,
        ecu,
        [
            0x31,
            0x01,
            0x70,
            0x00,
            processing_type,
            len(mid),
        ]
        + mid
        + specific_data
    )

    if result != [0x71, 0x01, 0x70, 0x00, 0x01]:
        print("Processing {} of MID {} returned {}".format(
            processing_type, mid, result), file=sys.stderr)
        sys.exit(-12)


def upload_file(server, ecu, mid, data):  # pylint: disable=too-many-locals
    """Upload the given data into the given memory object"""

    # ADÜ_3818, switch to extended session

    sendhsfz(server, ecu, [0x10, 0x03])

    # Retrieve the object info

    predown, postdown, specific_data = get_object_info(server, ecu, mid)

    # Call the preprocessing

    if predown != 0xFFFF:
        # ADÜ_2927
        do_processing(server, ecu, mid, specific_data, 0x03)

    # ADÜ_2931, perform the download

    mobj_size = len(data)

    result = sendhsfz(
        server,
        ecu,
        [
            0x34,
            0x00,
            0x40 + len(mid)
        ]
        + mid
        + [
            (mobj_size >> 24) & 0xFF,
            (mobj_size >> 16) & 0xFF,
            (mobj_size >> 8) & 0xFF,
            mobj_size & 0xFF
        ]
    )

    if result[0] != 0x74:
        print("RequestDownload of MID {} returned {}".format(
            mid, result), file=sys.stderr)
        sys.exit(-12)

    format_id = result[1]
    memory_size = format_id >> 4

    if (format_id & 0xF) != 0 or memory_size + 2 != len(result):
        print("UploadRequest of MID {} returned {}".format(
            mid, result), file=sys.stderr)
        sys.exit(-13)

    max_request_size = 0
    for size_byte in result[2:]:
        max_request_size = (max_request_size << 8) + size_byte

    # ADÜ_2947, perform transfer

    transfer_counter = 1
    transfer_cursor = 0

    while transfer_cursor < mobj_size:

        transfer_size = min(max_request_size - 2, mobj_size - transfer_cursor)

        result = sendhsfz(
            server,
            ecu,
            [
                0x36,
                transfer_counter & 0xFF
            ]
            + data[transfer_cursor:transfer_cursor+transfer_size]
        )

        if len(result) != 2 or result[0] != 0x76 or result[1] != transfer_counter & 0xFF:
            print("TransferData of MID {} returned {}".format(
                mid, result), file=sys.stderr)
            sys.exit(-14)

        transfer_counter += 1
        transfer_cursor += transfer_size

    # ADÜ_2957, transfer exit

    result = sendhsfz(
        server,
        ecu,
        [
            0x37
        ]
    )

    if len(result) != 1 or result[0] != 0x77:
        print("RequestTransferExit of MID {} returned {}".format(
            mid, result), file=sys.stderr)
        sys.exit(-15)

    # Call the postprocessing

    if postdown != 0xFFFF:
        # ADÜ_2927
        do_processing(server, ecu, mid, specific_data, 0x04)


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Upload an ADÜ object")

    parser.add_argument(
        "--server",
        help="Address of the HsFz server",
        required=False,
        default="127.0.0.1",
        type=str)

    parser.add_argument(
        "--ecu",
        help="Diagnostic address of the ECU",
        required=False,
        default=0x83,
        type=int)

    parser.add_argument(
        "--input-file",
        help="File with the data to upload",
        required=True,
        type=lambda x: os.path.abspath(x) if os.path.exists(x) else parser.
        error("File \"{}\" doesn't exist".format(x)))

    parser.add_argument(
        'MID',
        help="Memory object identifier",
        nargs="+",
        type=lambda x: int(x, 16) if len(x) <= 2 and x[0] != '-' else int("BAD" + x, 16))

    args = parser.parse_args()

    try:
        with open(args.input_file, "rb") as input_file:
            file_content = input_file.read()

    except OSError as excpt:
        print("Cannot read {} due to errno {}".format(
            args.input_file, excpt.errno), file=sys.stderr)
        sys.exit(-1)

    upload_file(args.server, args.ecu, args.MID, list(file_content))

    sys.exit(0)


if __name__ == "__main__":
    main()
