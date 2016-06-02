#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Create a basic logger to make logging easier
import logging
import os
from distutils.version import LooseVersion
import time
import re
import threading
import random

loglevels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR
}

logging.basicConfig()
logger = logging.getLogger('Xtralien')
logger.setLevel(
    loglevels.get(os.getenv('LOG', 'warn').lower(), logging.WARNING)
)

try:
    import numpy
except ImportError:
    logger.warn("Numpy not found, narray and nmatrix will fail")

import sys

if sys.version_info.major < 3:
    logger.warn("Module not supported on Python 2.x, you have been warned")

# Try and import the serial module (supports USB-serial communication)
try:
    import serial
except ImportError:
    serial = None
    logger.warn("The serial module was not found, USB not supported")

# Import useful BILs
import socket

# Import utils
# The try/except is needed to import as a module and run directly
try:
    import serial_utils as sutils
    import network_utils as nutils
except ImportError:
    import xtralien.serial_utils as sutils
    import xtralien.network_utils as nutils


def process_strip(x):
    return x.strip('\n[];')


def process_array(x):
    data = [float(y) for y in x.strip('\n[];').split(';')]
    try:
        return numpy.array(data)
    except NameError:
        return data


def process_matrix(x):
    data = [
        [float(z) for z in y.split(',')]
        for y in x.strip('\n[];').split(';')
    ]
    try:
        return numpy.array(data)
    except NameError:
        return data

number_regex = "(\-|\+)?[0-9]+(\.[0-9]+)?(e-?[0-9]+(\.[0-9]+)?)?"
re_matrix = re.compile(
    '(\[({number},{number}(;?))+\])\n?'.format(number=number_regex)
)
re_array = re.compile('(\[({number}(;?))+\])\n?'.format(number=number_regex))
re_number = re.compile('{number}\n?'.format(number=number_regex))


def process_auto(x=None):
    if x is None:
        return x
    if re_matrix.fullmatch(x):
        return process_matrix(x)
    elif re_array.fullmatch(x):
        return process_array(x)
    elif re_number.fullmatch(x):
        return float(x)
    elif '\n' in x:
        split_string = x.strip('\n;[]').split('\n')
        if len(split_string) < 2:
            return split_string[0]
        return split_string
    else:
        return x


class Device(object):
    connections = []
    current_selection = []
    formatters = {
        'strip': process_strip,
        'array': process_array,
        'matrix': process_matrix,
        'number': lambda x: float(x),
        'none': lambda x: x,
        'auto': process_auto
    }

    def __init__(self, addr=None, port=None, serial_timeout=0.1):
        self.connections = []
        self.current_selection = []
        self.in_progress = False

        if port:
            self.add_connection(SocketConnection(addr, port))
        elif addr:
            self.add_connection(SerialConnection(addr, timeout=serial_timeout))

    def scan(self):
        pass

    def add_connection(self, connection):
        self.connections.append(connection)

    def command(self, command, returns=False, sleep_time=0.05):
        if sleep_time is not None:
            time.sleep(sleep_time)
        if self.connections == []:
            logger.error(
                "Can't send command '{cmd}'\
                because there are no open connections'".format(
                    cmd=command
                )
            )
        for conn in self.connections:
            try:
                conn.write(command)
                if returns:
                    return conn.read(returns)
                return
            except Exception:
                conn.close()
                continue
        logger.error(
            "Can't send command '{cmd}'\
            because there are no open connections".format(
                cmd=command
            )
        )

    def close(self):
        for conn in self.connections:
            conn.close()

    def discover_devices(self):
        version = self.command("cloi version", True)

        if LooseVersion(version) >= LooseVersion("0.9.0"):
            logger.info("Can match against versions")

    def __getattribute__(self, x):
        if '__' in x or x in object.__dir__(self):
            return object.__getattribute__(self, x)
        else:
            self.current_selection.append(x)
            return self

    def __call__(self, *args, sleep_time=0.05, **kwargs):
        returns = (
            'returns' in kwargs.keys() or
            'format' in kwargs.keys() or
            kwargs.get('callback', False)
        )
        command = ' '.join(self.current_selection + [str(x) for x in args])
        self.current_selection = []

        formatter = lambda x: x
        if 'format' in kwargs.keys() or kwargs.get('callback', None):
            if 'format' not in kwargs.keys() or kwargs.get('format', ):
                kwargs['format'] = 'auto'
            try:
                formatter = self.formatters[kwargs.get('format', 'auto')]
            except KeyError:
                if kwargs['format']:
                    logger.warning('Formatter not found')

        callback = kwargs.get('callback', None)

        if callback:
            def async_function():
                while self.in_progress:
                    continue
                self.in_progress = True
                data = formatter(self.command(command, returns=True))
                self.in_progress = False
                callback(data)
            return threading.Thread(target=async_function).start()

        self.in_progress = True
        data = formatter(
            self.command(command, returns=returns, sleep_time=sleep_time)
        )
        self.in_progress = False
        return data

    def __repr__(self):
        if len(self.connections):
            return "<Device connection={connection}/>".format(
                connection=self.connections[0]
            )
        else:
            return "<Device connection=None/>"

    @staticmethod
    def discover():
        udp_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )
        udp_socket.bind(('0.0.0.0', random.randrange(6000, 50000)))
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.settimeout(0.01)
        udp_socket.sendto(b"xtra", ('<broadcast>', 8889))
        devices = []
        try:
            while True:
                (_, ipaddr) = udp_socket.recvfrom(4)
                devices.append(Device(addr=ipaddr[0], port=8888))
        except socket.timeout:
            pass
        finally:
            udp_socket.close()
        return devices


class Connection(object):
    def __init__(self):
        pass

    def read(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.read)

    def write(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.write)

    def close(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.close)


class SocketConnection(Connection):
    def __init__(self, host, port, timeout=0.07):
        super(SocketConnection, self).__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.socket.connect((host, port))
        self.socket.settimeout(timeout)

    def read(self, wait=True):
        retval = ""
        if wait:
            while retval == "":
                try:
                    retval = retval + str(self.socket.recv(576), 'utf-8')
                except socket.timeout:
                    continue

        while True:
            try:
                retval = retval + str(self.socket.recv(576), 'utf-8')
            except socket.timeout:
                break

        return retval

    def write(self, cmd):
        if type(cmd) == str:
            cmd = bytes(cmd, 'utf-8')
        self.socket.send(cmd)

    def close(self):
        self.socket.close()

    def __repr__(self):
        return "<Socket {host}:{port} />".format(
            host=self.host,
            port=self.port
        )


class SerialConnection(Connection):
    def __init__(self, port, timeout=0.1):
        super(SerialConnection, self).__init__()
        self.port = port
        self.connection = serial.Serial(port, timeout=timeout)

    def read(self, wait=True):
        retval = ""
        while wait and self.connection.inWaiting() == 0:
            continue

        while self.connection.inWaiting():
            try:
                retval = retval + str(self.connection.read(436), 'utf-8')
            except Exception:
                break

        return retval

    def write(self, cmd):
        if type(cmd) == str:
            cmd = bytes(cmd, 'utf-8')
        self.connection.write(cmd)

    def close(self):
        self.connection.close()

    def __repr__(self):
        return "<Serial/USB {connection} />".format(connection=self.port)