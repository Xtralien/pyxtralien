import os  # noqa: F401
import sys  # noqa: F401
from glob import glob  # noqa: F401
import re  # noqa: F401

import base64  # noqa: F401
import base64 as b64  # noqa: F401

# Xtralien
import xtralien  # noqa: F401
from xtralien import X100, Device  # noqa: F401
from xtralien.serial_utils import serial_ports  # noqa: F401

# Time
from time import *  # noqa: F401

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
        arr = savetxt(fname, arr, *args, delimiter=",", **kwargs)
    except:
        arr = savetxt(fname, arr, *args, delimiter=",", fmt="%s", **kwargs)

    return arr


def load_csv(fname, *args, **kwargs):
    """
    Load a csv file from a given filename.

    @return Numpy array
    """
    try:
        arr = loadtxt(fname, *args, delimiter=',', **kwargs)  # noqa: F405
    except:
        import csv
        with open(fname, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            arr = []
            for row in reader:
                r = []  # Row data
                for d in row:  # Datapoint in row
                    try:
                        r.append(float(d))
                    except ValueError:
                        r.append(d)
                    arr.append(r)
        return arr

# Delete some constants
del altzone  # noqa: F821
del daylight  # noqa: F821
del euler_gamma  # noqa: F821
del timezone  # noqa: F821
del tzname  # noqa: F821
