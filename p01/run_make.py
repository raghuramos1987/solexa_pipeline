#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import os
import pexpect

import run_ssh
from commandOp import CommandOp
from transfer import Transfer
import config

global test
test = 0

class MakeGerald(CommandOp):

    def __init__(self, logging):
        #full path
        self.logging = logging
        self.transRsync = Transfer('rsync')

    def set_params(self, run_folder, gerald_conf, dist_conf, dest, wall):
        self.logging.debug("setting params")
        if dest == 'OSC':
            self.local = 0
            self.gerald_pl = "/nfs/03/osu5422/CASAVA/CASAVA_v1.7.0-build/bin/GERALD.pl"
        elif dest == 'P01':
            self.local = 1
            self.gerald_pl = 'GERALD.pl'
        self.config_file = gerald_conf
        self.runid = run_folder.split('_')[0]
        self.ran_pipeline = 0
        self.pbs_path = '/nfs/03/osu5422/pbs_scripts/'

        self.options = "--EXPT_DIR"
        self.root_dir = "/slxdata/solexadata/"
        self.clust_server = 'glenn.osc.edu' 
        self.clust_uname = 'osu5422' 
        self.clust_passwd = 'A706412O'
        if not self.local:
            self.all_runs = "/nfs/proj07/BISR/"
        else:
            self.all_runs = "/slxdata/solexadata/"
        if not self.local:
            self.expt_dir = self.all_runs+'illumina_runs/'+run_folder+\
                            "/Data/Intensities/BaseCalls/"
        else:
            self.expt_dir = self.all_runs+run_folder+\
                            "/Data/Intensities/BaseCalls/"
        self.run_folder = run_folder
        self.compress_conf = dist_conf
        self.conf_obj = config.Parameters(self.compress_conf, 1)
        #############################################################
        #Take these from a config???
        #############################################################
        self.ssh_obj = run_ssh.SSH_cmd(self.clust_server, 
                                       self.clust_uname, 
                                       self.clust_passwd)
        self.transRsync.setServerParams(self.clust_server,
                                        self.clust_uname,
                                        self.clust_passwd)
        self.pbs_string = "#PBS -N gerald-job-"+self.runid+"-"+\
                          str(self.conf_obj.numOfNodes)+"n"+\
                          str(self.conf_obj.numOfCores)+"p-"+\
                          "test30tiles\n#PBS -l walltime="+\
                          str(self.conf_obj.wallTime)+":00:00\n"+\
                          "#PBS -l nodes="+\
                          str(self.conf_obj.numOfNodes)+":ppn="+\
                          str(self.conf_obj.numOfCores)+\
                          "\n#PBS -j oe\n"+\
                          "#PBS -S /bin/ksh\n#PBS -m b\n"+\
                          "#PBS -m e\n\n#tdate=$(date +%T)\n\n"+\
                          "set -x\n\ncd "
        self.backup_dir = self.all_runs+"illumina_runs/\nbackup"
        self.comp_conf = "[main]\nrunid="+self.runid+"\n"+\
                         "[compress]\nroot="+self.all_runs+\
                         "illumina_runs/\nbackup="+\
                         self.all_runs+"illumina_runs/backup/\nGerald="
        #self.InitiateRsync()

    def clean_content(self, in_l):
        in_l.reverse()
        ret_l = []
        for i in in_l:
            if i.strip().endswith('directory'):
                #error?
                raw_input("should not be here")
                break
            if i.startswith('ls'):
                break
            ret_l.append(i.split('/')[-1][:-7])
        return ret_l


    def rsync_back(self):
        #if not self.ran_pipeline:
            #print "error!!!"
            #throw error
            #return
        self.runid_dir = self.backup_dir+"/"+self.runid
        self.runid_dir = "".join(self.runid_dir.split("\n"))
        for lane, name_folder in self.conf_obj.ftp_user_dict.\
                iteritems():
            temp_dir = self.runid_dir
            temp_dir = os.path.join(temp_dir, name_folder[0]) + '/'
            out_file = open("temp", 'w') 
            if not test:
                self.ssh_obj.run("ls "+temp_dir+"*s_"+lane+"*",
                                 out_file)
            else:
                print "ls "+temp_dir+"*s_"+lane+"*"
            out_file.close()
            out_file = open("temp", 'r') 
            file_cont = out_file.readlines()
            file_cont.pop()
            out_file.close()
            file_cont = self.clean_content(file_cont)
            self.remove("temp")
            file_list = file_cont
            file_list.append(self.runid+"_summary.tar.gz")
            file_list.append(self.runid+"_Summary.htm")
            for file in file_list:
                self.transRsync.copy(temp_dir+file, '/cccstor/'+\
                                   name_folder[1]+'/', 0)
                self.logging.debug("transferred "+temp_dir+file+" to /cccstor/"+name_folder[1]+"/")
                #tell quest ???
                pass 
                #rsync back to p01
            if len(name_folder) == 4:
                sid = name_folder[2]
                eid = name_folder[3]
                self.conf_obj.server.UpdateQuestSampleResults(sid,\
                                     eid, file_list, self.runid, \
                                     "IlluminaGAII", "heWex45--")
                                     #"terry", "chess")
                self.logging.debug("updated quest for "+str(file_list))
        self.logging.info("Finished run "+self.runid)
    def write_comppbs(self):
        pbs_file_n = self.runid+'compress.pbs'
        self.pbs_file_h = open(pbs_file_n, 'w')
        temp = self.run_folder.split("_")[0]
        conf_file = self.all_runs+"compression_configs/conf_"+temp+".txt"
        self.comp_pbs_string = self.pbs_string+"py_source\n"+\
                           "source ~/.bashrc\n"+\
                           "/usr/bin/python cat_gzip.py "+\
                           conf_file+\
                           "\n/usr/bin/python osc_quest.py "+\
                           conf_file+" "+self.run_folder+" 0"
        self.pbs_file_h.write(self.comp_pbs_string)
        self.pbs_file_h.close()
        self.transRsync.copy(pbs_file_n, self.pbs_path, 1)
        self.remove(pbs_file_n)
        
    def write_makepbs(self, path):
        pbs_file_n = self.runid+'.pbs'
        self.pbs_file_h = open(pbs_file_n, 'w')
        self.make_pbs_string = self.pbs_string+path+\
                           "\ntime make -j "+\
                           str(self.conf_obj.numOfCores)+\
                           "\ncd $HOME/py_source/\n"+\
                           "\n/usr/bin/python osc_quest.py "+\
                           self.all_runs+'compression_configs/conf_'+\
                           pbs_file_n.strip('.pbs')+\
                           ".txt "+self.run_folder+" 1"

        self.pbs_file_h.write(self.make_pbs_string)
        self.pbs_file_h.close()
        self.transRsync.copy(pbs_file_n, self.pbs_path, 1)
        self.remove(pbs_file_n)

    def loadConfigObj(self, runFolder):
        temp = os.getcwd()
        os.chdir(self.codeBasePath)
        os.chdir("compression_configs")
        localPath = os.path.basename("conf_"+\
                    runFolder.split("_")[0]+".txt")
        print localPath
        self.conf_obj = config.Parameters(localPath, 0)
        self.conf_obj.popAll()
        os.chdir(temp)

    def InitiateRsync(self):
        self.write_comppbs()
        self.logging.info("Finished writing compression pbs") self.logging.debug("Starting Rsync to osc") if not os.access(self.root_dir+self.run_folder, os.F_OK):
            raise FatalError("Cannot access "+\
                             self.root_dir+self.run_folder)
        os.chdir(self.root_dir)
        if not self.local:
            self.transRsync.copy(os.path.join(os.getcwd(),self.run_folder),
                               self.all_runs+'illumina_runs/', 1)
        self.config_file = self.write_config(self.config_file,
                                             'gerald')
        self.logging.info("Finished writing Gerald config")
        temp = self.gerald_pl+' '+self.config_file+' '+\
               self.options+' '+self.expt_dir+' --make'
        self.logging.debug("Running command "+temp)
        reqd_path = self.gen_make(temp)
        self.logging.info("Path for gerald "+reqd_path)
        self.comp_conf += reqd_path+"\nBustard="
        reqd_path = '/'.join(reqd_path.rstrip('/').split('/')[:-1])
        self.comp_conf += reqd_path+"\n"
        self.compress_conf = self.write_config(self.comp_conf+\
                                               self.compress_conf,
                                               'compression')
        temp = os.getcwd()
        os.chdir(self.codeBasePath)
        self.conf_obj = config.Parameters(self.compress_conf, 0)
        os.chdir(temp)
        self.conf_obj.popAll()
        #try:
	    #self.conf_obj.server.\
		#UpdateRunStatusJobId(self.run_folder, self.job_id,'')
        #except:
	    #self.logging.info("Quest error")
        self.logging.info("Finished writing compression config")
        #temp = self.gerald_pl+' '+self.config_file+' '
        if not self.local:
            self.write_comppbs()
            self.logging.info("Finished writing compression pbs")

    def write_config(self, conf, name):
        file_n = "conf_"+self.runid+".txt"
        gerald_h = open(file_n, 'w')
        gerald_h.write(conf)
        gerald_h.close()
        self.transRsync.copy(file_n, self.all_runs+\
                      name+"_configs", 1)
        if name == "compression":
            self.move(file_n, os.path.join(self.codeBasePath, name+"_configs"))
            self.rem_comp_conf = self.all_runs+name+\
                                 "_configs/"+file_n
            return name+"_configs/"+file_n
        else:
            self.remove(file_n)
        return self.all_runs+name+'_configs/'+file_n

    def gen_compress(self):
        out_file = open("temp", 'w')
        if not test:
            self.ssh_obj.run("qsub pbs_scripts/"+self.runid+\
                             "compress.pbs", out_file)
            print "qsub pbs_scripts/"+self.runid+"compress.pbs"
        self.logging.info("Submitting compression job")
        self.logging.debug("qsub pbs_scripts/"+self.runid+\
                             "compress.pbs")
        out_file.close()
        out_file = open("temp", 'r')
        file_cont = out_file.readlines()
        out_file.close()
        self.remove("temp")
        main_line = file_cont[-2]
        self.job_id = main_line.split('.')[0]
        if test:
            job_id = '123456'
        #self.conf_obj.server.UpdateRunStatusCompressingResults(\
        #       self.run_folder, self.job_id,'')

    def gen_make(self, cmd):
        if not self.local:
            out_file = open("temp", 'w')
            if not test:
                self.ssh_obj.run(cmd, out_file)
            else:
                print cmd
            out_file.close()
        elif self.local:
            if not test:
                os.system(cmd+" > temp")
            else: 
                os.system("touch temp")
                print cmd+" > temp"
        self.logging.info("Finished generating gerald make file")
        out_file = open("temp", 'r')
        file_cont = out_file.readlines()
        out_file.close()
        # -4 because there is a logout line at the end
        main_line = file_cont[-4].strip()
        reqd_path = ""
        if main_line.endswith("completed with no problems"):
            self.remove("temp")
            reqd_path = main_line.split()[4]
            #out_file = open("temp", 'w')
            if not self.local:
                self.write_makepbs(reqd_path)
            #self.ssh_obj.run("python py_source/cluster_side.py "+\
                             #"pbs_scripts/"+self.runid+".pbs"+" "+\
                             #reqd_path+" "+self.runid, out_file)
            #out_file.close()
            #os.system("rm temp")
                out_file = open("temp", 'w')
                if not test:
                    self.ssh_obj.run("qsub pbs_scripts/"+self.runid+\
                                     ".pbs", out_file)
                    print "qsub pbs_scripts/"+self.runid+".pbs"
                out_file.close()
                out_file = open("temp", 'r')
                file_cont = out_file.readlines()
                out_file.close()
                main_line = file_cont[-2]
                self.remove("temp")
                self.job_id = main_line.split('.')[0]
                if test:
                    self.job_id = '123456'
                self.logging.info("Submitted gerald job. Jobid = "+self.job_id)
            elif not self.local: #case of compression pbs
                pass
            self.ran_pipeline = 1
            #call quest method to give job_id
            #out_file = open("temp", 'w')
            #self.ssh_obj.run("qstat "+job_id, out_file)
            #out_file.close()
        else:
            self.logging.info("Error!!! in making gerald. "+\
                              "Cannot submit job for make")
            raise myerror
        return reqd_path
        #############################################################
        #raise error if failure and tell quest???
        #############################################################

    def safetyCheck(self):
        pass

if __name__ == '__main__':
    b = 1
    a = MakeGerald(b)
    a.gen_make()
