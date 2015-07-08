#!/usr/bin/env python
import os
import sys

pid_vhost = os.popen('pidof vhost')

list_pids = pid_vhost.readlines()
if list_pids == [] :
    print '\nQuit:No vhost threads available.\n'
    sys.exit(0)
print 'list_pids:', list_pids
list_pids_str = ','.join([i.strip('\n') for i in list_pids])
os.system('top -p %s' % list_pids_str)
print 'top result', list_pids_str
   

