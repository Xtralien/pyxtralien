import socket

s = socket.socket()
s.connect(("192.168.2.187", 8888))
s.settimeout(0.05)


def write(msg):
    s.send(bytes(msg, 'utf-8'))

def read():
    msg = ""

    while True:
        return str(s.recv(576))

    return msg




