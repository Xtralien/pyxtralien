import xtralien


def main():
    for dev in xtralien.Device.discover(timeout=1.0):
        print(dev.connections[0].host)


if __name__ == "__main__":
    main()
