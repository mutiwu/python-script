#!/usr/bin/env python
# coding=utf-8
#import winpexpect
import pexpect
import os
import sys
import time
try:
#    cli = "plink -ssh root@172.16.236.154"
    cli = "ssh test@172.16.136.14"
#    child = winpexpect.winspawn(cli)
    child = pexpect.spawn(cli)
    child.logfile_read = sys.stdout
    child.expect('password:')
    child.send('teamsun\n')
#    child.expect('KeyPin:')
#    child.send('1234\n')
    child.expect('\$')
#    time.sleep(1)
    child.send('whoami\n')
    child.expect('\$')
    child.send('pwd\n')
    child.expect('\$')
#    print child.before.split('\r\n')
finally:
    child.send('exit\n')
