#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 28-04-2023 12:02:45
# 
# file          | main/plugins/osticket.py
# project       | autobackgroundrotation
# file version  | 1.0.1
#
import os
import traceback
import subprocess

# var storage
owner_of_images = "www-data:users"

start_page_image_name = "upload/images/autobackgroundrotation_start-page.jpg"
agent_login_page_image_name = "upload/scp/images/autobackgroundrotation_agent-login.jpg"
ticket_page_image_name = "upload/images/autobackgroundrotation_ticket-overview.jpg"


# change permissions to image (set owner to http)
def changeImagePermissions(path):
    os.system("chown  " + owner_of_images + " " + path)

# format httpd restart command for subprocess
def commandFormatter(command):
    nCMD = []
    commandSplit = command.split(" ")
    # remove empty values
    for arg in commandSplit:
        if arg: nCMD.append(arg)
    return nCMD

# set selected image as background
def changeImageHTTPD(self, logging, imageFilePath):
    notCompleted = False

    # config file: upload/scp/css/scp.css
    # path: ../../images/autobackgroundrotation_ticket-overview.jpg
    # edit scp.css file (background ticketsystem after login) if enabled
    if self.osticket_ticket_page: 
        try:    
            destination_path = self.osticket_path + ticket_page_image_name
            os.system("/usr/bin/cp " + imageFilePath + " " + destination_path)
            changeImagePermissions(destination_path)

        except:
            notCompleted = True
            logging.write(self, "ERROR | Changing background ticket-page failed")
            logging.writeError(self, traceback.format_exc())

    # config file: upload/scp/logo.php
    # path: images/autobackgroundrotation_agent-login.jpg
    # set agent-login background
    if self.osticket_agent_login: 
        try:
            destination_path = self.osticket_path + agent_login_page_image_name
            os.system("/usr/bin/cp " + imageFilePath + " " + destination_path)
            changeImagePermissions(destination_path)

        except: 
            notCompleted = True
            logging.write(self, "ERROR | Changing background agent-login failed")
            logging.writeError(self, traceback.format_exc())

    # config file: upload/assets/default/css/theme.css
    # path: ../../../images/autobackgroundrotation_start-page.jpg
    # set start/home page background
    if self.osticket_start_page:
        try:
            destination_path = self.osticket_path + start_page_image_name
            os.system("/usr/bin/cp " + imageFilePath + " " + destination_path)
            changeImagePermissions(destination_path)

        except: 
            notCompleted = True
            logging.write(self, "ERROR | Changing background of home/start page failed")
            logging.writeError(self, traceback.format_exc())
    
    # execute command to restart required services
    try: 

        # handle HTTP restart command
        if self.osticket_httpd_restart_command:
            formattedCommand = commandFormatter(self.osticket_httpd_restart_command)
            httpdrestart = subprocess.Popen(formattedCommand, stdout=subprocess.PIPE)
            logging.writeSubprocessout(self, httpdrestart.stdout)
        # handle PHP restart command
        if self.osticket_php_restart_command:
            formattedCommand = commandFormatter(self.osticket_php_restart_command)
            phprestart = subprocess.Popen(formattedCommand, stdout=subprocess.PIPE)
            logging.writeSubprocessout(self, phprestart.stdout)      
        logging.write(self, "INFO  | Restarted HTTPD and PHP")

    except:
        logging.write(self, "ERROR | Could not restart httpd")
        logging.writeError(self, traceback.format_exc())

    if not notCompleted:
        logging.write(self, "INFO  | Image rotation completed")
        return True
    # give back if changing was successful to cleanup static file
    else: return False
