#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2020 BMW Car IT GmbH
#
"""Read ECU UID"""

import argparse
import os.path
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


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Read ECU UID")

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

    args = parser.parse_args()

    uds_response = sendhsfz(args.ip_addr, args.diag_addr, [0x22, 0x80, 0x00])

    if len(uds_response) != 19 or uds_response[:3] != [0x62, 0x80, 0x00]:
        print("Invalid UDS response {}".format(
            " ".join("%02X" % x for x in uds_response)), file=sys.stderr)
        sys.exit(-1)

    print("ECU-UID: {}".format("".join("%02X" % x for x in uds_response[3:])))
    sys.exit(0)


if __name__ == "__main__":
    main()
