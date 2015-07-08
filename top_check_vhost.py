#!/usr/bin/env python
import os

pid_vhost = os.popen('pgrep vhost')

list_pids = pid_vhost.readlines()
if list_pids == [] :
    print '\nQuit:No vhost threads available.\n'
    os._exit(0)
print 'list_pids:', list_pids
list_pids_str = ','.join([i.strip('\n') for i in list_pids])
os.system('top -p %s' % list_pids_str)

print 'top result', list_pids_str
   

