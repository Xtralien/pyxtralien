from __future__ import print_function
import cloi

# Connect over Ethernet
x100 = cloi.Device('192.168.2.144', 8888)
# Alternatively if you use serial uncomment the line below
# x100 = cloi.Device('COM3')

x100.cloi.hello(callback=print)
# The above line will print "Hello World!"
# when data returns from the device

for x in range(20):
    x100.cloi.hello(callback=print)
# The above lines will print "Hello World!" 20 times
# as soon as each cloi hello command is returned from the device


def handle_numpy_data(data):
    print(data.shape)

x100.smu1.sweep(0, 0.1, 3, callback=handle_numpy_data)
# The above is an asynchronous version of the line below
handle_numpy_data(x100.smu1.sweep(0, 0.1, 3, format='auto'))
