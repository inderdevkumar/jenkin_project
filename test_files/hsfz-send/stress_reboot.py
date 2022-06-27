#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @file
# @copyright Copyright (C) 2020 BMW Car IT GmbH
#
"""Stress the reboot"""

import argparse
import os.path
import subprocess
import sys
import time
import logging

TIMEOUT_DELAY = 30
REBOOT_DELAY = 5
PWF_STATE_SETTLE_DELAY = 3
SENDHSFZ_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "sendhsfz.py"
)

logging.basicConfig(filename="stress_reboot.log", level=logging.DEBUG)


def failure(message):
    """Stop the execution of the test"""
    logging.error(message)
    print(message, file=sys.stderr)
    sys.exit(-1)


def sendhsfz(server, ecu, udsdata):
    """Send the UDS request and return the result"""

    logging.info("sendhsfz %s", " ".join(["%02X" % x for x in udsdata]))

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

    logging.info("RESULT : %s", exit_code)
    logging.info("STDOUT : %s", stdout_data)
    logging.info("STDERR : %s", stderr_data)

    if exit_code != 0:
        return []

    try:
        return [int(x, 16) for x in stdout_data.split()]
    except:  # pylint: disable=bare-except
        failure("Invalid UDS data received\n{}".format(stdout_data))


def ecu_hard_reset(server, ecu):
    """Send the ECU reset and check the response"""
    logging.info("ecu_hard_reset %s/%02X", server, ecu)

    uds_response = sendhsfz(server, ecu, [0x11, 0x01])
    if uds_response != [0x51, 0x01]:
        failure("Invalid UDS response to ECU hard reset {}".format(
            " ".join("%02X" % x for x in uds_response)))


def ecu_get_ip_config(server, ecu):
    """Return the IP config"""
    logging.info("ecu_get_ip_config %s/%02X", server, ecu)

    uds_response = sendhsfz(server, ecu, [0x22, 0x17, 0x2A])
    if len(uds_response) != 16 or uds_response[:3] != [0x62, 0x17, 0x2A]:
        logging.info("Invalid response")
        return ""
    return "%d.%d.%d.%d" % tuple(uds_response[4:8])


def set_energy_mode_production(server):
    """Before to change the PWF state, the energy mode must be set to production"""
    logging.info("set_energy_mode_production %s", server)

    uds_response = sendhsfz(
        server, 0x10, [0x31, 0x01, 0x0F, 0x0C, 0x01])
    if uds_response != [0x71, 0x01, 0x0F, 0x0C]:
        failure("Invalid UDS response to energy mode production {}".format(
            " ".join("%02X" % x for x in uds_response)))    


def pwf_pruefen_analyse_diagnose(server):
    """Configure the diag gateway for PWF state PAD"""
    logging.info("pwf_pruefen_analyse_diagnose %s", server)

    uds_response = sendhsfz(
        server, 0x10, [0x31, 0x01, 0x10, 0x31, 0x07, 0x07, 0xD1])
    if uds_response != [0x71, 0x01, 0x10, 0x31]:
        failure("Invalid UDS response to PWF PAD {}".format(
            " ".join("%02X" % x for x in uds_response)))


def pwf_parken_bn_io(server):
    """Configure the diag gateway for PWF state PARKEN"""
    logging.info("pwf_parken_bn_io %s", server)

    uds_response = sendhsfz(
        server, 0x10, [0x31, 0x01, 0x10, 0x31, 0x02, 0x02, 0xD9])
    if uds_response != [0x71, 0x01, 0x10, 0x31]:
        failure("Invalid UDS response to PWF PARKEN {}".format(
            " ".join("%02X" % x for x in uds_response)))


def pwf_wohnen(server):
    """Configure the diag gateway for PWF state WOHNEN"""
    logging.info("pwf_wohnen %s", server)

    uds_response = sendhsfz(
        server, 0x10, [0x31, 0x01, 0x10, 0x31, 0x05, 0x05, 0x73])
    if uds_response != [0x71, 0x01, 0x10, 0x31]:
        failure("Invalid UDS response to PWF WOHNEN {}".format(
            " ".join("%02X" % x for x in uds_response)))


def wait_hsfz_availability(server, ecu):
    """Wait until the device response to the ping"""
    logging.info("wait_hsfz_availability %s/%02X", server, ecu)

    for i in range(TIMEOUT_DELAY):
        logging.info("Send ping #%d", i)
        ip_addr = ecu_get_ip_config(server, ecu)
        if ip_addr != "":
            return
        time.sleep(1)
    failure("Target 0x{:02X} isn't available after {} seconds".format(
        ecu, TIMEOUT_DELAY))


def wait_hsfz_external_availability(server, ecu):
    """Wait until it is possible to connect to the HsFz external"""
    logging.info("wait_hsfz_external_availability %s/%02X", server, ecu)

    for i in range(TIMEOUT_DELAY):
        logging.info("Send ping #%d", i)
        ip_addr = ecu_get_ip_config(server, ecu)
        if ip_addr == "":
            failure(
                "Target 0x{:02X} didn't reply to get IP config".format(ecu))
        if ip_addr != "0.0.0.0":
            ext_ip_addr = ecu_get_ip_config(ip_addr, ecu)
            if ext_ip_addr != ip_addr:
                failure("Target 0x{:02X} returned inconsistent IP config ({} vs {})".format(
                    ecu, ip_addr, ext_ip_addr))
            return
        time.sleep(1)


def test_ecu_reboot(server, ecu):
    """Test the ECU reboot"""
    logging.info("test_ecu_reboot %s/%02X", server, ecu)
    ecu_hard_reset(server, ecu)
    logging.info(
        "Sleep %d seconds before to ping the ECU", REBOOT_DELAY)
    time.sleep(REBOOT_DELAY)
    wait_hsfz_availability(server, ecu)
    wait_hsfz_external_availability(server, ecu)


def test_cancel_shutdown(server, ecu, delay):
    """Test the ECU cancel shutdown"""
    logging.info("test_cancel_shutdown %s/%02X", server, ecu)
    pwf_parken_bn_io(server)
    logging.info("Sleep %G seconds before to cancel the shutdown", delay)
    time.sleep(delay)
    pwf_wohnen(server)
    logging.info("Wait %G seconds, for wohnen state to be broacasted",
                 PWF_STATE_SETTLE_DELAY)
    time.sleep(PWF_STATE_SETTLE_DELAY)
    wait_hsfz_availability(server, ecu)
    wait_hsfz_external_availability(server, ecu)


def main():
    """Entry point of the script"""

    parser = argparse.ArgumentParser(
        description="Read ECU mode (plant, engineering, field)")

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
        "--hard-reset-count",
        help="Number of triggered ECU hard reset",
        required=False,
        default=0,
        type=int)

    parser.add_argument(
        "--cancel-shutdown-count",
        help="Sleep delays, start, end, step",
        required=False,
        default="0,0,0",
        type=lambda x: tuple(float(m) for m in x.split(",")))

    args = parser.parse_args()

    logging.info("Prepare ECUReset test execution")
    set_energy_mode_production(args.ip_addr)
    pwf_pruefen_analyse_diagnose(args.ip_addr)
    wait_hsfz_availability(args.ip_addr, args.diag_addr)

    for i in range(args.hard_reset_count):
        print("ECU Hard Reset #{}".format(i))
        test_ecu_reboot(args.ip_addr, args.diag_addr)

    logging.info("Prepare cancel shutdown test execution")
    pwf_wohnen(args.ip_addr)
    logging.info("Wait %G seconds, for wohnen state to be broacasted",
                 PWF_STATE_SETTLE_DELAY)
    time.sleep(PWF_STATE_SETTLE_DELAY)

    curr_delay, stop, step = args.cancel_shutdown_count

    while curr_delay <= stop:
        print("Cancel shutdown with delay of {} ms".format(int(curr_delay * 1000)))
        test_cancel_shutdown(args.ip_addr, args.diag_addr, curr_delay)
        curr_delay += step

    sys.exit(0)


if __name__ == "__main__":
    main()
