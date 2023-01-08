#!/usr/bin/env python
"""Send custom DiSEqC commands and receive replies."""
from argparse import ArgumentParser
from logging import getLogger, DEBUG
from time import sleep

from common import configure_logging, Fragile
from diseqc import (
    prepare_frontend,
    shutdown_frontend,
    send_diseqc_command,
    receive_diseqc_reply,
)


LOGGER = configure_logging()


def hexadecimal_string_to_integer(input_string):
    """Convert provided hexadecimal string to integer."""
    return int(input_string, base=16)


def parse_arguments():
    """Parse command line arguments.

    Return a Namespace object with the parsed values.
    """
    parser = ArgumentParser(description="Send custom DiSEqC command.")
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
        default=5,
        help="timeout in seconds to keep feeding voltage to LNBf "
        "after sending the command (default: %(default)s)",
    )
    parser.add_argument(
        "--receive-timeout",
        type=int,
        default=500,
        help="timeout in milliseconds to wait for the DiSEqC reply (default: %(default)s)",
    )
    parser.add_argument(
        "--receive", action="store_true", help="also receive DiSEqC reply"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="increase logging verbosity"
    )
    parser.add_argument(
        "command",
        type=hexadecimal_string_to_integer,
        help="hexadecimal representation of bytes to send as DiSEqC command. "
        "Example: 0xe03160 to stop the positioner.",
    )
    return parser.parse_args()


def main():
    """Parse command line arguments and send the specified DiSEqC command."""
    arguments = parse_arguments()
    if arguments.verbose:
        getLogger().level = DEBUG

    dvb_frontend = "/dev/dvb/adapter%d/frontend%d" % (
        arguments.adapter,
        arguments.frontend,
    )
    LOGGER.info("Opening DVB frontend %s", dvb_frontend)
    with Fragile(open(dvb_frontend, "wb")) as dvb_frontend_file:
        LOGGER.info("DVB frontend %s opened", dvb_frontend)

        try:
            prepare_frontend(dvb_frontend_file)
            send_diseqc_command(dvb_frontend_file, arguments.command)
        except IOError:
            shutdown_frontend(dvb_frontend_file)
            raise Fragile.Break

        LOGGER.info(
            "Waiting %d seconds with LNBf voltage enabled "
            "for the command to complete",
            arguments.timeout,
        )
        sleep(arguments.timeout)

        if not arguments.receive:
            shutdown_frontend(dvb_frontend_file)
            raise Fragile.Break

        try:
            receive_diseqc_reply(dvb_frontend_file, arguments.receive_timeout)
        except IOError:
            shutdown_frontend(dvb_frontend_file)
            raise Fragile.Break

        shutdown_frontend(dvb_frontend_file)

    LOGGER.info("DVB frontend %s closed", dvb_frontend)


if __name__ == "__main__":
    main()
