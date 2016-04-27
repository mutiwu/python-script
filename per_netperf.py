#!/usr/bin/env python
# coding=utf-8
import os
import re
import time

dirdata = time.ctime().replace(' ', '_')
tmpath = "/tmp/per_net%s" %dirdata

if os.path.exists(tmpath):
    print "won't create new dir, quit the script."
    os.sys.exit(1)
os.mkdir(tmpath)
optl = 5
insts = 5
proto = ["TCP_STREAM", "TCP_MAERTS"]
psize = ["64", "4096", "65535"]
server_ip = "172.30.132.70"
cmd = "taskset -c %s netperf -H %s -l %s -C -c -t %s -- -m %s >>%s & "
for t in proto:
    finallist = ['Size', '\n', t, '\n']
    tpath = "%s/%s" %(tmpath, t)
    if os.path.exists(tpath):
        print "%s already exists, quit the script." %tpath
        os.sys.exit(1)
    os.mkdir(tpath)
    finaldata = "%s/finaldata_%s" %(tpath, t)
    f = file(finaldata, "a+")
    f.writelines(finallist)
    f.close()
    for ps in psize:
        stpath = "%s/%s" %(tpath, ps)
        if os.path.exists(stpath):
            print "%s already exists, quit the script." %stpath
            os.sys.exit(1)
        os.mkdir(stpath)
        stlist = []
        for c in range(1, 6):
            countfile = "%s//rs_%s_%s_c%s" %(stpath, t, ps, c)
            for i in range(1, (int(insts) + 1)):
#                status, output = commands.getstatusoutput(cmd %(i, server_ip, optl, t, ps, countfile))
                if os.system(cmd %(i, server_ip, optl, t, ps, countfile)):
                    print "Netperf hit wrong, quit"
                    os.sys.exit
            sleep_time = int(optl) + 3
            time.sleep(sleep_time)
            f = file(countfile, "r")
            tmpstr = 'flag'.join(f.readlines())
            f.close()
            pp = re.compile(r"\nflag\s+\d+\s+\d+\s+\d+\s+\d+\.\d+\s+(\d+\.\d+)")
            tmplist = pp.findall(tmpstr)
            stlist.append(float(sum([float(i) for i in tmplist])))
        stfinalrs = sum(stlist)/5
        valuelist = [ps, '\t', str(stfinalrs), '\n']
        f = file(finaldata, "a+")
        f.writelines(valuelist)
        f.close()

