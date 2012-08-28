#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import os
from error import TransferError
from sftp_trans import SFtp
from copy import Copy
from rsync import Rsync

class Transfer(Rsync, SFtp, Copy):

    def __init__(self, method):
        self.methodDict = ["rsync", "copy", "sftp"]
        self.setServerFlag = 0
        self.method = method
        if self.method not in self.methodDict:
            raise TransferError(method+" type of transfer is not "+\
                                       "implemented")
        
    def setServerParams(self, server, uname, passwd):
        if self.method == "rsync":
            self.rsyncObj = Rsync(server, uname, passwd)
        elif self.method == "sftp":
            self.sftpObj = SFtp(server, uname, passwd)
   
    def copy(self, src, dest, toServer=None):
        self.copyObj = Copy()
        if self.method == "rsync":
            if not toServer == None:
                self.rsyncObj.run(src, dest, toServer)
            else:
                raise TransferError("Did not specify transfer "+\
                                         "direction")
            return
        if os.path.isdir(src):
            if self.method == "sftp":
                raise TransferError("Cannot transfer directories "+\
                                     "using sftp")
            else:
                self.copyObj.copytree(src, dest)
        else:
            if self.method == "sftp":
                if os.path.isdir(dest):
                    raise TransferError("Cannot transfer to dir "+\
                                        "using sftp")
                self.sftpObj.copy_file(src, dest)
            else:
                self.copyObj.copy(src, dest)
            
