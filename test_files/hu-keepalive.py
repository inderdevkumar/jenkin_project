#!/usr/bin/env python
#
# Send UDP multicast packets.
# Requires that your OS kernel supports IP multicast.
#

import time
import struct
import socket
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()


MYPORT = 30500
MYGROUP_4 = '239.192.255.1'
MYTTL = 1  # Increase to reach other networks


def main():
    sender(MYGROUP_4)


def sender(group):
    addrinfo = socket.getaddrinfo(group, None)[0]

    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', MYTTL)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)

    while True:
        data = b'\x40\x10\x00\x40\x00\x01\x97\x03'
        sock.sendto(data, (addrinfo[4][0], MYPORT))
        logger.info("Keep-alive broadcasted to %s port %d", addrinfo[4][0], MYPORT)
        time.sleep(0.64)


if __name__ == '__main__':
    main()
