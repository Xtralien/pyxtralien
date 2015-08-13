#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

__author__ = 'jack'

import sys

try:
    import cloi
except ImportError:
    try:
        import __init__ as cloi
    except ImportError:
        cloi = None
        sys.exit(1)

if cloi:
    c = cloi.CLOI(0.05)
    c.scan(network=False)

    for device in c.list_devices():
        print(device)


