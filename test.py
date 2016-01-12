import cloi
import numpy as np
import matplotlib.pyplot as plt
import time

x11 = cloi.Device('192.168.2.144', 8888)

x11.cloi.hello(format=None)

print(x11.smu1.calibration.read(format=None))
x11.smu1.set.osr(1)
x11.smu1.set.range(5)
x11.smu1.set.voltage(1)
results = x11.smu1.measurei(format='narray')

plt.plot(results, 'ro-')
plt.show()