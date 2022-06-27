#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,bare-except,too-many-branches
#
# @file
# @copyright Copyright (C) 2019 BMW Car IT GmbH
#
"""Tool used for sending a UDS message via HsFz and printing the response"""

import argparse
import socket
import struct
import sys

TESTER_TOOL_ADDRESS = 0xF4
CONTROL_DIAGNOSIS = 0x01
CONTROL_ACK = 0x02
INCORRECT_TESTER_ADDRESS = 0x40
SID_NRC = 0x7F
NRC_PENDING = 0x78
NRC_MSG_LEN = 3
NRC_MSG_NRC_POS = 2
HSFZ_HEADER_LEN = 6
DIAGNOSIS_HEADER_LEN = 2


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Send a UDS message via HsFz")

    parser.add_argument(
        "--server",
        help="Address of the HsFz server",
        required=False,
        type=str)

    parser.add_argument(
        "--ecu",
        help="Diagnostic address of the ECU",
        required=False,
        default=0x83,
        type=int)

    parser.add_argument(
        'UDS',
        help="UDS data",
        nargs="+",
        type=lambda x: int(x, 16) if len(x) <= 2 and x[0] != '-' else int("BAD" + x, 16))

    args = parser.parse_args()

    if args.server:
        target = args.server.strip().rsplit(":", 1)

        if len(target) == 2:
            target_name = target[0]
            target_port = target[1]
        else:
            target_name = target[0]
            target_port = 6801
    else:
        target_name = "127.0.0.1"
        target_port = 6801

    try:
        target_addr = socket.gethostbyname(target_name)
    except:
        print("Cannot resolve \"{}\"".format(target_name), file=sys.stderr)
        sys.exit(-1)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((target_addr, target_port))
    except:
        print("Cannot connect to {}:{}".format(
            target_addr, target_port), file=sys.stderr)
        sys.exit(-1)

    # Send the HsFz request
    # length: 4 bytes (length and control not included)
    # control: 2 bytes, 1 -> diagnosis
    # src address: 1 byte, 0xF4 -> tester tool
    # dst address: 1 byte
    # UDS data

    server.send(
        struct.pack(
            ">IH",
            len(args.UDS) + DIAGNOSIS_HEADER_LEN,
            CONTROL_DIAGNOSIS
        )
        + bytes([TESTER_TOOL_ADDRESS, args.ecu])
        + bytes(args.UDS)
    )

    # Parse the responses

    data_buffer = bytes()
    response_found = False

    while server:
        # Load received data
        data_buffer = data_buffer + server.recv(512)

        # Each message is prefixed by length and control (see above)
        while len(data_buffer) >= HSFZ_HEADER_LEN:
            length, control = struct.unpack(
                ">IH", data_buffer[:HSFZ_HEADER_LEN])

            # Wait until the message is complete
            if length + HSFZ_HEADER_LEN > len(data_buffer):
                break

            # Extract the payload of the HsFz message
            if length > 0:
                payload = data_buffer[HSFZ_HEADER_LEN:HSFZ_HEADER_LEN+length]
            else:
                payload = bytes()

            # Update the data buffer by remove the current message
            data_buffer = data_buffer[HSFZ_HEADER_LEN+length:]

            # Handle the message
            if control == CONTROL_DIAGNOSIS:
                # If message is a diagnosis message and not a pending

                if len(payload) != (DIAGNOSIS_HEADER_LEN + NRC_MSG_LEN) \
                        or payload[DIAGNOSIS_HEADER_LEN] != SID_NRC \
                        or payload[DIAGNOSIS_HEADER_LEN+NRC_MSG_NRC_POS] != NRC_PENDING:
                    print(" ".join("%02X" %
                                   x for x in payload[DIAGNOSIS_HEADER_LEN:]))
                    server.close()
                    server = None
                    response_found = True

            elif control == INCORRECT_TESTER_ADDRESS:
                print("Address 0x{:02X} already used".format(TESTER_TOOL_ADDRESS),
                      file=sys.stderr)
                server.close()
                server = None

            elif control != CONTROL_ACK:
                print("Unexpected HsFz response code 0x{:04X}".format(control),
                      file=sys.stderr)
                server.close()
                server = None

    sys.exit(0 if response_found else -1)


if __name__ == "__main__":
    main()
