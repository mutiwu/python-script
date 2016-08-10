#!/usr/bin/env python
# coding=utf-8
import commands
import xml.etree.ElementTree as ET
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-s",
                    action="store",
                    dest="srciso",
                    metavar="FILEPATH",
                    default="/opt/centosminisrc/",
                    help="The original iso mountpoint."
                   )
parser.add_argument("-i",
                    action="store",
                    dest="xmlpath",
                    metavar="FILEPATH"
                   )
parser.add_argument("-d",
                    action="store",
                    dest="destiso",
                    metavar="FILEPATH"
                   )
args = parser.parse_args(sys.argv[1:])


xmlpath = args.xmlpath
srciso = args.srciso
dstreiso = args.destiso
Ppath = "/Packages"
Rpath = "/repodata"
srcP = args.srciso + Ppath
dstP = dstreiso + Ppath
dstR = dstreiso + Rpath
dstcompsxml = dstR + "/comps.xml"
cmd = "mkdir -p %s" %dstreiso
commands.getstatusoutput(cmd)

cmd = "cp -a %s/* %s/" %(srciso, dstreiso)
print cmd
commands.getstatusoutput(cmd)
cmd = "rm -rf %s/*" %dstR
print cmd
commands.getstatusoutput(cmd)
cmd = "rm -rf %s/*" %dstP
print cmd
commands.getstatusoutput(cmd)
cmd = "cp %s %s" %(xmlpath, dstcompsxml)
print cmd
commands.getstatusoutput(cmd)

xmltree = ET.parse(dstcompsxml)
compsrootele = xmltree.getroot()
glst = compsrootele.findall("group")
gdict = {}
for g in glst:
    id = g.find("id")
    id.text
    ple = g.find("packagelist")
    pks = ple.getiterator("packagereq")
    pl = []
    for pk in pks:
        pl.append(pk.text)
        pkt = pk.text + "*"
        cmd = "cp %s/%s %s/" %(srcP, pkt, dstP )
        print cmd
        commands.getstatusoutput(cmd)
    gdict[id] = pl
print gdict


cmd = "createrepo -g %s %s" %(dstcompsxml, dstreiso )
commands.getstatusoutput(cmd)