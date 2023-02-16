#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Print a list of all devices discovered on the network
"""

import xtralien


def main():
    """
    Attempt to discover all devices on the network and print any
    found.
    """
    for dev in xtralien.Device.discover(timeout=1.0):
        print(dev.connections[0].host)


if __name__ == "__main__":
    main()
