#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

# Create a basic logger to make logging easier
import logging

logging.basicConfig()
logger = logging.getLogger('CLOI')
logger.setLevel(logging.DEBUG)

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


class CLOI:
    def __init__(self, scan_timeout=0.03):
        self.devices = []
        self.scan_timeout = scan_timeout

    def scan(self, usb=True, network=True):
        if usb:
            for port in sutils.serial_ports():
                logger.debug("Attempting to connect to %s" % port)
                try:
                    s = serial.Serial(port)
                    try:
                        s.write(b"hello cloi\n")
                        data = s.read(576).decode('utf-8').strip().lower()
                        if data == "hello cloi":
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
                                if True: #try:

                                    s = socket.socket()
                                    s.settimeout(self.scan_timeout)
                                    s.connect_ex((ip, 8888))
                                    try:
                                        s.send(b"hello cloi\n")
                                        data = s.recv(576).decode('utf-8').strip().lower()
                                        if data == "hello world":
                                            logger.info("Found %s" % ip)
                                            d = Device()
                                            d.add_connection(SocketConnection(ip,8888))
                                            self.devices.append(d)
                                    except socket.timeout:
                                        continue
                                    except BrokenPipeError:
                                        continue
                                    finally:
                                        s.close()
                                else:
                                    pass

                except KeyError:
                    continue

    def add_device(self, device):
        self.devices.append(device)

    def list_devices(self):
        return self.devices


class Device(object):
    def __init__(self):
        self.connections = []
        self.instruments = {}

    def add_connection(self, connection):
        self.connections.append(connection)

    def command(self, command, will_return=False):
        if self.connections == []:
            logger.error("Can't send command '{cmd} because there are no open connections'".format(cmd=command))
        for conn in self.connections:
            if True:#try:
                conn.write(command)
                if will_return:
                    return conn.read(will_return)
                return
            else:#except Exception:
                continue
        logger.error("Can't send command '{cmd} because there are no open connections'".format(cmd=command))




    def __repr__(self):
        return "<Device connection={connection}/>".format(connection=self.connections[0])


class Instrument(object):
    def __init__(self, iid=None):
        if iid:
            self.iid = iid
        else:
            self.iid = 'Unknown'

    def __repr__(self):
        return "<{name} {iid}/>".format(name=self.__class__.__name__, iid=self.iid)


class Connection:
    def __init__(self):
        pass

    def read(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.read)

    def write(self, *args, **kwargs):
        logging.error("Method not implemented (%s)" % self.write)


class SocketConnection(Connection):
    def __init__(self, host, port, timeout=0.03):
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
        self.connection = serial.Serial(port)

    def __repr__(self):
        return "<Serial/USB {connection} />".format(connection=self.port)