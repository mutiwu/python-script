#!/usr/bin/env python
# coding=utf-8

import commands
import sys
import re
import os
import argparse
import random
import platform
import exceptions

parser= argparse.ArgumentParser()
parser.add_argument("int", metavar="N", type=int, help="The first CPU")
args = parser.parse_args()
int_cpu = args.int

def pidtree(p_name):
    cmd = "pgrep %s" % p_name
    status, output = commands.getstatusoutput(cmd)
    if status:
        print "pgrep hit error,exit."
        print output
        sys.exit(1)
    if output == "":
        print "no %s exist, exit" % p_name
        sys.exit(0)
    pid_snort = int(output)
    cmd = "pstree -p %s" %pid_snort
    status, output = commands.getstatusoutput(cmd)
    if status:
        print "pstree hit error, exit"
        sys.exit(1)
    re_p = re.compile(r".*?\((\d+)\)")
    plist = re_p.findall(output)
    p_str = ",".join(plist)
    return plist, p_str


def alltrheads_task(plist, psize):
    for i in range(psize):
        cpu = int_cpu + i
        cmd = "taskset -cp %s %s" % (cpu, plist[i])
        status, output = commands.getstatusoutput(cmd)
        if status:
            print "taskset hit error"
            print output
            sys.exit(1)
        print output

plist, p_str = pid_tree(p_name)
psize = len(plist)


#    status, output = commands.getstatusoutput("ls /sys/devices/system/cpu/")
#    if status:
#	print "get error"
#	print output
#	sys.exit(1)
#    re_cpu = re.compile(r'.*?cpu(\d+)\n')
#    max_clist = re_cpu.findall(output)
#    max_cpu_n = len(max_clist)
def p_taskset():
    status, output = commands.getstatusoutput("cat /proc/stat")
    if status:
	print "get error"
	print output
	sys.exit(1)
    re_ccpu = re.compile(r'\ncpu(\d+) ')
    curr_clist = re_ccpu.findall(output)
    curr_clist.pop(curr_clist.index('0'))
    curr_cpu_n = len(curr_clist)
    
#    if max_cpu_n == curr_cpu_n:
#	alltrheads_task(plist, psize)
    try:
        task_clist = random.sample(curr_clist, psize)
    except ValueError:
	print "Not enough cpus to pin, there're %s threads, and just %s cpus" % (psize, curr_cpu_n)
	sys.exit(2)
    for i in range(psize):
        cmd = "taskset -cp %s %s" % (task_clist[i], plist[i])
        status, output = commands.getstatusoutput(cmd)
        if status:
            print "taskset hit error"
            print output
            sys.exit(1)
        print output		


cmd = "top -p %s" % p_str
os.system(cmd)
