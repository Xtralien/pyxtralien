#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Create a basic logger to make logging easier
import logging
import os
import time
import re
import threading
import random

from xtralien.serial_utils import serial_ports
from xtralien.keithley import K2600

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
    logger.warn("Module not supported on Python 2.x")

# Try and import the serial module (supports USB-serial communication)
try:
    import serial
except ImportError:
    serial = None
    logger.warn("The serial module was not found, USB not supported")

# Import useful BILs
import socket


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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is not None:
            print(traceback)
        self.close()

    @property
    def connection(self):
        return self.connections[0]

    def add_connection(self, connection):
        self.connections.append(connection)

    def command(self, command, returns=False, sleep_time=0.001):
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
            if True:  # try:
                conn.write(command)
                return conn.read(returns)
            else:  # except (Exception, e):
                # print(e)
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

    def __getattribute__(self, x):
        if '__' in x or x in object.__dir__(self):
            return object.__getattribute__(self, x)
        else:
            self.current_selection.append(x)
            return self

    def __getitem__(self, x):
        self.current_selection.append(x)
        return self

    def __call__(self, *args, **kwargs):
        sleep_time = kwargs.get("sleep_time", 0.001)
        self.current_selection += args
        returns = kwargs.get('response', True) or kwargs.get('callback', False)
        command = ' '.join([str(x) for x in self.current_selection])
        self.current_selection = []

        formatter = lambda x: x
        if returns:
            try:
                formatter = self.formatters.get(
                    kwargs.get('format', 'auto'),
                    formatter
                )
            except KeyError:
                if kwargs.get('format', None):
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
    def discover(broadcast_address=None, timeout=0.1, *args, **kwargs):
        broadcast_address = broadcast_address or '<broadcast>'
        udp_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )
        udp_socket.bind(('0.0.0.0', random.randrange(6000, 50000)))
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.settimeout(timeout)
        udp_socket.sendto(b"xtra", (broadcast_address, 8889))
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

    def dup(self):
        return DeviceDuplicate(self)

    @staticmethod
    def USB(com=None, *args, **kwargs):
        if com is None:
            while True:
                try:
                    com = serial_ports()[0]
                except IndexError:
                    continue
                else:
                    break

        return Device(com, *args, **kwargs)

    fromUSB = USB
    openUSB = USB

    @staticmethod
    def COM(com, *args, **kwargs):
        return Device.USB("COM{}".format(com), *args, **kwargs)

    fromCOM = COM
    openCOM = COM

    @staticmethod
    def Network(ip, *args, **kwargs):
        return Device(ip, 8888, *args, **kwargs)

    fromNetwork = Network
    openNetwork = Network

    @staticmethod
    def first(*args, **kwargs):
        while True:
            try:
                try:
                    com = serial_ports()[0]
                    return Device.USB(com, *args, **kwargs)
                except IndexError:
                    return Device.discover(*args, **kwargs)[0]
            except IndexError:
                continue


class DeviceDuplicate(object):
    def __init__(self, device):
        self.device = device
        self.command_base = self.device.current_selection
        self.device.current_selection = []
        self.current_selection = []

    def __getattribute__(self, x):
        if '__' in x or x in object.__dir__(self):
            return object.__getattribute__(self, x)
        else:
            self.current_selection.append(x)
            return self

    def __getitem__(self, x):
        self.current_selection.append(x)
        return self

    def __call__(self, *args, **kwargs):
        self.device.current_selection = []
        response = self.device(
            ' '.join(self.command_base + self.current_selection),
            *args,
            **kwargs
        )
        self.current_selection = []
        return response


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

        while wait and (self.connection.inWaiting() == 0):
            continue

        while self.connection.inWaiting() > 0:
            try:
                retval = retval + str(
                    self.connection.read(
                        self.connection.inWaiting()
                    ),
                    'utf-8'
                )
            except Exception:
                break

        return retval

    def write(self, cmd):
        if type(cmd) == str:
            cmd = bytes(cmd, 'utf-8')
        self.connection.write(cmd)
        while self.connection.out_waiting > 0:
            continue

    def close(self):
        self.connection.close()

    def __repr__(self):
        return "<Serial/USB {connection} />".format(connection=self.port)


X100 = Device
