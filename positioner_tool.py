#!/usr/bin/env python
"""Send DiSEqC commands to polar/azimuth positioner."""
from argparse import ArgumentParser
from logging import DEBUG
from struct import unpack
from time import sleep

from common import configure_logging, Fragile
from diseqc import (
    prepare_frontend,
    shutdown_frontend,
    send_diseqc_command,
)


LOGGER = configure_logging()


def parse_arguments():
    """Parse command line arguments.

    Return a Namespace object with the parsed values.
    """
    parser = ArgumentParser(
        description="Send DiSEqC commands to polar/azimuth positioner."
    )
    parser.add_argument(
        "--adapter",
        type=int,
        default=0,
        help="DVB adapter to use (default: %(default)s)",
    )
    parser.add_argument(
        "--frontend",
        type=int,
        default=0,
        help="DVB frontend to use (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="timeout in seconds to keep feeding voltage to LNBf "
        "after sending the command (default: %(default)s)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="increase logging verbosity"
    )
    parser.add_argument(
        "angle",
        type=float,
        help="Angular position in degrees from zero to which the positioner should be driven. "
        "Positive values represent angles clockwise from zero "
        "and negative values represent angles counter-clockwise from zero. "
        "Example: 12.3 for angle 12.3 degrees clockwise from zero.",
    )
    return parser.parse_args()


def get_positioner_command(signed_angle):
    """Return DiSEqC command for driving positioner to provided angle."""
    if signed_angle >= 0:
        direction = 0xe0  # clockwise from zero
    else:
        direction = 0xd0  # counter-clockwise from zero

    angle = abs(signed_angle)
    integer_angle = int(angle)
    fractional_angle = angle - integer_angle

    high_order_byte = direction | (integer_angle >> 4)
    low_order_byte = (0xff & (integer_angle << 4)) + int(round(fractional_angle * 16))
    LOGGER.debug(
        "Angle %.3f degrees is represented as: %.2x %.2x",
        signed_angle,
        high_order_byte,
        low_order_byte,
    )

    array = bytearray([0, 0, 0, 0xe0, 0x31, 0x6e, high_order_byte, low_order_byte])
    return unpack(">Q", array)[0]


def main():
    """Parse command line arguments and send commands to positioner."""
    arguments = parse_arguments()
    if arguments.verbose:
        LOGGER.level = DEBUG

    dvb_frontend = "/dev/dvb/adapter%d/frontend%d" % (
        arguments.adapter,
        arguments.frontend,
    )
    LOGGER.info("Opening DVB frontend %s", dvb_frontend)
    with Fragile(open(dvb_frontend, "wb")) as dvb_frontend_file:
        LOGGER.info("DVB frontend %s opened", dvb_frontend)

        direction = "clockwise" if arguments.angle >= 0 else "counter-clockwise"
        LOGGER.info(
            "Driving the positioner to %.3f degrees %s from zero",
            abs(arguments.angle),
            direction,
        )
        try:
            prepare_frontend(dvb_frontend_file)
            diseqc_command = get_positioner_command(arguments.angle)
            send_diseqc_command(dvb_frontend_file, diseqc_command)
        except IOError:
            shutdown_frontend(dvb_frontend_file)
            raise Fragile.Break

        LOGGER.info(
            "Waiting %d seconds with LNBf voltage enabled "
            "for the command to complete",
            arguments.timeout,
        )
        sleep(arguments.timeout)

        shutdown_frontend(dvb_frontend_file)

    LOGGER.info("DVB frontend %s closed", dvb_frontend)


if __name__ == "__main__":
    main()
