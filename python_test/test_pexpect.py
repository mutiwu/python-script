#!/usr/bin/env python
# coding=utf-8

import pexpect
import os
import sys

class Sess(object):


    def __init__(self, user, ip, passwd):
        self.user = user
        self.ip = ip
        self.passwd = passwd
        if self.user == 'root':
            self.usersep = '#'
        else:
#            self.usersep = os.linesep + '$'
            self.usersep = '$'

    def prt(self, str):
        printline = os.linesep + '>' * 10
        print printline
        print str


    def login(self):
        cmd = 'ssh -l %s %s' % (self.user, self.ip)
        self.child = pexpect.spawn(cmd)
        self.child.logfile_read = sys.stdout
#        self.runcmd(ptn='password:',cmd=self.passwd)
        self.runcmd(ptn='test@172.16.136.14\'s password:', cmd=self.passwd)

    def chkptn(self, ptn):
        if ptn:
            index = self.child.expect([ptn, pexpect.EOF, pexpect.TIMEOUT])
            if index == 1:
                self.prt("expect hit EOF")
                os._exit(index)
            elif index == 2:
                self.prt("expect hit EOF")
                os._exit(index)

    def runcmd(self,ptn=None,ptn2=None,cmd=None):
        self.chkptn(ptn)
        icmd = cmd + os.linesep
        self.child.send(icmd)
        if ptn2 is None:
            ptn2 = self.usersep
        self.chkptn(ptn2)
        self.prt(('The before of the expect(%s) '
                  'that after sending cmd \'%s\' '
                  'is: %s' % (str(ptn2), cmd, self.child.before)))
        self.prt(('The after of the expect(%s) '
                  'that after sending cmd \'%s\' '
                  'is: %s' % (str(ptn2), cmd, self.child.after)))

    def logout(self):
        exitcmd = 'exit' + os.linesep
        self.child.send(exitcmd)

if __name__ == '__main__':
    def main(user, ip, passwd):
        try:
            sessrun = Sess(user,ip,passwd)
            sessrun.login()
            sessrun.runcmd(cmd='whoami')
            sessrun.runcmd(cmd='pwd')
        finally:
           # sessrun.logout()
           pass

    user = 'root'
    ip = '172.16.236.80'
    passwd = 'teamsun'
    main(user, ip, passwd)


