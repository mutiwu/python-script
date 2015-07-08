import os
import sys
from multiprocessing import Process
from multiprocessing import Pool
def promisc_reload(counts):
    try:
        if_name = sys.argv[1]
    except IndexError:
        print 'the first argv should be the interface name'
        os.sys.exit(0)
    print os.getpid()
    for i in range(counts):
        os.system('ifconfig %s promisc' % if_name)
        os.system('ifconfig %s -promisc' % if_name)
#        print 'promisc enabled %s times' % (i+1)
    print '====*promisc finished*===='
def ping(p_counts):
    print os.getpid()
    os.system('ping 10.66.9.130 -c %s' % p_counts)
    print '====*ping finished*===='    
def netperf(times):
    print os.getpid() 
    os.system('netperf -H 10.66.9.130 -l %s' % times)
    print '====*netperf finished*===='
if __name__ == '__main__':
    try: 
        p_counts = int(sys.argv[2])
        counts = int(sys.argv[3])
        times = int(sys.argv[4])
    except IndexError:
        sp1 = 'try xx.py interface_name promisc_reload_times'
        sp2 = 'ping_times netperf_times'
        print sp1 + sp2
        os.sys.exit(0)
    p0 = Process(target=promisc_reload, args=(p_counts,))
    p1 = Process(target=ping, args=(counts,))
    p2 = Process(target=netperf, args=(times,))
    pa = [p0, p1, p2]
    for p in pa:
        p.start()
    for p in pa:
        p.join()	    
    print '====*case  finished*===='

    


