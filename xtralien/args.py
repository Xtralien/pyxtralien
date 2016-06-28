import sys
from xtralien import Device
from xtralien import serial_utils


def main():
    filter_ = len(sys.argv) >= 2 and sys.argv[1] == 'filter'

    for port in serial_utils.serial_ports():
        if filter_:
            dev = None
            try:
                dev = Device.USB(port)
                resp = dev.cloi.hello(format='auto')
                if dev.cloi.hello(format='auto') == "Hello World":
                    print(port)
                continue
            except:
                continue
            finally:
                if dev:
                    dev.close()
        else:
            print(port)


if __name__ == "__main__":
    main()
