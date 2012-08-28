#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
#!/usr/bin/python
import paramiko
import os

class SFtp(object):

    def __init__(self, server, uname, passwd):
        host = server
        port = 22
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username = uname,\
                password = passwd)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def close(self):
        self.sftp.close()
        self.transport.close()

    def copy_file(self, srcname, destname):
        self.sftp.put(srcname, destname)


if __name__=="__main__":
    os.system("touch test_file")
    import config
    sftp_obj = SFtpTrans(config.Parameters('conf_test.txt'))
    print sftp_obj.passwd, sftp_obj.uname
    sftp_obj.connect()
    sftp_obj.copy_file('test_file', '/data/repos/solexa/bisr_test/test_file')
    #sftp_obj.sftp.get('temp', '.')
    sftp_obj.close()
    os.system('rm test_file')
    print "remove test_file from sftp server"

#import sys
#path =  sys.argv[1]    #hard-coded
#localpath = sys.argv[1]
#sftp.put(localpath, path)
#sftp.get(path, "temp\\"+path)

#sftp.close()
#transport.close()
#print 'Upload done.'

