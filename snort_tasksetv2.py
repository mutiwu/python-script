#!/usr/bin/env python
# coding=utf-8
import commands
import sys
import re
import os
import argparse
import random

parser= argparse.ArgumentParser()
parser.add_argument("prog", metavar="N", type=str, help="The first CPU")
args = parser.parse_args()
p_name = args.prog

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
#    pid_snort = int(output)
    pid_int_list = output.split('\n')
    plist = []
    for pid in pid_int_list:
        cmd = "pstree -p %s" % pid
        status, output = commands.getstatusoutput(cmd)
        if status:
            print "pstree hit error, exit"
            sys.exit(1)
        re_p = re.compile(r".*?\((\d+)\)")
        pid_list = re_p.findall(output)
        plist = plist + pid_list
    p_str = ",".join(plist)
    return plist, p_str

def p_taskset(plist):
    psize = len(plist)
    status, output = commands.getstatusoutput("cat /proc/stat")
    if status:
	print "get error"
	print output
	sys.exit(1)
    re_ccpu = re.compile(r'\ncpu(\d+) ')
    curr_clist = re_ccpu.findall(output)
    curr_clist.pop(curr_clist.index('0'))
    curr_cpu_n = len(curr_clist)
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



plist, p_str = pidtree(p_name)
p_taskset(plist)
cmd = "top -p %s" % p_str
os.system(cmd)
