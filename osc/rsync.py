#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import os
import pexpect
import sys
from commands import getoutput
from getpass import getpass
from error import TransferError

class Rsync(object):

    def __init__(self, server, uname, passwd):
        self.server = server
        self.uname = uname
        self.passwd = passwd


    def run(self, source, dest, toServer):
        temp_stdout = sys.stdout
        self.fstdout = open("rsyncstdoutlog.txt", "w")
        sys.stdout = self.fstdout
        self.src = source
        self.dest = dest
        if os.path.isdir(self.src):
            self.fileList = os.listdir(self.src)
        else:
            self.fileList = self.src
        temp = self.uname+'@'+self.server+':'
        self.cmd = 'rsync -ar '
        if toServer:
            dest = temp + dest
            source += ' '
        else:
            source = '-e ssh --blocking-io '+temp+source+' '
        i = 0
        self.cmd += source+dest
        print self.cmd
        self.child = pexpect.spawn(self.cmd)
        self.child.logfile = sys.stdout
        while i == 0:
            #try:
                #warning... assuming that osc always says 'password:'
            i = self.child.expect(['password:',pexpect.EOF],
                                  timeout=None)

            if i == 0:
                self.child.sendline(self.passwd)
            #except EOF:     print 'EOF'
            #except TIMEOUT: print 'TIMEOUT'
        print 'finished'
        sys.stdout = temp_stdout
        self.fstdout.close()
        self.checkTransfer()

    def checkTransfer(self):
        self.fstdout = open("rsyncstdoutlog.txt", "r")
        reqdLine = self.fstdout.readlines()[-2]
        self.fstdout.close()
        if reqdLine.startswith("rsync error"):
            raise TransferError("Rsync failed check rsyncstdoutlog.txt")
        os.remove("rsyncstdoutlog.txt")

if __name__ == '__main__':
    temp_stdout = sys.stdout
    passwd = getpass()
    a = Rsync('glenn.osc.edu', 'osu5422', passwd)
    a.run(sys.argv[1], sys.argv[2], int(sys.argv[3]))

    # 0 indicates transfer from osc and 1 indicates transfer to osc
