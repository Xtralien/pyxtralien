# pyxtralien

This module is a simple interface to Ossila's Source Measure Unit.

## Description

Xtralien is an open-source project from the Engineers at [Ossila](https://ossila.com)
to allow control of their equipment easily and Pythonically.
It is based on CLOI, the Command Language for Ossila Instruments.

## Installation

Using `pip`:

```shell
pip install xtralien
```

If you want to control the equipment using USB you will also need to install [pySerial](https://pypi.org/project/pyserial/).

## Usage

Below is a simple example of taking a measurement using the library.

```python
import time

from xtralien import Device

com_port = 'com5'
channel = 'smu1'

# Connect to the Source Measure Unit using USB
with Device(com_port) as SMU:
    # Turn on SMU 1
    SMU[channel].set.enabled(1, response=0)

    # Set voltage, measure voltage and current
    voltage, current = SMU[channel].oneshot(set_v)[0]

    # Print measured voltage and current
    print(f'V: {voltage} V; I: {current} A')

    # Reset output voltage and turn off SMU 1
    SMU[channel].set.voltage(0, response=0)
    time.sleep(0.1)
    SMU[channel].set.enabled(False, response=0)

```

For more documentation examples see our [programming guide](https://www.ossila.com/pages/source-measure-unit-python-programming-guide).
