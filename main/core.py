#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 10-03-2023 10:39:28
# 
# file          | main/core.py
# project       | autobackgroundrotation
# file version  | 1.0.0
#

#
# Software uses a crontab under /etc/cron.d/autobackgroundrotation for running (if using the installation script)
#

#
# Further version ideas:
# - auto image converter
# - plugin for domains
#

from datetime import datetime
from configparser import ConfigParser
from pathlib import Path
import os
import traceback
import random

# static variables
config_file = 'config.ini'
config_general = "GENERAL"
config_storage = "STORAGE"
config_daytimes = "DAYTIMES"

# time for logging / console out
class time():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime


# message handling (logging/console out)
class logging():

    # delete old logfiles, only keep last month
    def logFileCleanUp(self):
        for file in os.listdir(self.path + "logs/"):
            filename = file.split(".")[0]
            fileNameContents = filename.split("-")
            if (int(fileNameContents[0]) < int(datetime.now().strftime("%Y"))) or (int(fileNameContents[1]) < (int(datetime.now().strftime("%m")) - 1)):
                os.remove(self.path + "logs/" + file)

    def toFile(self, msg):
        logFile = open(self.path + "logs/" + str(datetime.now().strftime("%Y-%m")) + ".log", "a")
        logFile.write(msg + "\n")
        logFile.close()
        logging.logFileCleanUp(self)

    def write(self, msg):
        message = str(time.getTime() + " " + str(msg))
        print(message)
        logging.toFile(self, message)

    def writeError(self, msg):
        message = str(msg)
        print(message)
        logging.toFile(self, message)

    def writeSubprocessout(self, msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write(self, "SYS   | " + line)


class core():

    # get random image from directory
    # paths is a list
    def getRandomImage(self, paths):
        allFiles = []
        randomImage = False
        # check all path and get all files out of it
        for path in paths:
            filesInDir = os.listdir(path)
            
            # merge all available files in one list
            for file in filesInDir:
                allFiles.append(path + file)
        
        # check if files were found
        if len(allFiles) > 0:
            # get random image from all files
            randomImage = random.choice(allFiles)
        
        if not randomImage:
            logging.write(self, "ERROR | Failed to get random image")
            return False
        
        else:
            logging.write(self, "INFO  | Selected random image: " + randomImage)
            return randomImage

    # check when last change was performed
    def checkLastChanged(self, changeMethod):
        runDir = self.path + "run/"

        # if change method in daytimebased
        if changeMethod in self.timestamps.keys():
            # select correct subdir
            runDir += "daytimebased/"

            # get all files from dir
            filesInRunDir = os.listdir(runDir)

            # check if dir contains a file named like the daytime
            if changeMethod in filesInRunDir:
                logging.write(self, "INFO  | Not changing - already changed in current daytime: " + changeMethod)
                return False

            else: return True

        # if rotation is cyclebased
        else:
            runDir += "timebased/"
            filesInRunDir = os.listdir(runDir)
            # placeholder
            lastchanged_file = ""

            # get file that was gernerated with this script (if exists)
            for file in filesInRunDir:
                if file.startswith("lastchanged_"):
                    lastchanged_file = file
            
            if not lastchanged_file: return True
            else:
                # split filename
                split_filename_lastchanged_timestamp = lastchanged_file.split("_")[1]
                duration_in_hours = int(self.formatCycleDuration())
                # split timestamp and paste to datetime
                slt = split_filename_lastchanged_timestamp.split("-")
                changedTimestamp = datetime(int(slt[0]), int(slt[1]), int(slt[2]), int(slt[3]), int(slt[4]))
                currentTimestamp = datetime.now()
                logging.write(self, "INFO  | Last changed " + str(changedTimestamp) + " vs now: " + str(currentTimestamp))
                # get timedelta and format to hours
                time_delta_in_hours = (currentTimestamp - changedTimestamp).total_seconds()/60/60
                if time_delta_in_hours > duration_in_hours: return True
                else: 
                    logging.write(self, "INFO  | Cycle time isn't reached yet, current delta in hours: " + str(time_delta_in_hours))
                    logging.write(self, "INFO  | Next cycle in " + str(duration_in_hours - time_delta_in_hours) + " hours")
                    return False


    # update last changed file
    # function will only run if changing was successful
    def updateLastChanged(self, changeMethod):
        runDir = self.path + "run/"

        # if change method in daytimebased
        if changeMethod in self.timestamps.keys():
            # select correct subdir
            runDir += "daytimebased/"

        else:
            # select correct subdir
            runDir +="timebased/"

            # format time to remeber timestamp when last changed
            changeMethod = "lastchanged_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M"))

        # get all files from dir
        filesInRunDir = os.listdir(runDir)

        # remove all old files
        for file in filesInRunDir: os.remove(runDir + file)

        # touch file with current daytime as name to register last change 
        # or lastchanged timestamp (if change method is cyclewise)
        Path(runDir + changeMethod).touch()


    # format d and h to hours
    def formatCycleDuration(self):
        if self.duration.endswith("h"): return self.duration[:-1]
        else:
            duration = self.duration[:-1]
            return duration*24

    # check if given parameter from config is correct
    # required for cyclebased rotation
    def validateCycleDuration(self):
        valid = True
        length = len(self.duration)

        # check length
        if length > 3 or length < 2: valid = False
        # check if last character is letter
        if not (self.duration[length - 1].isalpha()): valid = False
        # check if last letter is d or h (day / hour)
        if not (self.duration[length - 1] == "d" or self.duration[length - 1] == "h"): valid = False
        
        return valid
        
        
    # check if provided daytimetimestamps are 24h in total
    def validate_timestamps(self):

        # merge all timestamps from config to dictionary
        self.timestamps = {
            "morning" : self.dt_morning.split("-"),
            "midday" : self.dt_midday.split("-"),
            "evening" : self.dt_evening.split("-"),
            "night" : self.dt_night.split("-")
        }

        # formatting hours to integers
        for daytime in self.timestamps:
            self.timestamps[daytime] = [int(self.timestamps[daytime][0]), int(self.timestamps[daytime][1])]

        total_timespan = 0
        # calculate total hours to cover
        for daytime in self.timestamps:
            # filter for night timespan
            if not self.timestamps[daytime][1] < self.timestamps[daytime][0]:
                
                # get timespan of each daytime (+1 to include start hour)
                # because of scheme: hour + 59 min 06-10 == 06:00 until 10:59
                total_timespan += self.timestamps[daytime][1] - self.timestamps[daytime][0] +1
            
            # handle night timestamp (over 00:00)
            else:
                total_timespan += 24 - self.timestamps[daytime][0]
                total_timespan += self.timestamps[daytime][1] +1

        # check if all hours are covered from any timespan/daytime
        if (total_timespan == 24):
            logging.write(self, "INFO  | Timestamps are valid")
            return True
        else: 
            logging.write(self, "ERROR | Timestamp-Check failed returning - please check your timestamps in config!")
            logging.write(self, "ERROR | Total hours to cover: " + str(total_timespan))
            return False

    def getDayTime(self):
        current_hour = int(datetime.now().strftime("%H"))
        current_daytime = False

        for daytime in self.timestamps:
            
            # check if current hour is greater or equals daytime beginning hour and if current hour is lower or equals end hour of daytime
            if (current_hour >= self.timestamps[daytime][0]) and (current_hour <= self.timestamps[daytime][1]):
                current_daytime = daytime
            
            # check if current hour is lower or equals end hour of night or starthour is grater or equals start hour of night 
            if  (self.timestamps[daytime][1] < self.timestamps[daytime][0]):
                if (current_hour < 24 and current_hour >= self.timestamps[daytime][0]) or (current_hour <= self.timestamps[daytime][1]):
                    current_daytime = daytime

        return current_daytime

    # change images as set in config
    def rotateTimebased(self):
        duration_valid = self.validateCycleDuration()
        self.changeMethod = "timebased"
        # empty placeholder for updateLastChanged and checkLastChanged
        self.timestamps = {}

        # argument is only a placeholder
        timeToChange = self.checkLastChanged(self.changeMethod)

        if duration_valid:

            if timeToChange:
                logging.write(self, "INFO  | Cycle duration is valid")

                # get all subdirs
                image_paths = []
                for dir in self.dirs:
                    subpath = self.dirs[dir]
                    image_paths.append(self.path + self.image_pool + subpath)

                self.randomImageInput(image_paths)
            
            else: return
            
        else:
            logging.write("ERROR | Cycle duration is unvalid - check your config file")
            return
            

    # change images depending on daytime
    def rotateDaytimeBased(self):
        
        # validate timestamps
        timestamps_valid = self.validate_timestamps()

        # check if timestamps are valid (covering 24h)
        if timestamps_valid:
            dayTime = self.getDayTime()

            # check if daytime was given back correctly
            if not dayTime: 
                logging.write(self, "ERROR | Failed to select daytime - please check your config!")
                return
            
            else:
                logging.write(self, "INFO  | Current/selected daytime: " + dayTime)

                # check when last rotation was made, image should only be changed once in a daytime period
                timeToChange = self.checkLastChanged(dayTime)

                # set global var to update static files via updateLastChanged and checkLastChanged
                self.changeMethod = dayTime

                if timeToChange:
                    # select subpath from dictionary / merge path infos together
                    subpath = self.dirs[dayTime]
                    fullpath = [self.path + self.image_pool + subpath]
                    self.randomImageInput(fullpath)

                    
    # reverse entry from both selection methods
    # pathList is (daytimebased: list with one directory)(cyclewise: list with multiple directories)
    def randomImageInput(self, pathList):
        randomSelectedFile = self.getRandomImage(pathList)

        # intiating pluginselection
        if randomSelectedFile: self.selectPlugin(randomSelectedFile)
        else: 
            logging.write(self, "ERROR | No file selected - returning")
            return

    # lookup which plugin is enabled
    def selectPlugin(self, randomSelectedFile):
        
        # if plugin is osticket
        if self.plugin == 'osticket':

            try: 
                # backgrounds to change
                self.osticket_start_page = self.cnfgImp["OSTICKET"].getboolean("start_page")
                self.osticket_agent_login = self.cnfgImp["OSTICKET"].getboolean("agent_login")
                self.osticket_ticket_page = self.cnfgImp["OSTICKET"].getboolean("ticket_page")
                self.osticket_httpd_restart_command = self.cnfgImp["OSTICKET"]["httpd_restart_command"]
                self.osticket_php_restart_command = self.cnfgImp["OSTICKET"]["php_restart_command"]
                self.osticket_path = self.cnfgImp["OSTICKET"]["os_ticket_path"]

            except:
                logging.write(self, "ERROR | Failed to load settings for backgrounds for OSTICKET")
                logging.writeError(self, traceback.format_exc())
                return

            # import plugin
            import plugins.osticket as osticket
            
            success = osticket.changeImageHTTPD(self, logging, randomSelectedFile)

        elif self.plugin == 'domain':

            try:
                # backgrounds to change
                self.domain_lockscreen = self.cnfgImp["LOCAL_DOMAIN"].getboolean("lockscreen")
                self.domain_desktop = self.cnfgImp["LOCAL_DOMAIN"].getboolean("desktop")

            except:
                logging.write(self, "ERROR | Failed to load settings for backgrounds for OSTICKET")
                logging.writeError(self, traceback.format_exc())
                return

            # import plugin
            import plugins.domain as domain
            logging.write(self, "INFO  | Plugin hasn't been developed yet. Check newer versions of this software on GitHub")
            
            success = True

        elif self.plugin == 'simplehtml':
    
            try:
                # backgrounds to change
                self.simplehtml_basepath = self.cnfgImp["SIMPLEHTML"]["basepath"]
                self.simplehtml_defaultname = self.cnfgImp["SIMPLEHTML"]["defaultname"]

            except:
                logging.write(self, "ERROR | Failed to load settings for backgrounds for SIMPLEHTML")
                logging.writeError(self, traceback.format_exc())
                return

            # import plugin
            import plugins.simplehtml as simplehtml            

            success = simplehtml.changeImageHTTPD(self, logging, randomSelectedFile)

        else:
            logging.write(self, "ERROR | No plugin selected")
            return

        # update last changed file
        if success:
            self.updateLastChanged(self.changeMethod)


    def __init__(self):
        
        # create config importer
        self.cnfgImp = ConfigParser(comment_prefixes='/', allow_no_value=True)
        
        # open config.ini file
        self.cnfgImp.read(config_file)

        try:
            # get logfile path
            self.path = self.cnfgImp[config_general]["main_path"]
        except:
            print(traceback.format_exc())
            print("ERROR | Wasn't able to read config file")
            print("ERROR | Check your if the path to your config.ini in core.py is correct!")
            return

        # try to load plugins (osticket/local_domain)
        try:
            self.plugin_osticket = self.cnfgImp["PLUGINS"].getboolean("osticket")
            self.plugin_domain = self.cnfgImp["PLUGINS"].getboolean("local_domain")
            self.plugin_simplehtml = self.cnfgImp["PLUGINS"].getboolean("simplehtml")

            # if both plugins are enabled
            if self.plugin_domain is self.plugin_osticket is self.plugin_simplehtml:
                logging.write(self, "ERROR | All plugins are enabled or disabled - please check your config")
                return

            # set enabled plugin to global variable
            if self.plugin_osticket: self.plugin = "osticket" 
            elif self.plugin_domain: self.plugin = "domain"
            elif self.plugin_simplehtml: self.plugin = "simplehtml"
            logging.write(self, "INFO  | Changing background for '" + self.plugin + "'")
            
        except:
            logging.write(self, "ERROR | Failed to load plugin")
            logging.writeError(self, traceback.format_exc())
            return

        try:
            # import required data
            self.daytime_dependend = self.cnfgImp[config_general].getboolean("daytime_dependend")
            logging.write(self, "INFO  | Got daytime_dependend variable")
        
        except:
            logging.write(self, "ERROR | Could not read [" + config_general + "][daytime_dependend] from " + config_file)
            logging.writeError(self, traceback.format_exc())
            return
        
        # import image dirs
        try:
            self.image_pool = self.cnfgImp[config_storage]["image_pool"]
            self.ip_morning = self.cnfgImp[config_storage]["ip_morning"]
            self.ip_midday = self.cnfgImp[config_storage]["ip_midday"]
            self.ip_evening = self.cnfgImp[config_storage]["ip_evening"]
            self.ip_night = self.cnfgImp[config_storage]["ip_night"]

            # merge directories to dictionary
            self.dirs = {
                "morning" : self.ip_morning,
                "midday" : self.ip_midday,
                "evening" : self.ip_evening,
                "night" : self.ip_night,
            }

        except:
            logging.write(self, "ERROR | Was not able to get image directories")
            logging.writeError(traceback.format_exc())
            return


        # intialize rotation method
        # if rotation should be performed regulary
        if not self.daytime_dependend:
            
            # try to read cycle duration from config file
            try: 
                self.duration = self.cnfgImp[config_general]["cycle_duration"]

            except:
                logging.write(self, "ERROR | Could not import 'cycle_duration'")
                logging.writeError(self, traceback.format_exc())
                return

            logging.write(self, "INFO  | Rotating timebased, every " + (self.duration))
            self.rotateTimebased()
        
        # if rotation should be performed daytime-based
        else:
            try:
                self.dt_morning = self.cnfgImp[config_daytimes]["morning"]
                self.dt_midday = self.cnfgImp[config_daytimes]["midday"]
                self.dt_evening = self.cnfgImp[config_daytimes]["evening"]
                self.dt_night = self.cnfgImp[config_daytimes]["night"]
                logging.write(self, "INFO  | Got all required variables")

            except:
                logging.write(self, "ERROR | Failed to import settings from " + config_file)
                logging.writeError(self, traceback.format_exc())
                return

            # start rotation
            self.rotateDaytimeBased()
       
if __name__ == "__main__":
    core()   
