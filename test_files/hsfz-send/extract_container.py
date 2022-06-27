#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2012 BMW Car IT GmbH
#
"""Extract an optimized binary container"""

import argparse
import os
import os.path
import struct
import sys


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Extract an optimized binary container")

    parser.add_argument(
        'file',
        help="Container file",
        nargs=1,
        type=lambda x: os.path.abspath(x) if os.path.exists(x) else parser.
        error("File \"{}\" doesn't exist".format(x)))

    args = parser.parse_args()

    try:
        with open(args.file[0], "rb") as input_file:
            file_content = input_file.read()
    except OSError as excpt:
        print("Cannot read {} to errno {}".format(
            args.file, excpt.errno), file=sys.stderr)
        sys.exit(-1)

    if len(file_content) < 20:
        print("Input file is too small", file=sys.stderr)
        sys.exit(-2)

    version, _, length = struct.unpack(">BBH", file_content[:4])
    print("Version {} Length {} bytes ECU-ID {}".format(
        version,
        length,
        "".join(("%02X" % x) for x in file_content[4:20])
    ))

    if length + 4 != len(file_content):
        print("Invalid length", file=sys.stderr)
        sys.exit(-3)

    entries_data = file_content[20:]
    entry_index = 1

    while entries_data:
        entry_type, _, entry_length = struct.unpack(">BBH", entries_data[:4])
        if entry_type == 0x00:
            file_name = "CSR_{:02}.der".format(entry_index)
        elif entry_type == 0x01:
            file_name = "Certificate_{:02}.der".format(entry_index)
        elif entry_type == 0x02:
            file_name = "Chain_{:02}.der".format(entry_index)
        else:
            file_name = "Entry_Type{:02X}_{:02}.bin".format(
                entry_type, entry_index)
        print("Extract {}".format(file_name))

        try:
            with open(file_name, "wb") as output_file:
                output_file.write(entries_data[4:4+entry_length])
        except OSError as excpt:
            print("Cannot create output file due to errno {}".format(
                excpt.errno), file=sys.stderr)
            sys.exit(-4)
        except:  # pylint: disable=bare-except
            print("Cannot create output file", file=sys.stderr)
            sys.exit(-5)

        entries_data = entries_data[4+entry_length:]
        entry_index += 1


if __name__ == "__main__":
    main()
