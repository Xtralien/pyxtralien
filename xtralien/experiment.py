MONITOR = 0b001
TRIGGER = 0b010


class Experiment(object):
    def __init__(self, name=None, description=None, mode=MONITOR, frequency=1, devices=None):
        self.devices = devices
        self.frequency = frequency
        self.mode = mode

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.save()
