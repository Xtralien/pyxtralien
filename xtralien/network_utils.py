__author__ = 'jack'

import socket

def generate_ip_list(addr):
    netmask = ip_to_int(addr.get('netmask'))
    mask = netmask ^ ((2 ** 32) - 1) # Get the inverse of the netmask
    ip = ip_to_int(addr.get('addr'))
    for x in range(ip & netmask, ip | mask):
        yield int_to_ip(x)
    return []


def ip_to_int(ip):
    retval = 0

    for x in socket.inet_aton(ip):
        retval = (retval << 8) | x

    return retval


def int_to_ip(ip):
    retval = bytearray()

    for x in range(4):
        retval.append((ip >> (3 - x)*8) & 0xff)

    return socket.inet_ntoa(bytes(retval))