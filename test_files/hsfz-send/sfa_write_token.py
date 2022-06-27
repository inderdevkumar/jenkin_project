#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2020 BMW Car IT GmbH
#
"""Write a SFA token"""

import argparse
import os.path
import struct
import subprocess
import sys

SENDHSFZ_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "sendhsfz.py"
)

FIX_HEADER_SIZE = 26
LINK_SIZE = {1: 17, 2: 16, 3: 33}
TIME_STAMP_SIZE = 8
FEATURE_ID_SIZE = 3


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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (stdout_data, stderr_data) = process.communicate()
    exit_code = process.wait()

    if exit_code != 0:
        print("{} failed".format(SENDHSFZ_SCRIPT_PATH))
        print("RETURN: {}".format(exit_code), file=sys.stderr)
        print("STDOUT:\n{}".format(stdout_data), file=sys.stderr)
        print("STDERR:\n{}".format(stderr_data), file=sys.stderr)
        sys.exit(-2)

    try:
        return [int(x, 16) for x in stdout_data.split()]
    except:  # pylint: disable=bare-except
        print("Invalid UDS data received", file=sys.stderr)
        print(stdout_data, file=sys.stderr)
        sys.exit(-3)


def extract_token_and_feature_id(hexdata):
    """Parse the SFA token to retrieve the fields"""
    data = [int(hexdata[i:i+2], 16) for i in range(0, len(hexdata), 2)]
    length, version, offset, _, link_type \
        = struct.unpack(">IBI16sB", bytes(data[0:FIX_HEADER_SIZE]))
    if version != 1:
        raise ValueError("Unsupported token version {}".format(version))
    if link_type not in LINK_SIZE:
        raise ValueError("Unsupported link type {}".format(link_type))
    if offset > length:
        raise ValueError("Invalid signature offset {} (max {})".format(
            offset, length))
    feature_offset = FIX_HEADER_SIZE + LINK_SIZE[link_type] + TIME_STAMP_SIZE
    if feature_offset + FEATURE_ID_SIZE > length or length > len(data):
        raise ValueError("Invalid token length {}".format(length))
    return (
        data[:length],
        data[length:],
        data[feature_offset:feature_offset+FEATURE_ID_SIZE]
    )


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Send a SFA token")

    parser.add_argument(
        "--ip-addr",
        help="IP address of the test bench",
        required=False,
        default="160.48.199.99",
        type=str)

    parser.add_argument(
        "--diag-addr",
        help="Diagnostic address of the ECU (prefixed by 0x for an hexadecimal value)",
        required=False,
        default=0x63,
        type=lambda x: int(x, 0))

    parser.add_argument(
        "--stk-file",
        help="SFA token to upload",
        required=True,
        type=lambda x: os.path.abspath(x) if os.path.exists(x) else parser.
        error("File \"{}\" doesn't exist".format(x)))

    args = parser.parse_args()

    try:
        with open(args.stk_file, "r") as input_file:
            # file contains the token data and the signing certificate
            file_data = input_file.read()
    except OSError as exception:
        print("Cannot read {} due to errno {}".format(
            args.input_file, exception.errno), file=sys.stderr)
        sys.exit(-1)

    try:
        token_data, signing_certificate, feature_id = \
            extract_token_and_feature_id(file_data)
    except Exception as exception:  # pylint: disable=broad-except
        print("Failed to parse SFA token due to {}".format(
            exception), file=sys.stderr)
        sys.exit(-1)

    print("Write {} bytes token for feature {} to {}/{}".format(
        len(token_data),
        "".join("%02X" % x for x in feature_id),
        args.ip_addr,
        args.diag_addr
    ))

    write_token_uds_message = [0x31, 0x01, 0x0F, 0x2A]
    write_token_uds_message += feature_id
    write_token_uds_message += [0x01] if signing_certificate else [0x00]
    write_token_uds_message += token_data
    write_token_uds_message += signing_certificate

    uds_response = sendhsfz(args.ip_addr, args.diag_addr,
                            write_token_uds_message)

    if uds_response != [0x71, 0x01, 0x0F, 0x2A]:
        print("Token rejected with UDS response {}".format(
            " ".join("%02X" % x for x in uds_response)), file=sys.stderr)
        sys.exit(-1)
    else:
        print("Token installed")
        sys.exit(0)


if __name__ == "__main__":
    main()
