#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

__author__ = 'jack'

import __init__ as cloi

c = cloi.CLOI(0.02)
c.scan()

for device in c.list_devices():
    print(device)
