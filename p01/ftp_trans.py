import ftplib
import config
import getpass
import error

class FtpTrans:

    def __init__(self):
        self.recur_times = {"mkdir":0, "connect":0, "chdir":0, \
                "copy_file":0, "close":0,}

    def connect(self):
        passwd = "ma5dr%S-"
        user_str = "illuminaP01"
        try: 
            self.ftp_handle = ftplib.FTP("bisr.osumc.edu", \
                                         user_str, passwd)
        except socket.error, ftplib.error_temp:
            self.recurse("connect")


    def mkdir(self, file):
        try:
            self.ftp_handle.mkd(file)
        except ftplib.error_temp:
            self.recurse("mkdir", file)

    def chdir(self, name):
        try:
            self.ftp_handle.cwd(name)
        except ftplib.error_temp:
            self.recurse("chdir", name)

    def copy_file(self, file):
        file_handle = open(file, "rb")
        try:
            self.ftp_handle.storbinary("STOR %s" %file, file_handle)
        except ftplib.error_temp:
            self.recurse("copy_file", file)

    def close(self):
        try:
            self.ftp_handle.sendcmd("quit")
        except ftplib.error_temp:
            self.recurse("close")
        self.ftp_handle.close()

    def recurse(self, fun_name, para = None):
        self.recur_times[fun_name] += 1
        if self.recur_times[fun_name] > 5:
            raise error.FtpRecuError(fun_name, \
                                     self.recur_times[fun_name])
        if fun_name == "mkdir":
            self.mkdir(para)
        elif fun_name == "chdir":
            self.chdir(para)
        elif fun_name == "copy_file":
            self.copy_file(para)
        elif fun_name == "close":
            self.close()
        elif fun_name == "connect":
            self.connect()


