#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
#!/usr/bin/python
import os
import error
import xmlrpclib
import ConfigParser
from string import *

class Parameters:

    def __init__(self, conf_file, isString):
        self.config = ConfigParser.ConfigParser()
        self.conf_file = conf_file
        if os.path.isfile(conf_file):
            file = open(conf_file, 'r')
            file_lines = file.readlines()
            file.close()
            self.config.read(conf_file)
        elif isinstance(conf_file, str) and isString:
            file_lines = conf_file.splitlines()
            tempFileH = open("temp", 'w')
            tempFileH.write(conf_file)
            tempFileH.close()
            self.config.read("temp")
            self.remove("temp")
        else:
            raise error.FnfError(conf_file)
        self.runid = ""
        self.root_path = ""
        self.Bustard_path = ""
        self.Gerald_path = ""
        self.backup_path = ""
        self.log_file_name = ""
        self.sftp_server = ""
        self.lane_user_dict = {}
        self.ftp_user_dict = {}
        self.sftp_user_dict = {}
        self.sid_dict = {}
        self.perm_dict = {}
        self.run_loc = ""
        self.popMain()
        #http = "http"
        http = "https"
        self.server = xmlrpclib.ServerProxy(http+"://bisr.osumc.edu/"+\
                                            "QUEST/Public/"+\
                                            "SolexaChipSeqRPC.ashx")

    def popMain(self):
        if self.config.has_option('main', 'runid'): 
            self.runid = self.config.get('main', 'runid')
            self.run_loc = self.config.get('main', 'location')
            self.sftp_server = self.config.get('main', 'sftpserver')
            self.numOfLanes = self.config.getint('main', 'numOfLanes')
        if self.config.has_section('pbs'):
            self.popCluster()

    def popCluster(self):
        self.numOfCores = self.config.getint("pbs", "numOfCores")
        self.numOfNodes = self.config.getint("pbs", "numOfNodes")
        self.wallTime = self.config.getint("pbs", "wallTime")
    
    def popCompress(self):
        self.root_path = self.config.get('compress', 'root')
        self.backup_path = self.config.get('compress', 'backup')
        self.Gerald_path = self.config.get('compress', 'Gerald')
        self.Bustard_path = self.config.get('compress', 'Bustard')
        self.log_file_name = os.path.join(self.backup_path,\
                                          self.runid)
        self.log_file_name = os.path.join(self.log_file_name, \
                                          "log_"+self.runid+\
                                          ".txt")
        self.copy_to_runid = [#os.path.join(self.Bustard_path,\
                              #"support.txt"),
                              os.path.join(self.Gerald_path,\
                                           "config.txt")]
        self.copy_to_users = [os.path.join(self.Gerald_path,\
                                           "Summary.htm"),
                              self.runid+"_summary.tar.gz"]
    def popAll(self):
        self.popCompress()
        self.popLanes()

    def popQuest(self, laneNum):
        lane = 'Lane'+str(laneNum)
        self.perm_dict[str(laneNum)] = [self.config.getboolean(lane,
                                 'compressFlag'), 
                             self.config.getboolean(lane,
                                 'transferFlag')]
        user = self.config.get(lane, 'user')
        self.lane_user_dict[str(laneNum)] = user
        sampleId = self.config.get(lane, 'sampleId')
        exptId = self.config.get(lane, 'exptId')
        folder_path = self.server.GetFolder(sampleId,\
                                            exptId)
        self.sid_dict[sampleId] = [user, str(laneNum), sampleId]
        self.sid_dict[sampleId].append("")
        if folder_path[0] == '\\':
            folder_path = folder_path[folder_path.\
                                      index('QUEST'):]
            folder_path = folder_path.replace('\\','/')
            folder_path = folder_path.replace('//','/')
            self.ftp_quest = 0
        else: 
            folder_path = folder_path[\
                          folder_path.index(":")+\
                                  3:]
        self.ftp_user_dict[str(laneNum)]= [self.sid_dict\
                            [sampleId][0], folder_path, \
                            self.sid_dict[sampleId][2],\
                            self.sid_dict[sampleId][3]]

    def popSftp(self, laneNum):
        lane = "Lane"+str(laneNum)
        self.perm_dict[str(laneNum)] = [self.config.getboolean(lane,
                                 'compressFlag'), 
                             self.config.getboolean(lane,
                                 'transferFlag')]
        user = self.config.get(lane, 'user')
        passwd = self.config.get(lane, 'passwd')
        email = self.config.get(lane, 'emailid')
        self.lane_user_dict[str(laneNum)] = user
        self.sftp_user_dict[str(laneNum)] = [user, passwd, email]

    def popLanes(self):
        # adding 1 because range in python is from 1 to n-1
        for i in range(1, self.numOfLanes+1):
            lane = 'Lane'+str(i)
            method = lower(self.config.get(lane, 'method'))
            if method == 'quest':
                self.popQuest(i)
            elif method == 'sftp':
                self.popSftp(i)
 
    def populate_val(self, file_lines):
        flag = 0
        line_num = 0
        for line in file_lines:
            if line.startswith('#') or line.isspace() or \
               not line.split():
                continue
            elif line.startswith('runid'):
                #Stores the runid for the current run of the script
                self.runid = line.split(':').pop().strip()
            elif line.startswith('root'):
                #Parent directory from where the script is run
                #Also argv[1] of the script is under this path
                self.root_path = line.split(':').pop().strip().\
                                 rstrip('/')
            elif line.startswith('Bustard'):
                self.Bustard_path = line.split(':').pop().strip().\
                                    rstrip('/')
            elif line.startswith('Gerald'):
                self.Gerald_path = line.split(':').pop().strip().\
                                   rstrip('/')
            elif line.startswith('backup'):
                #Path to backup directory
                self.backup_path = line.split(':').pop().strip().\
                                   rstrip('/')
            elif line.startswith('sftpserver'):
                self.sftp_server = line.split(':').pop().strip()
            elif line.startswith('location'):
                self.run_loc = line.split(':').pop().strip()[:3]
            self.log_file_name = os.path.join(self.backup_path,\
                                              self.runid)
            self.log_file_name = os.path.join(self.log_file_name, \
                                              "log_"+self.runid+\
                                              ".txt")
        for line in file_lines:
            line_num += 1
            if line.startswith('#') or line.isspace() or\
               not line.split():
                continue
            if line.startswith('Users'):
                flag = 1
                continue
            if line.startswith("Quest"):
                break
            if flag:
                reqd_list = line.strip('\n').split(':')
                csv_list = []
                if len(reqd_list) == 4:
                    self.perm_dict[reqd_list[1]] = reqd_list[-1]
                    self.lane_user_dict[reqd_list[1]] = reqd_list[0]
                    self.ftp_user_dict[reqd_list[1]]= [reqd_list[0],\
                                                       reqd_list[2]]
                else:
                    raise error.ConfError("Config file", line_num,\
                                          line)

        self.copy_to_runid = [#os.path.join(self.Bustard_path,\
                              #"support.txt"),
                              os.path.join(self.Gerald_path,\
                                           "config.txt")]
        self.copy_to_users = [os.path.join(self.Gerald_path,\
                                           "Summary.htm"),
                              self.runid+"_summary.tar.gz"]

    def populate_quest(self, file_lines):
        flag = 0
        line_num = 0
        for line in file_lines:
            line_num += 1
            if line.startswith('#') or line.isspace()\
               or not line.split():
                continue
            if line.startswith("Quest"):
                flag = 1
                continue
            if line.startswith("SFTP"):
                flag = 0
                continue
            if flag:
                reqd_list = line.strip('\n').split(':')
                if len(reqd_list) >= 4:
                    self.ftp_quest = 1
                    self.perm_dict[reqd_list[1]] = reqd_list[-1]
                    self.lane_user_dict[reqd_list[1]] = reqd_list[0]
                    self.sid_dict[reqd_list[2]] = [reqd_list[0],\
                                                   reqd_list[1],\
                                                   reqd_list[2]]
                    self.sid_dict[reqd_list[2]].append("")
                    folder_path = self.server.GetFolder(reqd_list[2],\
                                                        reqd_list[3])
                    if folder_path[0] == '\\':
                        folder_path = folder_path[folder_path.\
                                                  index('QUEST'):]
                        folder_path = folder_path.replace('\\','/')
                        folder_path = folder_path.replace('//','/')
                        self.ftp_quest = 0
                    else: 
                        folder_path = folder_path[\
                                      folder_path.index(":")+\
                                              3:]
                    print folder_path
                    self.ftp_user_dict[reqd_list[1]]= [self.sid_dict\
                            [reqd_list[2]][0], folder_path, \
                            self.sid_dict[reqd_list[2]][2],\
                            self.sid_dict[reqd_list[2]][3]]
                else:
                    raise error.ConfError("Config file",\
                                          line_num, line)
    def pop_sftp(self, file_lines):
        flag = 0
        line_num = 0
        for line in file_lines:
            line_num += 1
            if line.startswith('#') or line.isspace()\
               or not line.split():
                continue
            if line.startswith("SFTP"):
                flag = 1
                continue
            if line.startswith("Quest"):
                flag = 0
                continue
            if flag:
                reqd_list = line.strip('\n').split(':')
                if len(reqd_list) == 5:
                    self.perm_dict[reqd_list[1]] = reqd_list[-1]
                    self.lane_user_dict[reqd_list[1]] = reqd_list[0]
                    self.sftp_user_dict[reqd_list[1]] = \
                            [reqd_list[0], reqd_list[2], reqd_list[3]]
                else:
                    raise error.ConfError("Config file",\
                                          line_num, line)
                    


if __name__=='__main__':
    import sys
    conf_obj = Parameters(sys.argv[1], 0)
    print conf_obj.runid, conf_obj.root_path, conf_obj.Bustard_path,\
          conf_obj.Gerald_path, conf_obj.backup_path, conf_obj.log_file_name,\
          conf_obj.lane_user_dict
    print conf_obj.root_path+"\n"+conf_obj.Bustard_path+"\n"+\
              conf_obj.Gerald_path+"\n"+ conf_obj.backup_path+"\n"+\
              conf_obj.runid

    print "\n\n"
    print conf_obj.sftp_server
    print conf_obj.perm_dict
    
    print conf_obj.ftp_user_dict
