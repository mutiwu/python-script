#!/usr/bin/env python
# coding=utf-8

import commands
import sys
import re
import os
import argparse

parser= argparse.ArgumentParser()
parser.add_argument("int", metavar="N", type=int, help="The first CPU")
args = parser.parse_args()
int_cpu = args.int
cmd = "pgrep snort"
status, output = commands.getstatusoutput(cmd)
if status:
    print "pgrep hit error,exit."
    print output
    sys.exit(1)
if output == "":
    print "no snort exist, exit"
    sys.exit(0)
pid_snort = int(output)
cmd = "pstree -p %s" %pid_snort
status, output = commands.getstatusoutput(cmd)
if status:
    print "pstree hit error, exit"
    sys.exit(1)
re_p = re.compile(r".*?\((\d+)\)")
plist = re_p.findall(output)
psize = len(plist)
for i in range(psize):
    cpu = int_cpu + i
    cmd = "taskset -cp %s %s" % (cpu, plist[i])
    status, output = commands.getstatusoutput(cmd)
    if status:
        print "taskset hit error"
        print output
        sys.exit(1)
    print output
p_str = ",".join(plist)
cmd = "top -p %s" % p_str
os.system(cmd)
