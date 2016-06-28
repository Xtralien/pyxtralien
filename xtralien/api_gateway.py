from xtralien import Device

devices = []
import json
import SocketServer

class APIHandler(SocketServer.StreamRequestHandler):
    pass

class APIGateway(object):
    def __init__(self, host="0.0.0.0", port=3000):
        self.devices = []
        self.host = host
        self.port = port


        self.server = SocketServer

    def refreshDevices(self):
        self.devies = devices.Discover()
