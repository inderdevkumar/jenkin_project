#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2012 BMW Car IT GmbH
#
"""Create an optimized binary container from a list of files"""

import argparse
import re
import struct
import sys


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Extract an optimized binary container")

    parser.add_argument(
        "--output-file",
        help="File that will contain the container",
        required=False,
        type=str)

    parser.add_argument(
        "--ecu-uid",
        help="ECU-UID",
        required=False,
        default="000102030405060708090A0B0C0D0EEE",
        type=str)

    parser.add_argument(
        'file',
        help="Input files",
        nargs="+",
        type=str)

    args = parser.parse_args()
    files_contents = bytes()

    for file_name in args.file:
        try:
            groups = re.compile("^(.+)//([0-9a-fA-F]{2})$").match(file_name)
            if groups:
                file_path = groups.group(1)
                file_type = int(groups.group(2), 16)
            else:
                file_path = file_name
                file_type = 0x01  # Certificate

            with open(file_path, "rb") as input_file:
                file_content = input_file.read()

            if len(file_content) > 0xFFFF:
                print("File {} is too large ({} bytes)".format(
                    file_path, len(file_content)), file=sys.stderr)
                sys.exit(-2)

            files_contents += \
                struct.pack(">BBH", file_type, 0, len(file_content)) \
                + file_content

        except OSError as excpt:
            print("Cannot read {} due to errno {}".format(
                file_name, excpt.errno), file=sys.stderr)
            sys.exit(-1)

    if args.output_file:
        try:
            with open(args.output_file, "wb") as output_file:
                output_file.write(struct.pack(
                    ">BBH", 1, 0, 16 + len(files_contents)))
                output_file.write(
                    bytes([int(args.ecu_uid[i*2:i*2+2], 16) for i in range(16)]))
                output_file.write(files_contents)
        except OSError as excpt:
            print("Cannot create output file due to errno {}".format(
                excpt.errno), file=sys.stderr)
            sys.exit(-3)
        except ValueError as excpt:
            print("Invalid ECU-UID {}".format(args.ecu_uid), file=sys.stderr)
            sys.exit(-4)
        except:  # pylint: disable=bare-except
            print("Cannot create output file", file=sys.stderr)
            sys.exit(-5)


if __name__ == "__main__":
    main()
