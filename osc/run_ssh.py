#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import pexpect
import sys


class SSH_cmd:

    def __init__(self, server, uname, passwd):
        self.server = server
        self.uname = uname
        self.passwd = passwd

    def run(self, cmd, out_file):
        temp = 'ssh '+self.uname+'@'+self.server
        self.child = pexpect.spawn(temp)
        self.child.logfile = out_file
        i = 0
        self.child.expect(['password:'], timeout=None)
        self.child.sendline(self.passwd)
        flag = 1
        while i == 0:
        #try:
            #warning... assuming that osc always says 'password:'
            self.child.expect(['[#\$] '], timeout=None)
            if flag:
                self.child.sendline(cmd)
                flag = 0
            else:
                self.child.sendline('logout')
                i = 1
        #self.child.expect([pexpect.EOF], timeout=None)
        #if i == 1:
            #self.child.sendline(cmd)
            #flag = 0

if __name__ == '__main__':
    passwd = "A706412O" 
    a = SSH_cmd('glenn.osc.edu', 'osu5422', passwd)
    a.run("/usr/bin/python /nfs/03/osu5422/try.py", sys.stdout)
