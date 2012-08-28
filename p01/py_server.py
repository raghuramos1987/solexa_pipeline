#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import socket
import logging
import threading
import thread
import time
import os
import traceback

import run_make
import mail

global test
test = 0
# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class SolexaXmlRpcServer(SimpleXMLRPCServer):

    def __init__(self, *args, **kw):
        SimpleXMLRPCServer.__init__(self, *args, **kw)
        self.running = 1
        self.runFlag = {}
        self.runRunId = ""
        #self.safetyCheck = {}
        self.rsyncFlag = {}
        self.rsyncRunId = ""
        self.compressFlag = {}
        self.compressRunId = ""
        self.allPipeLines = {}
        self.runIndex = 0
        self.compressIndex = 0
        self.rsyncIndex = 0
        self.runFlag[self.runRunId] = 0
        self.compressFlag[self.compressRunId] = 0
        self.rsyncFlag[self.rsyncRunId] = 0

    def serve_forever(self):
        while self.running:
            if self.runFlag[self.runRunId]:
                self.runFlag[self.runRunId] = 0
                logging.debug("starting rsync")
                self.allPipeLines[self.runRunId].set_params(self.run_folder,
		    self.gerald_conf, self.dist_conf, self.dest,
		    26, )
                thread.start_new_thread(self.allPipeLines[self.runRunId].InitiateRsync,
                                        ())
            elif self.compressFlag[self.compressRunId]:
                self.compressFlag[self.compressRunId] = 0
                thread.start_new_thread(self.allPipeLines[self.compressRunId].gen_compress,
                                        ())
            elif self.rsyncFlag[self.rsyncRunId]:
                self.rsyncFlag[self.rsyncRunId] = 0
                thread.start_new_thread(self.allPipeLines[self.rsyncRunId].rsync_back, ())
            #elif self.safetyCheck:
                #thread.start_new_thread(self.pipeline_run.safetyCheck,
                                        #())
                #logging.debug("finished safety check")
                #self.safetyCheck = 0
                #self.runFlag = 1
            self.handle_request()

    def stop(self):
        """stop(): stops the server"""
        self.running = 0
        return 1

    def adder_function(self, x, y):
        return x + y

    def QuestCall(self, run_folder, gerald_conf, dist_conf, local,
                  ctrl_lane):
        """Main call from quest which is called when clicked on
        Execute configuration"""
        pipeline_run = run_make.MakeGerald(logging)
        pipeline_run.codeBasePath = os.getcwd()
        self.runRunId = run_folder.split('_')[0]
        self.allPipeLines[self.runRunId] = pipeline_run
        self.runFlag[self.runRunId] = 1
        self.run_folder = run_folder
        self.gerald_conf = gerald_conf
        self.dist_conf = dist_conf
        self.dest = local
        logging.debug("Got call from Quest")
        return 1

    def TestCall(self, run_folder, gerald_conf, dist_conf, local,
                  ctrl_lane):
        mailObj = mail.Mail()
        mailObj.mail_diff("user@gmail.com", "xmlrpctest",
                           run_folder+'\n'+gerald_conf+'\n'+dist_conf+\
                           '\n'+local)
        return 1

 #change this later TODO:raghu!
#TODO: raghu. put all proc calls in try catch blocks to handle
#them and return some value to quest!
    def ReadyForCompression(self, run_folder):
        """Function call initiated from quest which is in turn started
        by osc_quest.py"""
        self.rsyncRunId = run_folder.split('_')[0]
        self.allPipeLines[self.rsyncRunId].loadConfigObj(run_folder)
        self.rsyncFlag[self.rsyncRunId] = 1
        print "Correct quest call"
        return 1

    def ReadyForDataTransfer(self, run_folder):
        """Function call initiated from quest which is in turn started
        by osc_quest.py"""
        print "wrong quest call"
        self.compressRunId = run_folder.split('_')[0]
        try:
            self.allPipeLines[self.compressRunId].loadConfigObj(run_folder)
        except:
            traceback.print_exc()
            return 0
        self.compressFlag[self.compressRunId] = 1
        return 1

if __name__ == "__main__":

    logging.basicConfig(level = logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        filename = "server_logs/test_log.txt",
                        filemode = 'w')
    server = SolexaXmlRpcServer((socket.gethostname(), int(sys.argv[1])),\
                        requestHandler=RequestHandler)
    server.register_function(server.adder_function, 'add')
    server.register_function(server.stop)
    server.register_function(server.QuestCall)
    server.register_function(server.TestCall)
    server.register_function(server.ReadyForCompression)
    server.register_function(server.ReadyForDataTransfer)


    server.serve_forever()
