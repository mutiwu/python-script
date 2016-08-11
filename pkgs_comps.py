#!/usr/bin/env python
# coding=utf-8
import commands
import xml.etree.ElementTree as ET
import argparse
import sys
import os

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
parser.add_argument("-c",
		    action="store",
		    dest="cmppath",
		    metavar="FILEPATH"
		   )
args = parser.parse_args(sys.argv[1:])


xmlpath = args.xmlpath
srciso = args.srciso
dstreiso = args.destiso
cmppath = args.cmppath
Ppath = "/Packages"
Rpath = "/repodata"
srcP = args.srciso + Ppath
cmpP = args.cmppath + Ppath
dstP = dstreiso + Ppath
dstR = dstreiso + Rpath
dstcompsxml = dstR + "/comps.xml"

opl = os.listdir(srcP)
oplstr = "\n".join(opl)
print oplstr
def cmd_handle(cmd):
    status, output = commands.getstatusoutput(cmd)
    if status:
	print output
	__import__("shutil").rmtree(dstreiso)
	os.sys.exit(1)
    print cmd
cmd = "mkdir -p %s" %dstreiso
cmd_handle(cmd)
cmd = "cp -a %s/* %s/" %(cmppath, dstreiso)
cmd_handle(cmd)
cmd = "rm -rf %s/*" %dstR
cmd_handle(cmd)
cmd = "rm -rf %s/*" %dstP
cmd_handle(cmd)
cmd = "cp %s %s" %(xmlpath, dstcompsxml)
cmd_handle(cmd)

xmltree = ET.parse(dstcompsxml)
compsrootele = xmltree.getroot()
glst = compsrootele.findall("group")
#gdict = {}
for g in glst:
    gid = g.find("id")
    print gid.text
    ple = g.find("packagelist")
    pks = ple.getchildren()
    to_del_list = []
    for pk in pks:
	if pk.text not in oplstr:
	    print pk.text
	    to_del_list.append(pk)

    print to_del_list
    for pk in to_del_list:
	print pk
	pks.remove(pk)
#	__import__("shutil").rmtree(dstreiso)
#        pl.append(pk.text)
    ET.dump(ple)
    for pk in pks:
        pkt = pk.text + "*"
        cmd = "cp %s/%s %s/" %(srcP, pkt, dstP )
	cmd_handle(cmd)
#    gdict[id.text] = pl
# print gdict
npl = os.listdir(dstP)
cpl = os.listdir(cmpP)
diff_pl = []
for i in cpl:
    if i not in npl:
	diff_pl.append(i)
if "TRANS.TBL" in diff_pl:
    diff_pl.remove("TRANS.TBL")
print "\n".join(diff_pl)
for dp in diff_pl:
    cmd = "cp %s/%s %s" %(cmpP, dp, dstP)
    cmd_handle(cmd)

cmd = "createrepo -g %s %s" %(dstcompsxml, dstreiso )
cmd_handle(cmd)
