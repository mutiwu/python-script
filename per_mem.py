#!/usr/bin/env python
# coding=utf-8
import commands
import time
import os
import re


dirdata = time.ctime().replace(' ', '_')
tmpath = "/tmp/stream%s" %dirdata
finaldata = "%s/finaldata" %tmpath

if os.path.exists(tmpath):
    print "won't create new dir, quit the script."
    os.sys.exit(1)
os.mkdir(tmpath)
status, output = commands.getstatusoutput("gcc -fopenmp -D_OPENMP stream.c -o stream")
if status:
    print "compile failed, please check"
    print output
    os.sys.exit(1)
status, output = commands.getstatusoutput("export OMP_NUM_THREADS=256")
if status:
    print "export OMP treads failed, please check"
    print output
    os.sys.exit(1)
pr = {"Copy":[], "Scale":[], "Add":[], "Triad":[]}
for i in range(1, 6):
    countfile = "%s/stream_rst_%s" %(tmpath, i)
    if os.path.exists(countfile):
	print "The %s already exists, quit" %countfile
	os.sys.exit(1)
    status, output = commands.getstatusoutput("./stream")
    if status:
        print "stream hit error, need check"
        print output
        os.sys.exit(2)
    f = file(countfile, "w+")
    f.write(output)
    f.write("\n")
    f.close()
    for p in pr.keys():
        patn = re.compile(r"%s:\s+(\d+\.\d+)" %p)
        pr[p].append(float(patn.search(output).group(1)))

if os.path.exists(finaldata):
    tmpdate = time.ctime().replace(' ', '_')
    print "the finaldata already exists, will mv it as finaldata%s" %tmpdate
    status, output = commands.getstatusoutput("mv %s %s%s" %(finaldata, finaldata, tmpdate))
    if status:
        print "failed to mv, will quit the script."
        print output
        os.sys.exit(1)

f = file(finaldata, "a+")
tmplist = ['\t\t', 'AvaBW', '\n']
f.writelines(tmplist)
f.close()
for p in pr.keys():
    fv = sum(pr[p])/5
    tmplist = [p, '\t\t', str(fv), '\n']
    f = file(finaldata, "a+")
    f.writelines(tmplist)
    f.close()
