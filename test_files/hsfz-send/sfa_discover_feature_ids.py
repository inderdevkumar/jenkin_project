#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2020 BMW Car IT GmbH
#
"""List SFA features"""

import argparse
import os.path
import subprocess
import sys

SENDHSFZ_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "sendhsfz.py"
)

DISCOVER_RSP_HEADER_SIZE = 7
DISCOVER_RSP_ENTRY_SIZE = 5
FEATURE_IDS = {
    0x000000: "Plant Mode",
    0x000001: "Engineering Mode",
    0x00151D: "IPSec Link Deactivation",
    0x001D1A: "Internal Debug Access and DLT external tracing",
    0x001D1D: "DLT internal tracing",
    0x009C9C: "KDS: Client re-pairing",
    0x00AAFC: "KDS: Audit (Operation) Mode",
    0x00DC9D: "KDS: Delete client pairing",
    0x010001: "Test Feature ID",
    0x01D2FD: "Deaktivierung zentraler Fehlerspeicher Diagnosemaster",
    0x204348: "MGU22 Speech",
    0x414154: "AndroidAuto",
    0x414350: "CarPlay",
    0x4D4150: "Navigation Map",
    0x4E4152: "MGU22 Navigation Application RoW",
    0x4E4141: "MGU22 Navigation Application Asia",
    0x53DA52: "SDARS SXM"
}
FEATURE_STATUS = {
    0: "No secure token received",
    1: "Enabled",
    2: "Disabled",
    3: "Expired"
}
FEATURE_VALIDATION = {
    0x00: "OK",
    0x01: "UNCHECKED",
    0x02: "MALFORMED",
    0x03: "EMPTY",
    0x04: "ERROR",
    0x05: "SECURITY_ERROR",
    0x06: "WRONG_LINKTOID",
    0x07: "CHECK_RUNNING",
    0x08: "TIMESTAMP_TOO_OLD",
    0x09: "VERSION_NOT_SUPPORTED",
    0x0A: "FEATURE_ID_NOT_SUPPORTED",
    0x0B: "UNKNOWN_LINKTYPE",
    0xFF: "OTHER"
}


def to_string(value, dictionary):
    """Convert a value into a string"""

    if value in dictionary:
        return "{}(0x{:X})".format(dictionary[value], value)

    return "{value}(0x{value:X})".format(value=value)


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
        description="Discover SFA feature IDs")

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

    uds_response = sendhsfz(args.ip_addr, args.diag_addr,
                            [0x31, 0x01, 0x0F, 0x28, 0x00])

    response_is_ok = True

    if len(uds_response) < DISCOVER_RSP_HEADER_SIZE:
        response_is_ok = False
    else:
        nb_features_ids = uds_response[4] * 65536 + \
            uds_response[5] * 256 + uds_response[6]

    if response_is_ok and uds_response[:4] != [0x71, 0x01, 0x0F, 0x28]:
        response_is_ok = False

    if response_is_ok \
            and (DISCOVER_RSP_HEADER_SIZE + nb_features_ids * DISCOVER_RSP_ENTRY_SIZE) \
            != len(uds_response):
        response_is_ok = False

    if not response_is_ok:
        print("Invalid UDS response {}".format(
            " ".join("%02X" % x for x in uds_response)), file=sys.stderr)
        sys.exit(-1)

    for i in range(DISCOVER_RSP_HEADER_SIZE, len(uds_response), DISCOVER_RSP_ENTRY_SIZE):
        feature_id = uds_response[i] * 65536 + \
            uds_response[i+1] * 256 + uds_response[i+2]
        status = uds_response[i+3]
        validation = uds_response[i+4]
        print("Feature: {}\n    Status: {}\n    Validation status: {}".format(
            to_string(feature_id, FEATURE_IDS),
            to_string(status, FEATURE_STATUS),
            to_string(validation, FEATURE_VALIDATION)
        ))
    sys.exit(0)


if __name__ == "__main__":
    main()
