#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import smtplib  
import os
import config
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import commands

class Mail:
    def __init__(self, runid="", text="", attach=[""],
                 toaddr_list=None):
        #self.server = smtplib.SMTP('smtp.gmail.com', 587)  
        #self.fromaddr = "raghuramos1987@gmail.com"
        #self.server.ehlo('x')
        #resp, null = self.server.starttls()
        #self.server.ehlo('x')
        #self.server.login("raghuramos1987@gmail.com", 'jaihanuman')
        self.server = smtplib.SMTP('smtp.osumc.edu')  
        self.fromaddr = "onti01@osumc.edu"
        if runid != "":
            self.runid = runid
            if not toaddr_list:
                self.toaddr_list = ['raghuramos1987@gmail.com',
                                    #'Gulcin.Ozer@osumc.edu'
                                    ]
            self.subject = text
            self.subject += " "+self.runid
            self.text = "Please find the relevant file attached"
            self.attach = attach
            for to_addr in self.toaddr_list:
                self.mail_diff(to_addr, self.subject, self.text,\
                          self.attach)
            self.close()

    def attach_file(self, attach):
        self.attach = attach

    def mail_diff(self, to, subject="default mail",
                  text="default mail", attach=[]):
        msg = MIMEMultipart()
        msg['From'] = "onti01@osumc.edu"  
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        if attach:
            for i in attach:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(i, 'rb').read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(i))
                msg.attach(part)
        self.server.sendmail(self.fromaddr, to, msg.as_string())

    def close(self):
        self.server.close()


if __name__ == '__main__':
    a = Mail()
    a.mail_diff('raghuramos1987@gmail.com',) 
                
