#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,bare-except,too-many-branches
#
# @file
# @copyright Copyright (C) 2020 BMW Car IT GmbH
#
"""Tool used for retrieving the IP addresses of the available test benches"""


import select
import socket
import sys
import time

ERRNO_ADDRESS_NOT_AVAILABLE = 99
HSFS_BROADCAST_ADDRESS = '169.254.255.255'
HSFZ_BROADCAST_PORT = 6811
HSFZ_LISTEN_PORT = 7811
HSFZ_VEHICLE_IDENTIFICATION_DATA = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x11])
UDP_PACKET_SIZE = 1500

USAGE_INFO = """List the available test benches, it will bind to the first AutoIP address
(169.254.x.x) on the host. This tool won't work with DHCP address allocation.
Press any key to stop it."""

# On Linux, listening on a broadcast address didn't give any results for
# several possible reasons. Linux routes only the broadcast messages from the
# interface that it selected during the binding. Then Linux is filtering out
# the broadcast messages if some configuration are applied. At last, there
# is a bug in Ubuntu which routes AutoIP messages to disabled interfaces.
# It wasn't possible to listen to the broadcast messages on Linux to retrieve
# the available test benches. This method should work with Windows.
# A better solution would be to list the interfaces, to retrieve the
# corresponding address and to bind to them. But with Python, it requires some
# hacks as SIOCGIFADDR isn't a defined symbol.

def list_test_benches():
    """List the test benches"""

    try:
        hsfz_broadcast = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        hsfz_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception as exception: # pylint: disable=broad-except
        print("Cannot create socket due to {}".format(
            exception), file=sys.stderr)
        sys.exit(-1)

    address_found = False

    print(USAGE_INFO)

    while True:
        for tested_addr in range(1, 65535):
            if (tested_addr % 100) == 1:
                rlist, _, _ = select.select([sys.stdin], [], [], 0)
                if rlist:
                    sys.exit(0)
            address = '169.254.{}.{}'.format(
                tested_addr // 256, tested_addr % 256)
            try:
                hsfz_broadcast.bind((address, HSFZ_LISTEN_PORT))
                address_found = True
                break
            except Exception as exception: # pylint: disable=broad-except
                print_exception = True
                for excep_arg in exception.args:
                    if isinstance(excep_arg, int):
                        if excep_arg == ERRNO_ADDRESS_NOT_AVAILABLE:
                            print_exception = False
                if print_exception:
                    print("Cannot bind to {} due to {}".format(
                        address,
                        exception
                    ), file=sys.stderr)
        if address_found:
            print("Local AutoIP {} found".format(address))
            break
        print("No AutoIP address found, retry...")
        time.sleep(1)

    while True:
        rlist, _, _ = select.select([sys.stdin, hsfz_broadcast], [], [], 1)
        for fd in rlist:
            if fd == sys.stdin:
                sys.exit(0)
            elif fd == hsfz_broadcast:
                try:
                    data, addr = hsfz_broadcast.recvfrom(UDP_PACKET_SIZE)
                except Exception as exception: # pylint: disable=broad-except
                    print("Failed to listen to port {} due to {}".format(
                        HSFZ_BROADCAST_PORT, exception), file=sys.stderr)
                    sys.exit(-1)
                print("{} -> {}".format(
                    addr[0],
                    "".join(
                        chr(x)
                        if 32 <= x <= 127 else "."
                        for x in data),
                    file=sys.stderr))
        if not rlist:
            try:
                hsfz_broadcast.sendto(
                    HSFZ_VEHICLE_IDENTIFICATION_DATA,
                    (HSFS_BROADCAST_ADDRESS, HSFZ_BROADCAST_PORT)
                )
            except:
                pass

    hsfz_broadcast.close()


if __name__ == "__main__":
    list_test_benches()
