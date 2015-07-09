import os
import sys
for i in range(100):
    try:
        nic_module = sys.argv[1]
    except IndexError:
        print 'usage:python x.py $nic_module'
        os.sys.exit(0)
    os.system('modprobe -r %s' % nic_module)
    os.system('modprobe %s' % nic_module)
    os.system('service network restart')
    print 'finished load/unload for %s times' % (i+1)

os.system('ping 10.66.9.130 -c 10')
os.system('netperf -H 10.66.9.130 -l 10')
