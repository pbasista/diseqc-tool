# DiSEqC tool

A tool for sending custom DiSEqC commands via DVB frontend
to the connected devices and optionally to receive their replies.

## Usage:

```shell
$ ./diseqc_tool.py --help
usage: diseqc_tool.py [-h] [--adapter ADAPTER] [--frontend FRONTEND]
                      [--timeout TIMEOUT] [--receive-timeout RECEIVE_TIMEOUT]
                      [--receive] [--verbose]
                      command

Send custom DiSEqC command.

positional arguments:
  command               hexadecimal representation of bytes to send as DiSEqC
                        command. Example: 0xe03160 to stop the positioner.

optional arguments:
  -h, --help            show this help message and exit
  --adapter ADAPTER     DVB adapter to use (default: 0)
  --frontend FRONTEND   DVB frontend to use (default: 0)
  --timeout TIMEOUT     timeout in seconds to keep feeding voltage to LNBf
                        after sending the command (default: 5)
  --receive-timeout RECEIVE_TIMEOUT
                        timeout in milliseconds to wait for the DiSEqC reply
                        (default: 500)
  --receive             also receive DiSEqC reply
  --verbose             increase logging verbosity
```

For example, instructing a polar/azimuth positioner to stop its movement
can be done by sending a DiSEqC command `0xe03160`:

```shell
$ ./diseqc_tool.py 0xe03160
2023-01-08 08:59:36,858    INFO common Opening DVB frontend /dev/dvb/adapter0/frontend0
2023-01-08 08:59:36,908    INFO common DVB frontend /dev/dvb/adapter0/frontend0 opened
2023-01-08 08:59:37,973    INFO diseqc Sending DiSEqC command e0 31 60 00 00 00
2023-01-08 08:59:38,002    INFO diseqc DiSEqC command e0 31 60 00 00 00 sent
2023-01-08 08:59:38,003    INFO common Waiting 5 seconds with LNBf voltage enabled for the command to complete
2023-01-08 08:59:43,024    INFO common DVB frontend /dev/dvb/adapter0/frontend0 closed
```

### DiSEqC commands

The following table contains some potentially useful DiSEqC commands:

| Command    | Description |
|------------|-------------|
| `0xe00000` | Reset microcontrollers of all devices. |
| `0xe03100` | Reset microcontroller of the polar/azimuth positioner. |
| `0xe03160` | Stop the movement of the polar/azimuth positioner. |
| `0xe03163` | Disable limits of the polar/azimuth positioner. |
| `0xe03166` | Set clockwise limit of the polar/azimuth positioner to the current position. |
| `0xe03167` | Set counter-clockwise limit of the polar/azimuth positioner to the current position. |
| `0xe0316b01` | Drive the polar/azimuth positioner to the stored position #1. |
| `0xe0316ee0a0` | Drive the polar/azimuth positioner to the angle 10 degrees clockwise from zero. |
| `0xe0316ed0a0` | Drive the polar/azimuth positioner to the angle 10 degrees counter-clockwise from zero. |

A more complete reference to DiSEqC commands is available in the DiSEqC [documentation](https://www.eutelsat.com/files/PDF/DiSEqC-documentation.zip) by Eutelsat, specifically in the "DiSEqC Bus Specification" document that is included in the linked zip archive as the `bus_spec.pdf` file.
It contains details of DiSEqC commands' structure and some of the values that can be used in its individual parts.

### Driving polar/azimuth positioner to a specific angle

There is a convenience script called `positioner_tool.py`
which can be used for driving a polar/azimuth positioner to a specific angle:

```shell
$ ./positioner_tool.py --help
usage: positioner_tool.py [-h] [--adapter ADAPTER] [--frontend FRONTEND]
                          [--timeout TIMEOUT] [--verbose]
                          angle

Send DiSEqC commands to polar/azimuth positioner.

positional arguments:
  angle                Angular position in degrees from zero to which the
                       positioner should be driven. Positive values represent
                       angles clockwise from zero and negative values
                       represent angles counter-clockwise from zero. Example:
                       12.3 for angle 12.3 degrees clockwise from zero.

optional arguments:
  -h, --help           show this help message and exit
  --adapter ADAPTER    DVB adapter to use (default: 0)
  --frontend FRONTEND  DVB frontend to use (default: 0)
  --timeout TIMEOUT    timeout in seconds to keep feeding voltage to LNBf
                       after sending the command (default: 15)
  --verbose            increase logging verbosity
```

For example, to drive the positioner to 12.3 degrees angle clockwise from zero,
it is possible to use the following command:

```shell
$ ./positioner_tool.py 12.3
2023-01-08 09:03:23,385    INFO common Opening DVB frontend /dev/dvb/adapter0/frontend0
2023-01-08 09:03:23,423    INFO common DVB frontend /dev/dvb/adapter0/frontend0 opened
2023-01-08 09:03:23,423    INFO common Driving the positioner to 12.300 degrees clockwise from zero
2023-01-08 09:03:24,497    INFO diseqc Sending DiSEqC command e0 31 6e e0 c5 00
2023-01-08 09:03:24,526    INFO diseqc DiSEqC command e0 31 6e e0 c5 00 sent
2023-01-08 09:03:24,527    INFO common Waiting 15 seconds with LNBf voltage enabled for the command to complete
2023-01-08 09:03:39,549    INFO common DVB frontend /dev/dvb/adapter0/frontend0 closed
```
