from xtralien import Device

# Constants
EXT = 1 << 4
FAN = 1 << 5
SHUTTER = 1 << 6
SHORT = 1 << 7


class SmartBoard(object):
    def __init__(self, device):
        """
        The SmartBoard is a wrapper around the Device class that uses
        predefined commands to make using the smartboard easier.
        """
        self.device = device
        self.relays = 1

        self.device.smartio.set.value.port[2](relays, response=0)

    def pixel(pixel, on=True):
        pixel = pixel or 1
        self.device.smartio.set.value.pin[15 + pixel](on, response=0)

    def pixels(*pixels):
        value = 0

        if pixels:
            for pixel in pixels:
                value |= 1 << pixel - 1 if pixel > 0 else 0
        else:
            value = 0b11111111

        self.device.smartio.set.value.port(0, value, response=0)

    def toggle(*toggles):
        self.relays ^= switch
        print(relays)
        self.device.smartio.set.value.port(2, self.relays, response=0)
        sleep(0.1)

    @staticmethod
    def USB(port):
        device = X100.USB(port)
        return SmartBoard(device)

    @staticmethod
    def Network(ip):
        device = Device.Network(ip)
        return SmartBoard(device)

relays = 1
