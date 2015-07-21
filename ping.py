#!/usr/bin/env python
import commands
import re
import sys
import getopt
import signal

class Ping(object):
    def __init__(self,iface,ip_addr,counts):
        self.ip_addr = ip_addr
        self.iface = iface
        self.counts = counts
        self.packets = [0, 
                        1,
                        48,
                        64,
                        512,
                        1440,
                        1500,
                        1505,
                        4096,
                        4192,
                        32767,
                        65507,]
        self.interval = [0.2,
                         0.4,
                         0.8,
                         1,]
        self.ptn = re.compile(r"(\d+)\% packet loss")
        self.fail_ratio = 5
    def ping(self):
        self.faillist = []
        self.losspacket = []
        self.goodping = []
        for self.i in self.interval:
            for self.p in self.packets:
                self.cmd = "ping -I %s %s -c %s " % (self.iface, 
                                                     self.ip_addr, self.counts)
                self.cmd += "-i %s -s %s" % (self.i, self.p)
                self.status, self.output = commands.getstatusoutput(self.cmd)
                if self.status:
                    self.failitem = "ping failed with interval:%s, size:%s " % (self.i, self.p) 
                    self.failitem += "return the status %s." % self.status
                    self.faillist.append(self.failitem)
                self.ploss = self.ptn.search(self.output)
                if int(self.ploss.groups()[0]) > self.fail_ratio:
                    self.lossitem = "Packet loss with interval:%s, size:%s" % (self.i, self.p)
                    self.lossitem += "And %s" % self.ploss.group()
                    self.losspacket.append(self.lossitem)
                self.gooditem = "Pass with interval:%s, size:%s" % (self.i, self.p)
                self.gooditem += "\tAnd %s" % self.ploss.group()
                self.goodping.append(self.gooditem)
        return self.faillist, self.losspacket, self.goodping
        
def usage():
    return """-i $interface -a(eth0 def) $ip_address(127.0.0.1 def) 
              -c $counts(10 def)"""
def exit_handle(signum):
    print "signal number is $s, e is %s exit" % signum
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handle)
    signal.signal(signal.SIGTERM, exit_handle)
    ip_addr = "10.66.10.63"
    counts = "10"
    iface = "eth0"
    try:
        options, args = getopt.getopt(sys.argv[1:], "i:a:c:",
                                      [
                                      'help',
                                       ])
    except getopt.GetoptError:
        print usage()
        sys.exit(0)
    for name, value in options:
        if name == "--help":
            print usage()
            sys.exit(0)
        if name == "-i":
            iface = value
        if name == "-a":
            ip_addr = value
        if name == "-c":
            counts = value
    if len(sys.argv) == 1:
        print "will use the default cfg"
        print usage()
    test = Ping(iface=iface, ip_addr=ip_addr, counts=counts) 
    output = {
            0:"The folloings are failed pings",
            1:"The followings are pings that lost than 5",
            2:"The followings are good pings",
            }
    result = test.ping()
    for i in output:
        print output[i]
        print "\n".join(result[i])
