#!/usr/bin/python
import glob
import copy 
import time
import os
import re
import sys
import commands
import config
import logging
import ftp_trans
import xmlrpclib
import mail
import error
import sftp_trans
import traceback
from commandOp import CommandOp
from transfer import Transfer

#Importing this to just id the error. Check function ftp_files
import ftplib


class CatTar(CommandOp):
    ##################################################################
    # This function is called when an object of the class is created.
    # 
    # We basically define required parameters and extract relevant 
    # command line information.
    # 
    ##################################################################
    def __init__(self, conf_obj):
        """This class returns an object which has the required 
        configuration values. Please add/delete data from __init__ 
        to suit requirements."""
        self.test = 0
        self.conf_obj = conf_obj
        self.transSftp = Transfer('sftp')
        #for next version this should be changed to 
        #ftp_trans.FtpTrans(self.conf_obj)
        self.ftp_obj = ftp_trans.FtpTrans()
        self.runid = self.conf_obj.runid
        self.backup_dir = self.conf_obj.backup_path
        #Change below code to modify logging format
        if(not os.path.isdir(self.backup_dir)):
            raise error.FnfError(self.backup_dir, 
                                 "Error: backup dir not found"+\
                                  self.backup_dir+"; Exiting")
        self.root_dir = self.conf_obj.root_path
        self.runid_dir = os.getcwd()
        self.transCopy = Transfer('copy')
        self.summaryName = ""

    ##################################################################
    # Creates directories of users under backup directory
    # Calls calcpath for further processing (for every lane and for 
    # every user
    ##################################################################
    def create_dir(self):
        logging.debug("dir list: "+str(self.conf_obj.lane_user_dict))
        for lane, name in self.conf_obj.lane_user_dict.iteritems():
            if not self.conf_obj.perm_dict[lane][0]:
                continue
            os.chdir(self.runid_dir)
            self.s_what = "s_"+lane+"_"
            if not os.path.isdir(name):
                os.mkdir(name)
                #Recreating dir tree on the ftp server
            os.chdir(name)
            self.cur_name_dir = os.getcwd()
            self.calcpath()
        self.add_htm()
    
    ##################################################################
    #This function populates different path variables and calls concat
    #as many times as required. Concat handles further processing
    ##################################################################
    def calcpath(self):
        self.Bustard_path = self.conf_obj.Bustard_path
        self.Gerald_path = self.conf_obj.Gerald_path
        os.chdir(self.Bustard_path)
        reqd_list = commands.getoutput("ls "+self.s_what+\
                                       "[1-9]_*_qseq.txt").split("\n")
        ind = []
        try:
            ind.append(reqd_list[0].split('_')[2])
        except IndexError:
            logging.debug("here is the problem causing ind "+str(ind))
        #The below for loop takes care of the case where there could 
        #be 2 kinds of files for same lane. 
        #Example:s_2_1_... s_2_2_...
        for file in reqd_list:
            if file.split('_')[2] not in ind:
                ind.append(file.split('_')[2])
        #Files which need to be included in the tar file. You could 
        #directly add to this list to make things easier
        for i in ind:
            #if there is only one set of files for every lane
            if len(ind) == 1:
                self.files = {self.s_what+'eland_extended.txt':'', 
                              self.s_what+'sequence.txt':'', 
                              self.s_what+'sorted.txt':'', 
                              self.s_what+'export.txt':''}
            #otherwise more than one set of files
            else:
                self.files = {self.s_what+i+'_'+'eland_extended.txt'\
                              :'', 
                              self.s_what+i+'_'+'sequence.txt':'', 
                              self.s_what+i+'_'+'sorted.txt':'', 
                              self.s_what+i+'_'+'export.txt':''}
            #Add in paths where corresponding files can be found
            for file in self.files.iterkeys():
                if not file.endswith("qseq.txt"):
                    self.files[file] = self.Gerald_path
                else:
                    self.files[file] = self.Bustard_path
            self.concat(i)


    ##################################################################
    # Concatenates all txt files under Bustard
    ##################################################################
    def concat(self, i_str):
        #Separate out the name of the current user. 
        #Used only for logging purposes
        cur_name = self.cur_name_dir.split("/")[-1]
        os.chdir(self.Bustard_path)
        concat_files = ''
        reqd_list = commands.getoutput("ls "+self.s_what+i_str+\
                                       "_*_qseq.txt").split("\n")
        logging.info("Starting loop for user "+cur_name)
        for file in reqd_list:
            concat_files += file +' '
        logging.info("Starting concatenation of files")
        logging.debug("Starting concatenation of files under "+\
                      self.Bustard_path)
        logging.debug('cat '+self.s_what+i_str+'_qseq.txt ')
        if(self.test):
            print 'cat '+concat_files+'> '+\
                  os.path.join(self.cur_name_dir,\
                  self.s_what+i_str)+'_qseq.txt \n'
        else:
            os.system('cat '+concat_files+'> '+\
                      os.path.join(self.cur_name_dir,\
                      self.s_what+i_str)+'_qseq.txt ')
        logging.info("Finished concatenation of files")
        logging.debug("Finished concatenation of files under "+\
                      self.Bustard_path)
        self.copy_tar()

    ##################################################################
    # Copies all files under Bustard and Gerald to the path for the 
    # user. Then tars the files.
    ##################################################################
    def copy_tar(self):
        all_paths = ''
        #Put all files to be copied in a single string
        #Will it be better to do it one by one?
        for file, path in self.files.iteritems():
            all_paths += os.path.join(path, file) + ' '
        logging.info("Starting copying of files")
        logging.debug("Starting copying of files under "+\
                      self.Bustard_path+" and "+ self.Gerald_path+\
                      " to "+self.cur_name_dir)
        logging.debug("cp "+all_paths+" "+self.cur_name_dir)
        if(self.test):
            print "cp "+all_paths+" "+self.cur_name_dir+"\n"
        else:
            for f in all_paths.split():
                self.transCopy.copy(f.strip(), self.cur_name_dir)
        logging.info("Finished copying of files")
        os.chdir(self.cur_name_dir)
        logging.info("Renaming of files")
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                if(self.test):
                    print "mv "+file+" "+self.runid+'_'+file+"\n"
                else:
                    #TODO: raghu. check error
                    self.move(file, self.runid+'_'+file)
        for file in os.listdir(os.getcwd()):
            if file.endswith(".txt"):
                logging.info("Starting tarring of file "+file)
                logging.debug("gzip "+file)
                if(self.test):
                    print "gzip "+file
                else:
                    os.system("gzip "+file)
                logging.info("Finished tarring of file "+file)
    
    ##################################################################
    #Copies summary, plots and htm from Bustard and Gerald into a temp
    #directory. Tars the temp directory and deletes the intermediate 
    #directory.
    ##################################################################
    def add_htm(self):
        self.Bustard_path = self.conf_obj.Bustard_path
        self.Gerald_path = self.conf_obj.Gerald_path
        logging.info("Starting summary tar creation")
        os.chdir(self.runid_dir)
        os.mkdir(self.runid+"summary")
        os.chdir(self.runid+"summary")
        logging.info("Copying htm files from Bustard")
        for file in glob.glob(os.path.join(self.Bustard_path, 
                  "*.[hH][Tt][Mm]")):
            self.transCopy.copy(file, ".")
        logging.info("Copying Plots folder from Bustard")
        self.transCopy.copy(os.path.join(self.Bustard_path, "Plots"),
                        os.path.join(os.getcwd(),"Plots"))
        os.mkdir(self.Gerald_path.split('/')[-1])
        os.chdir(self.Gerald_path.split('/')[-1])
        logging.info("Copying htm files from Gerald ")
        for file in glob.glob(os.path.join(self.Gerald_path, 
                                     "*.[hH][Tt][Mm]")):
            self.transCopy.copy(file, ".")
        logging.info("Copying Plots folder from Gerald") 
        self.transCopy.copy(os.path.join(self.Gerald_path, "Plots"),
                      os.path.join(os.getcwd(), "Plots"))
        logging.info("Starting tarring of Summary")
        os.chdir(self.runid_dir)
        os.system("tar -czf "+self.runid+"_summary.tar.gz "+\
                  self.runid+"summary")
        logging.info("Finished tarring of Summary")
        self.copy_file()
    
    ##################################################################
    # Copies the required files for different users.
    ##################################################################
    def copy_file(self):
        logging.info("Making copies of summary tar")
        os.chdir(self.runid_dir)
        logging.debug(self.conf_obj.copy_to_runid)
        logging.debug(self.conf_obj.copy_to_users)
        logging.debug(str(self.conf_obj.lane_user_dict)+" HI")
        for file in self.conf_obj.copy_to_runid:
            self.transCopy.copy(file, os.getcwd())
        for file in self.conf_obj.copy_to_users:
            for name in self.conf_obj.lane_user_dict.itervalues():
                self.transCopy.copy(file, name)
                if file.split('/')[-1] == 'Summary.htm':
                    os.chdir(name)
                    logging.debug("Renaming Summary.htm "+os.getcwd())
                    self.move('Summary.htm', self.runid+'_Summary.htm')
                    os.chdir('..')
        os.chdir(self.runid_dir)
        self.removeDir(self.runid+"summary")

    def ftp_files(self):
        i = 0
        #############################################################
        #name_folder format
        #
        #1. For Non-quest
        #   Length of list = 2
        #   [<name of user>, <folder to cd to on quest>]
        #2. For Quest
        #   Length of list = 4
        #   [<name of user>, <folder to cd to on quest>, <sample id>,
        #    <experiment id>]
        #############################################################
        for lane, name_folder in self.conf_obj.ftp_user_dict.\
                iteritems():
            if not self.conf_obj.perm_dict[lane][1]:
                continue
            os.chdir(self.runid_dir)
            os.chdir(name_folder[0])
            file_list = commands.getoutput("ls *s_"+lane+"*").\
                                           split("\n")
            file_list.append(self.runid+"_summary.tar.gz")
            file_list.append(self.runid+"_Summary.htm")
            if len(name_folder) < 4:
                self.ftp_obj.connect()
                self.ftp_obj.chdir(name_folder[1])
                try:
                    self.ftp_obj.mkdir(self.runid)
                except ftplib.error_perm:
                    self.ftp_obj.connect()
                    self.ftp_obj.chdir(name_folder[1])
                    logging.debug("runid dir already there")
                self.ftp_obj.chdir(self.runid)
                try:
                    self.ftp_obj.mkdir(name_folder[0])
                except ftplib.error_perm:
                    self.ftp_obj.connect()
                    self.ftp_obj.chdir(name_folder[1])
                    self.ftp_obj.chdir(self.runid)
                    logging.debug("user dir also already there")
                self.ftp_obj.chdir(name_folder[0])
            else:
                if self.conf_obj.ftp_quest:
                    self.ftp_obj.connect()
                    self.ftp_obj.chdir(name_folder[1])
            for file in file_list:
                logging.info("Transferring file %s of user %s" \
                        %(file, name_folder[0]))
                if self.conf_obj.ftp_quest:
                    self.ftp_obj.copy_file(file)
                else:
                    self.transCopy.copy(file, '/cccstor/'+\
                              name_folder[1]+'/'+file)
                    logging.debug('cp '+file+' /cccstor/'+\
                              name_folder[1]+'/'+file)
            if self.conf_obj.ftp_quest:
                self.ftp_obj.close()
            logging.info("Finished transfer !!!")
            if len(name_folder) == 4:
                sid = name_folder[2]
                eid = name_folder[3]
                self.conf_obj.server.UpdateQuestSampleResults(sid,\
                                     eid, file_list, self.runid, \
                                     "IlluminaGAII", "heWex45--")
    def sftp_files(self):
        #name_folder = [uname, passwd, email id]
        for lane, name_folder in self.conf_obj.sftp_user_dict.\
                iteritems():
            if not self.conf_obj.perm_dict[lane][1]:
                continue
            os.chdir(self.runid_dir)
            os.chdir(name_folder[0])
            file_list = commands.getoutput("ls *s_"+lane+"*").\
                                           split("\n")
            file_list.append(self.runid+"_summary.tar.gz")
            file_list.append(self.runid+"_Summary.htm")
            self.transSftp.setServerParams(self.conf_obj.sftp_server,
                                           name_folder[0],
                                           name_folder[1])
            for file in file_list:
                logging.info("Transferring file %s of user %s" \
                        %(file, name_folder[0]))
                self.transSftp.copy(file, "/data/repos/solexa/"+\
                        name_folder[0]+"/"+file)
            self.mail_obj = mail.Mail()
            if(name_folder[2] != ""):
                email_text = "Results for Illumina run "+self.runid+\
                             " has been uploaded to our SFTP server.\n"+\
                             "SFTP server: "+self.conf_obj.sftp_server+\
                             "\nUsername: "
                email_text += name_folder[0]+"\nPassword: "+\
                              name_folder[1]+"\n"
                email_text += "Use winscp to download the files\n"+\
                              "http://winscp.net/eng/download.php\n"
                email_text += "\nRegards,\n\n"+\
                "Biomedical Informatics Shared Resource\n"+ \
                "The Ohio State University Comprehensive Cancer"+\
                "Center\n"+\
                "210 Biomedical Research Tower\n 460 W 12th Ave\n"+\
                "Columbus, OH 43210\n (614) 366-1538\n"
                self.mail_obj.mail_diff(name_folder[2], \
                                        "Illumina run "+self.runid, \
                                        email_text)

class Main:
    def __init__(self, config_obj):
        if len(sys.argv) < 2:
            raise error.UsageError("Usage: ./cat_tar.py "+\
                                   "<config_file_name>")
        self.conf_obj = config_obj
        self.main_obj = CatTar(self.conf_obj)
        self.flag = 1
        while(self.flag):
            self.check()
            if self.flag == 0:
                break
            time.sleep(900)

    def check(self):
        result = commands.getoutput("ls "+\
                                    self.conf_obj.\
                                    Gerald_path+"/finished.txt")
        if result.strip("\n").split("/")[-1] == "finished.txt":
		self.main()
		self.flag = 0
		os.chdir(self.conf_obj.runid)
		mail.Mail(self.conf_obj.runid, "SUCCESS",\
			  [self.conf_obj.log_file_name, 
			   'errorlog.txt', 'stdoutlog.txt'])

    def main(self):
        self.main_obj.create_dir()
        self.main_obj.ftp_files()
        self.main_obj.sftp_files()


if __name__ == '__main__':
    conf_obj = config.Parameters(sys.argv[1], 0)
    conf_obj.popAll()
    os.chdir(conf_obj.backup_path)
    try:
        os.mkdir(conf_obj.runid)
    except OSError:
        print "Directory already there"
    os.chdir(conf_obj.runid)
    logging.basicConfig(level = logging.DEBUG, 
                        format= \
                        '%(asctime)s %(levelname)s %(message)s',
                        filename = conf_obj.log_file_name,
                        filemode = 'w')
    temp_stderr = sys.stderr
    full_path = os.path.join(conf_obj.backup_path, conf_obj.runid)
    fstderr = open(full_path+"/errorlog.txt", "w")
    sys.stderr = fstderr
    temp_stdout = sys.stdout
    fstdout = open(full_path+"/stdoutlog.txt", "w")
    sys.stdout = fstdout
    flag = 1
    try:
        outer_obj = Main(conf_obj)
    except Exception, err:
        traceback.print_exc()
        fstderr.close()
        sys.stderr = temp_stderr
        fstdout.close()
        sys.stdout = temp_stdout
        #raise own error here and handle it in the main
        #if block
        os.chdir(conf_obj.backup_path)
        os.chdir(conf_obj.runid)
        os.getcwd()
        mail.Mail(conf_obj.runid, "FAILED",\
                  [conf_obj.log_file_name, 
                   'errorlog.txt', 'stdoutlog.txt'])
        flag = 0
    if flag:
        sys.stderr = temp_stderr
        fstderr.close()
        sys.stdout = temp_stdout
        fstdout.close()

