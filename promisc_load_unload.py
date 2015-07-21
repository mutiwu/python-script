import sys
import commands
import re
import getopt
import time
import threading
import signal
def promisc_reload(prses, if_name, timeout):
    time.sleep(3
    stattime = time.time())
    while True:
        pid = [ commands.getoutput("pidof %s" % prs) for prs in prses ]
        if not ( pid[0] and pid[1] ):
            break
        cmd_e = "ifconfig %s promisc" % if_name
        cmd_d = "ifconfig %s -promisc" % if_name
        status = commands.getstatusoutput(cmd_e)[0]
        print "enable promisc"
        time.sleep(2)
        if status:
            print "when try to enable promisc, hit error, please check."
            sys.exit(1)
        status = commands.getstatusoutput(cmd_d)[0]
        print "disable promisc"
        if status:
            print "when try to disable promisc, hit error, please check."
            sys.exit(1)
        endtime = time.time()
        timegap = endtime - stattime
        if timegap == timeout:
            break
def ping(host_ip, if_name, p_counts):
    cmd = "ping %s -I %s -c %s" % (host_ip, if_name, p_counts)
    status, result = commands.getstatusoutput(cmd)
    ptn = re.compile(r"(\d+)\% packet loss")
    ploss = ptn.findall(result)[0]
    if status:
        print "ping hit error, please retest, or check if ping works well"
        sys.exit(0)
    if int(ploss) > 5:
        print "%s packet loss, case failed" % ploss
        sys.exit(1)
    print "ping works well, %s%% packet loss passed" % ploss
      
def netperf(host_ip, times, n_proto):
    cmd = "netperf -H %s -l %s -t %s" % (host_ip, times, n_proto)
    status, result = commands.getstatusoutput(cmd)
    ptn = re.compile(r"(\d+\.\d+)\s+$")
    tput = ptn.findall(result)[0]
    if status:
        print "netperf hit issue, please retest, or check if netperf works"
    if float(tput) <= 4000.0:
        print "netperf performance %s bad, result %s" % (tput, result)
        sys.exit(1)
    print "netperf passed, performance is %s, result is %s" % (tput, result)

def usage():
    return '''-p $netperf_proto -t $netperf_times -i $host_ip -I $test_iface
    --help\tusage
    '''
def exit_handle(signum):
    print "signal number is %s , exit" % signum
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_handle)
    signal.signal(signal.SIGTERM, exit_handle)
    n_protos = ["TCP_STREAM", "UDP_STREAM",]
    n_proto = n_protos[0]
    times = 60
    host_ip = "10.66.9.130"
    if_name = "eth0"
    prses = ["ping", "netperf"]
    try: 
        opts, args = getopt.getopt(sys.argv[1:], "p:t:i:I:", ['help',])
    except getopt.GetoptError:
        print "wrong typing, usage:"
        print usage()
        sys.exit(1)
    for name, value in opts:
        if name == "-p":
            if value not in n_protos:
                print "only support %s" % ','.join(n_protos)
                sys.exit(1)
            n_proto = value
        if name == "-t":
            if int(value) < 10:
                print "-t should larger than 9"
                sys.exit(1)
            times = value
        if name == "-i":
            host_ip = value
        if name == "-I":
            if_name = value
    if ('--help', '') in opts:
        print usage()
        sys.exit(0)
    p_counts = int(times) * 2
    timeout = float(p_counts) * 1.5
    print n_proto, times, p_counts, timeout, host_ip, if_name
    p1 = threading.Thread(target=promisc_reload, args=(prses, if_name, timeout))
    p2 = threading.Thread(target=ping, args=(host_ip, if_name, p_counts))
    p1.start()
    if not p1.isAlive():
        print "promisc process is not alive"
        sys.exit(1)
    p2.start()
    if not p2.isAlive():
        print "ping process is not alive"
        p1.join(10)
        sys.exit(1)
    netperf(host_ip, times, n_proto)
    p2.join(timeout)
    p1.join(timeout)
    
    

    


