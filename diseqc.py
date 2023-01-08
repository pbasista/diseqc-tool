"""Functionality for sending DiSEqC commands and receive replies."""
from array import array
from fcntl import ioctl
from logging import getLogger
from struct import pack, pack_into, unpack, Struct
from time import sleep

from ioctl.dvb import (
    DVB_DISEQC_MASTER_CMD_FORMAT,
    DVB_DISEQC_SLAVE_REPLY_FORMAT,
    FE_SET_TONE,
    FE_SET_VOLTAGE,
    FE_DISEQC_SEND_MASTER_CMD,
    FE_DISEQC_RECV_SLAVE_REPLY,
    SEC_TONE_OFF,
    SEC_VOLTAGE_13,
    SEC_VOLTAGE_18,
    SEC_VOLTAGE_OFF,
)


LOGGER = getLogger(__name__)


def set_lnbf_voltage(dvb_frontend_file, sec_voltage):
    """Set DC voltage to LNBf via an ioctl on the provided opened frontend file."""
    human_readable_values = {
        SEC_VOLTAGE_13: "13V",
        SEC_VOLTAGE_18: "18V",
        SEC_VOLTAGE_OFF: "OFF",
    }
    value = human_readable_values[sec_voltage]

    LOGGER.debug("Setting LNBf voltage to %s", value)
    try:
        ioctl(dvb_frontend_file, FE_SET_VOLTAGE, sec_voltage)
    except IOError:
        LOGGER.exception(
            "Failed to perform ioctl FE_SET_VOLTAGE(0x%x), with payload %s",
            FE_SET_VOLTAGE,
            sec_voltage,
        )
        raise

    sleep(0.015)  # 15 milliseconds

    LOGGER.debug("LNBf voltage set to %s", value)


def prepare_frontend(dvb_frontend_file):
    """Prepare the provided DVB frontend for sending a DiSEqC command."""
    LOGGER.debug("Setting tone to OFF")
    try:
        ioctl(dvb_frontend_file, FE_SET_TONE, SEC_TONE_OFF)
    except IOError:
        LOGGER.exception(
            "Failed to perform ioctl FE_SET_TONE(0x%x), with payload %s",
            FE_SET_TONE,
            SEC_TONE_OFF,
        )
        raise

    sleep(0.015)  # 15 milliseconds

    set_lnbf_voltage(dvb_frontend_file, SEC_VOLTAGE_18)

    power_up_seconds = 1
    LOGGER.debug(
        "Waiting %d seconds for the connected devices to power up", power_up_seconds
    )
    sleep(power_up_seconds)


def shutdown_frontend(dvb_frontend_file):
    """Turn off the LNBf voltage on the provided DVB frontend."""
    set_lnbf_voltage(dvb_frontend_file, SEC_VOLTAGE_OFF)


def send_diseqc_command(dvb_frontend_file, diseqc_command):
    """Send the specified DiSEqC command to the provided DVB frontend."""
    # last 6 bytes from the command number
    # converted to unsigned long long (8 bytes)
    # using big endian byte order
    command_bytes = pack(">Q", diseqc_command)[2:]

    # trim leading null bytes
    leading_null_bytes = 0
    for command_byte in command_bytes:
        if command_byte != "\0":
            break
        leading_null_bytes += 1

    # and add the same number of null bytes to the end
    command_bytes = command_bytes[leading_null_bytes:] + b"\0" * leading_null_bytes

    command_bytes_representation = " ".join(
        "%.2x" % ord(command_byte) for command_byte in command_bytes
    )

    LOGGER.info("Sending DiSEqC command %s", command_bytes_representation)
    LOGGER.debug(
        "Parsed DiSEqC command: "
        "framing: %.2x, address: %.2x, command: %.2x, argument: %.2x %.2x %.2x",
        *(ord(command_byte) for command_byte in command_bytes)
    )

    payload = pack(
        DVB_DISEQC_MASTER_CMD_FORMAT,
        ord(command_bytes[0]),
        ord(command_bytes[1]),
        ord(command_bytes[2]),
        ord(command_bytes[3]),
        ord(command_bytes[4]),
        ord(command_bytes[5]),
        6 - leading_null_bytes,
    )
    try:
        ioctl(dvb_frontend_file, FE_DISEQC_SEND_MASTER_CMD, payload)
    except IOError:
        LOGGER.exception(
            "Failed to perform ioctl FE_DISEQC_SEND_MASTER_CMD (0x%x), with payload %s",
            FE_DISEQC_SEND_MASTER_CMD,
            payload,
        )
        raise

    sleep(0.015)  # 15 milliseconds

    LOGGER.info("DiSEqC command %s sent", command_bytes_representation)


def receive_diseqc_reply(dvb_frontend_file, receive_timeout):
    """Receive a DiSEqC reply on the provided DVB frontend."""
    reply_struct = Struct(DVB_DISEQC_SLAVE_REPLY_FORMAT)
    reply_buffer = array("B", (0 for _ in range(reply_struct.size)))
    # taking the padding into account
    pack_into("@i", reply_buffer, 8, receive_timeout)

    LOGGER.info("Receiving DiSEqC reply")
    try:
        ioctl(dvb_frontend_file, FE_DISEQC_RECV_SLAVE_REPLY, reply_buffer)
    except IOError as exc:
        LOGGER.exception(
            "Failed to perform ioctl FE_DISEQC_RECV_SLAVE_REPLY (0x%x), with payload %s",
            FE_DISEQC_RECV_SLAVE_REPLY,
            reply_buffer,
        )
        if exc.errno == 95:  # operation not supported
            LOGGER.error(
                "DVB frontend %s seems to not support "
                "bidirectional DiSEqC (versions 2 and above)",
                dvb_frontend_file.name,
            )
        raise

    sleep(0.015)  # 15 milliseconds

    message_bytes = bytearray(4)
    (
        message_bytes[0],
        message_bytes[1],
        message_bytes[2],
        message_bytes[3],
        message_length,
        _timeout,
    ) = unpack(DVB_DISEQC_SLAVE_REPLY_FORMAT, reply_buffer)

    if message_length == 0:
        LOGGER.info("Received empty DiSEqC reply")
        return

    message_representation = " ".join(
        "%.2x" % ord(message_byte) for message_byte in message_bytes
    )
    LOGGER.info(
        "Received DiSEqC reply of length %d: %s",
        message_length,
        message_representation,
    )
