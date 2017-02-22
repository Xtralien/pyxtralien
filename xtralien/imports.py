# pylint: disable=W0611,W0614,W0401,W0622,W0404
"""Xtralien Imports

This module is a list of imports used by Xtralien Python Distribution.

Most of these are common functions, however we found that we were using
them a lot so we included them here.
"""

import os  # noqa: F401
import sys  # noqa: F401
from glob import glob  # noqa: F401
import re  # noqa: F401

import base64  # noqa: F401
import base64 as b64  # noqa: F401
import decimal  # noqa: F401

# Time
from time import *  # noqa: F401

# Warnings
from warnings import *  # noqa: F403

# Xtralien
import xtralien  # noqa: F401
from xtralien import X100, Device  # noqa: F401
from xtralien.serial_utils import serial_ports  # noqa: F401

# Scipy
import scipy  # noqa: F401
from scipy import *  # noqa: F401

# Numpy
import numpy as np  # noqa: F401
from numpy import *  # noqa: F401
from numpy.random import *  # noqa: F401

# Matplotlib
import matplotlib.pyplot as plt  # noqa: F401
from matplotlib.pyplot import *  # noqa: F401

# 3D plotting
from mpl_toolkits.mplot3d import axes3d, Axes3D  # noqa: F401


def print_header(*args):
    """
    Print a header containing the given elements.

    This is just a specific format for printing.
    """
    for arg in args:
        if (not arg) or arg == '':
            buffer_ = ''
        else:
            buffer_ = ' '
        print("{:#^80}".format(arg.join([buffer_] * 2)))


def array_to_csv(arr, fname, *args, **kwargs):
    """
    Save an array to a csv, with a given filename.

    The array should be a numpy array.
    """
    try:
        savetxt(fname, arr, *args, delimiter=",", **kwargs)
    except (IOError, ValueError):
        savetxt(fname, arr, *args, delimiter=",", fmt="%s", **kwargs)


def load_csv(fname, skip_headers=False, *args, **kwargs):
    """
    Load a csv file from a given filename.

    @return Numpy array
    """
    arr = None

    with open(fname, 'r+') as fileh:
        if skip_headers:
            fileh.readline()

        try:
            arr = loadtxt(fileh, *args, delimiter=',', **kwargs)  # noqa: F405
        except (IOError, ValueError):
            import csv
            reader = csv.reader(fileh, delimiter=',')
            arr = []
            for row in reader:
                rowdata = []
                for data in row:  # Datapoint in row
                    try:
                        rowdata.append(float(data))
                    except ValueError:
                        rowdata.append(data)
                    arr.append(rowdata)
    return arr

# Delete some constants
del altzone  # noqa: F821
del daylight  # noqa: F821
del timezone  # noqa: F821
del tzname  # noqa: F821
euler_gamma = None  # noqa: F821 # pylint: disable=locally-disabled,invalid-name
del euler_gamma  # noqa: F821
