#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

# Create a basic logger to make logging easier
import logging
import os
from distutils.version import LooseVersion
import time
import re
import threading

loglevels = {
    'debug': logging.DEBUG,
    'info' : logging.INFO,
    'warn' : logging.WARNING,
    'error': logging.ERROR
}

logging.basicConfig()
logger = logging.getLogger('CLOI')
logger.setLevel(loglevels.get(os.getenv('LOG', 'warn').lower(), logging.WARNING))

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


# Try and import the netifaces module, used to get the local ip addresses
# and subnet masks to generate a list of possible addresses
try:
    import netifaces
except ImportError:
    netifaces = None
    logger.warn("netifaces module not found, Network scan not supported")


# Import useful BILs
import socket

# Import utils
# The try/except is needed to import as a module and run directly
try:
    import serial_utils as sutils
    import network_utils as nutils
except ImportError:
    import cloi.serial_utils as sutils
    import cloi.network_utils as nutils

registered_devices = {}

class CLOI(object):
    def __init__(self, scan_timeout=0.03):
        self.devices = []
        self.scan_timeout = scan_timeout

    def scan(self, usb=True, network=False):
        if usb:
            for port in sutils.serial_ports():
                logger.debug("Attempting to connect to %s" % port)
                try:
                    s = serial.Serial(port)
                    try:
                        s.write(b"cloi hello\n")
                        data = s.read(576).decode('utf-8').strip().lower()
                        if data == "hello world":
                            d = Device()
                            self.devices.append(d)

                    except socket.timeout:
                        pass
                    finally:
                        s.close()
                except Exception:
                    logger.warning("Could not open port %s" % port)

        if network:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                try:
                    for addr in addrs[netifaces.AF_INET]:
                        if addr.get('broadcast', None):
                            for ip in nutils.generate_ip_list(addr):
                                try:

                                    s = socket.socket()
                                    s.settimeout(self.scan_timeout)
                                    s.connect((ip, 8888))
                                    try:
                                        logger.debug("Testing " + ip)
                                        s.send(b"cloi hello\n")
                                        data = s.recv(576)

                                        if data == b"Hello World\n":
                                            logger.info("Found %s" % ip)
                                            d = Device()
                                            d.add_connection(SocketConnection(ip,8888))
                                            d.discover_devices()
                                            self.devices.append(d)
                                    except socket.timeout:
                                        continue
                                    except BrokenPipeError:
                                        continue
                                    finally:
                                        s.close()
                                except socket.error:
                                    pass

                except KeyError:
                    continue

    def add_device(self, device):
        self.devices.append(device)

    def list_devices(self):
        return self.devices

def process_strip(x):
    return x.strip('\n[];')

def process_array(x):
    data = [float(y) for y in x.strip('\n[];').split(';')]
    try:
        return numpy.array(data)
    except NameError:
        return data
    
def process_matrix(x):
    data = [[float(z) for z in y.split(',')] for y in x.strip('\n[];').split(';')]
    try:
        return numpy.array(data)
    except NameError:
        return data
    
number_regex = "(\-|\+)?[0-9]+(\.[0-9]+)?(e-?[0-9]+(\.[0-9]+)?)?"
re_matrix = re.compile('(\[({number},{number}(;?))+\])\n?'.format(number=number_regex))
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
    
    def __init__(self, addr=None, port=None):
        self.connections = []
        self.current_selection = []
        self.in_progress = False
        
        if port:
            self.add_connection(SocketConnection(addr, port))
        elif addr:
            self.add_connection(SerialConnection(addr))

    def scan(self):
        pass

    def add_connection(self, connection):
        self.connections.append(connection)

    def command(self, command, returns=False):
        time.sleep(0.2)
        if self.connections == []:
            logger.error("Can't send command '{cmd} because there are no open connections'".format(cmd=command))
        for conn in self.connections:
            if True:#try:
                conn.write(command)
                if returns:
                    return conn.read(returns)
                return
            else:#except Exception:
                continue
        logger.error("Can't send command '{cmd} because there are no open connections'".format(cmd=command))


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

    def __call__(self, *args, **kwargs):
        returns = 'returns' in kwargs.keys() or 'format' in kwargs.keys() or kwargs.get('callback', False)
        command = ' '.join(self.current_selection + [str(x) for x in args])
        self.current_selection = []
        
        formatter = lambda x: x
        if 'format' in kwargs.keys() or kwargs.get('callback', None):
            if not 'format' in kwargs.keys() or kwargs.get('format', ):
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
        data = formatter(self.command(command, returns=returns))
        self.in_progress = False
        return data

    def __repr__(self):
        if len(self.connections):
            return "<Device connection={connection}/>".format(connection=self.connections[0])
        else:
            return "<Device connection=None/>"


class Connection:
    def __init__(self):
        pass

    def read(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.read)

    def write(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.write)


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

    def __repr__(self):
        return "<Socket {host}:{port} />".format(host=self.host, port=self.port)


class SerialConnection(Connection):
    def __init__(self, port):
        super(SerialConnection, self).__init__()
        self.port = port
        self.connection = serial.Serial(port, timeout=0.1)
        
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

    def __repr__(self):
        return "<Serial/USB {connection} />".format(connection=self.port)


def register(cls, path):
    registered_devices[path] = cls
