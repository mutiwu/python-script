
# !/usr/bin/env python
# -*- coding:UTF-8 -*-

import socket
import time
import argparse
import fcntl
import struct
#import psutil
import sys


class Iface_info(object):
    def __init__(self, iface):
        self.iface = iface
        DEVICE_NAME_LEN = 15
        self.pack_256 = struct.pack('256s', iface[:DEVICE_NAME_LEN])

    @property
    def macaddr(self):
        MAC_START = 18
        MAC_END = 24
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, self.pack_256)
        return ''.join(['%02x:' % ord(char)
                        for char in info[MAC_START:MAC_END]])[:-1]

    @property
    def ipaddr(self):
        IP_START = 20
        IP_END = 24
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip_str = fcntl.ioctl(s.fileno(),
                                 0x8915,
                                 self.pack_256)
        except IOError as e:
            print "No ip address found on %s, use '10.0.101.100' as the test ip" % self.iface
            return "10.0.101.100"
        return socket.inet_ntoa(ip_str[IP_START:IP_END])


def get_ifaces():
    ifstat = open('/proc/net/dev').readlines()
    #i[1].split(":")[0].lstrip()
    return [i.split(":")[0].lstrip().rstrip() for i in ifstat[2:]]



def iptobytes(ipaddr):
    ipseplst = ipaddr.split(".")
    hexlist = [hex(int(i)) for i in ipseplst]
    ret = ""
    for hex_i in hexlist:
        new_hex = hex_i[2:]
        if len(new_hex) == 1:
            new_hex = '0' + new_hex
        ret = ret + bytearray.fromhex(new_hex)
    return ret


def mactobytpes(macaddr):
    macseplist = macaddr.split(":")
    ret = ""
    for hex_i in macseplist:
        ret = ret + bytearray.fromhex(hex_i)
    return ret


def arpsending(iface, req_sec, dst_ipaddr):
    starttime = time.time()
    fintime = time.time() + req_sec
    endtime = 0
    ethertype = "\x08\x06"
    arphdr = "\x00\x01" + "\x08\x00" + "\x06" + "\x04" + "\x00\x01"
    ifinfo = Iface_info(iface)
    src_ipaddr = iptobytes(ifinfo.ipaddr)
    src_hwaddr = mactobytpes(ifinfo.macaddr)
    bc_hwaddr = mactobytpes("ff:ff:ff:ff:ff:ff")
    rdst_hwaddr = mactobytpes("00:00:00:00:00:00")
    dst_ipaddr = iptobytes(dst_ipaddr)
    arp_frame = bc_hwaddr + src_hwaddr + ethertype + arphdr + \
        src_hwaddr + src_ipaddr + rdst_hwaddr + dst_ipaddr
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((iface, 0))
    cnt = 0
    while endtime < fintime:
        s.send(arp_frame)
        endtime = time.time()
        cnt += 1
    s.close()
    r_sec = endtime - starttime
    pps = int(round((cnt / r_sec)))
    return r_sec, pps


def print_ret(ret):
    r_sec, pps = ret
    print("TIME\tPPS\n")
    print("%.2f\t%s PPS\n" % (r_sec, pps,))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        action="store",
                        dest="iface",
                        metavar="interface",
                        default="eth0",
                        help="Specify the interface to send arp")
    parser.add_argument("-t",
                        action="store",
                        dest="req_sec",
                        metavar="seconds",
                        type=int,
                        default=30,
                        help="Test time")
    parser.add_argument("-d",
                        action="store",
                        dest="dst_ipaddr",
                        metavar="IP ADDR",
                        default="10.0.101.254",
                        help="Dst ip address")

    args = parser.parse_args(sys.argv[1:])
    iface = args.iface
    req_sec = args.req_sec
    dst_ipaddr = args.dst_ipaddr
    #ifaces = psutil.net_if_addrs().keys()
    ifaces = get_ifaces()
    if iface not in ifaces:
        print "%s is not in the system" % iface
        sys.exit(1)
    print("Device: %s\nRequest Addr: %s\n" % (iface,dst_ipaddr))
    print("Starting testing")
    ret = arpsending(iface, req_sec, dst_ipaddr)
    print_ret(ret)
