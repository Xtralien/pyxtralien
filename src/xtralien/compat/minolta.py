"""Minolta light-measuring devices
See http://www.konicaminolta.com/instruments

----------
"""
# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

import sys
import time

ABSOLUTE = '04'
PEAK = '08'
CONT = '09'


try:
    import serial
except ImportError:
    print("Could not load `serial` module, please install if possible.")
    sys.exit(1)


class LS100(object):
    """LS100 interface class
    """

    longName = "Minolta LS100/LS110"
    driverFor = ["ls110", "ls100"]
    codes = {
        'ER00\r\n': 'Unknown command',
        'ER01\r\n': 'Setting error',
        'ER11\r\n': 'Memory value error',
        'ER10\r\n': 'Measuring range over',
        'ER19\r\n': 'Display range over',
        'ER20\r\n': 'EEPROM error (the photometer needs repair)',
        'ER30\r\n': 'Photometer battery exhausted'
    }

    def __init__(self, port, maxAttempts=1):
        self.portString = port
        self.isOpen = 0
        self.lastQual = 0
        self.type = 'LS100'
        self.com = None
        self.OK = True
        self.maxAttempts = maxAttempts

        try:
            self.com = serial.Serial(self.portString)
        except:
            self._error(
                "Couldn't connect to port %s."
                "Is it being used by another program?".format(
                    self.portString
                )
            )

        # Setup the params for PR650 comms
        if self.OK:
            # Not sure why this helps but on win32 it does!!
            self.com.close()
            # This is a slightly odd characteristic of the Minolta LS100
            self.com.setByteSize(7)
            self.com.setBaudrate(4800)
            self.com.setParity(serial.PARITY_EVEN)  # none
            self.com.setStopbits(serial.STOPBITS_TWO)
            try:
                if not self.com.isOpen():
                    self.com.open()
            except:
                self._error(
                    "Opened serial port {},"
                    "but couldn't connect to LS100".format(
                        self.portString
                    )
                )
            else:
                self.isOpen = 1

        if self.OK:  # We have an open com port. try to send a command
            for repN in range(self.maxAttempts):
                time.sleep(0.2)
                for n in range(10):
                    # Set absolute mode
                    reply = self.sendMessage('MDS,04')
                    if reply[0:2] == 'OK':
                        self.OK = True
                        break
                    elif reply not in self.codes.keys():
                        self.OK = False
                        break  # wasn't valid
                    else:
                        self.OK = False  # false so far but keep trying

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def setMode(self, value=ABSOLUTE):
        self.__mode = value
        self._send('MDS,{}'.format(value))

    def measure(self):
        """Measure the current luminance and set .lastLum to this value"""
        reply = self._send('MES')
        if self._ok(reply):
            lum = float(reply.split()[-1])
            return lum
        else:
            return -1

    @property
    def lum(self):
        """Makes a measurement and returns the luminance value
        """
        return self.measure()

    def clear(self):
        """Clear the memory of the device from previous measurements
        """
        return self._ok(self._send('CLE'))

    def _ok(self, msg):
        return msg[:2] == 'OK'

    def _error(self, msg):
        self.OK = False

    def _send(self, msg, timeout=5.0):
        """Send a command to the photometer and wait an alloted
        timeout for a response.
        """
        if msg[-2:] != '\r\n':
            msg += '\r\n'  # append a newline if necess

        # flush the read buffer first
        self.com.read(self.com.inWaiting())
        for attemptN in range(self.maxAttempts):
            # Send the message
            time.sleep(0.1)
            self.com.write(msg)
            self.com.flush()
            time.sleep(0.1)
            # Get reply (within timeout limit)
            self.com.setTimeout(timeout)
            retVal = self.com.readline()
            if len(retVal) > 0:
                self.OK = self._ok(msg)
                return retVal
