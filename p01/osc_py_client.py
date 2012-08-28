#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import xmlrpclib
import sys

import socket
#s = xmlrpclib.ServerProxy('http://'+socket.gethostname()+':'+\
        #sys.argv[1])
s = xmlrpclib.ServerProxy('http://10.127.24.50:'+\
        sys.argv[1])
#print s.pow(2,3)  # Returns 2**3 = 8
print s.add(2,3)  # Returns 5
#print s.div(5,2)  # Returns 5//2 = 2

# Print list of available methods
print s.system.listMethods()
#print s.TestCall('1','2','3','4',1)
print s.stop()

