#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 29-03-2024 13:13:32
# 
# file          | main/plugins/simplehtml.py
# project       | autobackgroundrotation
# file version  | 1.0
#
import os
import traceback

# var storage
owner_of_images = "www-data:users"


# change permissions to image (set owner to http)
def changeImagePermissions(path):
    os.system("chown  " + owner_of_images + " " + path)

# set selected image as background
def changeImageHTTPD(self, logging, imageFilePath):
    notCompleted = False

    try:    
        destination_path = self.simplehtml_basepath + self.simplehtml_defaultname
        os.system("/usr/bin/cp " + imageFilePath + " " + destination_path)
        changeImagePermissions(destination_path)

    except:
        notCompleted = True
        logging.write(self, "ERROR | Changing background ticket-page failed")
        logging.writeError(self, traceback.format_exc())

    if not notCompleted:
        logging.write(self, "INFO  | Image rotation completed")
        return True
    # give back if changing was successful to cleanup static file
    else: return False

