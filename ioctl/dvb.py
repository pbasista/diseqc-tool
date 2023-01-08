"""Python versions of some ioctl definitions related to DVB frontend.

Original definitions have been obtained
from Linux kernel's header file <linux/dvb/frontend.h>.
"""
from .ioctl_numbers import _IO, _IOR, _IOW

# enum fe_sec_tone_mode
SEC_TONE_ON = 0
SEC_TONE_OFF = 1

# enum fe_sec_voltage
SEC_VOLTAGE_13 = 0
SEC_VOLTAGE_18 = 1
SEC_VOLTAGE_OFF = 2

FE_SET_TONE = _IO(ord("o"), 66)
FE_SET_VOLTAGE = _IO(ord("o"), 67)
FE_ENABLE_HIGH_LNB_VOLTAGE = _IO(ord("o"), 68)

# It is necessary to take the padding
# between the individual structure members into account.
# Therefore, the @ character needs to be used
# as the first character of the format string.
# https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment

# struct dvb_diseqc_master_cmd {
#     __u8 msg[6];
#     __u8 msg_len;
# };
DVB_DISEQC_MASTER_CMD_FORMAT = "@6BB"
FE_DISEQC_SEND_MASTER_CMD = _IOW(ord("o"), 63, DVB_DISEQC_MASTER_CMD_FORMAT)

# struct dvb_diseqc_slave_reply {
#     __u8 msg[4];
#     __u8 msg_len;
#     int  timeout;
# };
DVB_DISEQC_SLAVE_REPLY_FORMAT = "@4BBi"
FE_DISEQC_RECV_SLAVE_REPLY = _IOR(ord("o"), 64, DVB_DISEQC_SLAVE_REPLY_FORMAT)
