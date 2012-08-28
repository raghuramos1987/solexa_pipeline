#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import os

from copy import Copy

class CommandOp(Copy):

    def __init__(self):
        pass

    def remove(self, fileOrDir):
        if not os.access(fileOrDir, os.F_OK):
            raise CommandError("Cannot access "+fileOrDir)
        if os.path.isdir(fileOrDir):
            os.removedirs(fileOrDir)
        else:
            os.remove(fileOrDir)
    def removeDir(self, fileOrDir):
        for root, dirs, files in os.walk(fileOrDir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def move(self, src, dest):
        if not os.access(src, os.F_OK):
            raise CommandError("Cannot access "+src)
        try:
            os.rename(src, dest)
        except OSError:
            #TODO: raghu. change this to something more informative
            #sounds too much like windows!
            if os.path.isdir(dest):
                self.copy(src, dest)
                self.remove(src)


