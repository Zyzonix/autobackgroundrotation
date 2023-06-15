#!/bin/bash
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 10-03-2023 10:39:37
# 
# file          | install.sh
# project       | autobackgroundrotation
# file version  | 1.0.1
#

echo "######################################################"
echo "# Welcome to the installer of autobackgroundrotation #"
echo "#                                                    #"
echo "# This project has been developed by Zyzonix         #"
echo "# https://github.com/Zyzonix/autobackgroundrotaion   #"
echo "######################################################"
echo ""

# check if executed as root
USR=$(/usr/bin/id -u)
if [ $USR -ne 0 ]
  then echo "Please rerun this script as root (su -i or sudo)- exiting..."
  exit
fi

printf "%s " "Press any key to continue or CTRL+C to exit..."
read ans

# set install dir to main dir in config-file
MAINDIR=$(pwd)
echo "Setting main directory"
echo "Updating config file"
PATHOLD='main_path='
PATHNEW='main_path='$MAINDIR/
CONFIGPATH=$MAINDIR/config.ini
sed -i "s+$PATHOLD.*+$PATHNEW+g" $CONFIGPATH

# create all required subdirs
echo "Creating all required sub directories"
mkdir -v $MAINDIR/images
mkdir -v $MAINDIR/logs
mkdir -v $MAINDIR/run
mkdir -v $MAINDIR/run/daytimebased
mkdir -v $MAINDIR/run/timebased

# create image dirs
echo "Creating image directories"
mkdir -v $MAINDIR/images/morning
mkdir -v $MAINDIR/images/midday
mkdir -v $MAINDIR/images/evening
mkdir -v $MAINDIR/images/night
cp $MAINDIR/main/template.jpg $MAINDIR/images/night
cp $MAINDIR/main/template.jpg $MAINDIR/images/morning
cp $MAINDIR/main/template.jpg $MAINDIR/images/evening
cp $MAINDIR/main/template.jpg $MAINDIR/images/midday

# update config_file in core.py
OLDCONFIGPATH="config_file = 'config.ini'"
NEWCONFIGPATH="config_file = '"$MAINDIR"/config.ini'"
sed -i "s+$OLDCONFIGPATH+$NEWCONFIGPATH+g" $MAINDIR/main/core.py

# install crontab for hourly run in exclusive cron-file
CRONFILE=/etc/cron.d/autobackgroundrotation
CRONCOMMAND="01 *    * * *   root    /usr/bin/python3 $MAINDIR/main/core.py"
echo ""
echo "Installing crontab under " $CRONFILE
touch $CRONFILE
echo "05 *    * * *   root    /usr/bin/python3 $MAINDIR/main/core.py" >> $CRONFILE

printf "%s " "Please enter the command to restart HTTPD (like /usr/bin/rc-service httpd restart or /usr/bin/systemctl restart apache2 (Debian)):"
read HTTPDCOMMAND
HTTPDOLD='httpd_restart_command='
echo "Setting to "$HTTPDCOMMAND
read -p "Correct? y / n : " CONFIRM
if [ "$CONFIRM" != "y" ]; then exit; fi
sed -i "s+$HTTPDOLD.*+$HTTPDOLD$HTTPDCOMMAND+" $CONFIGPATH

printf "%s " "Please enter the command to restart PHP (like /usr/bin/rc-service php-fpm7 restart (Debian: leave empty)):"
read PHPCOMMAND
PHPOLD='php_restart_command='
echo "Setting to "$PHPCOMMAND
read -p "Correct? y / n : " CONFIRM
if [ "$CONFIRM" != "y" ]; then exit; fi
sed -i "s+$PHPOLD.*+$PHPOLD$PHPCOMMAND+" $CONFIGPATH

read -p "Should the image rotation be daytime based? y / n : " CONFIRM
if [ "$CONFIRM" != "y" ] 
then 
    sed -i "s+"daytime_dependend=".*+daytime_dependend=false+g" $CONFIGPATH
    echo "Standard rotation time is set to 2h - to change it manually edit the cycle_duration parameter in the config.ini file."
    echo 'Please remind that only h (hour) and d (day) are allowed!'
else
    sed -i "s+"daytime_dependend=".*+daytime_dependend=true+g" $CONFIGPATH
fi

# configure osticket plugin
read -p "Should the osTicket plugin be enabled? y / n : " CONFIRM
if [ "$CONFIRM" != "n" ] 
then 
    sed -i "s+"osticket=".*+osticket=true+g" $CONFIGPATH
    read -p "Automatically change background of start page? y / n : " CONFIRM
    if [ "$CONFIRM" != "n" ] 
    then 
        sed -i "s+"start_page=".*+start_page=true+g" $CONFIGPATH
    else 
        sed -i "s+"start_page=".*+start_page=false+g" $CONFIGPATH
    fi
    read -p "Automatically change background of agent login? y / n : " CONFIRM
    if [ "$CONFIRM" != "n" ] 
    then 
        sed -i "s+"agent_login=".*+agent_login=true+g" $CONFIGPATH
    else 
        sed -i "s+"agent_login=".*+agent_login=false+g" $CONFIGPATH
    fi
    read -p "Automatically change background of ticket page? y / n : " CONFIRM
    if [ "$CONFIRM" != "n" ] 
    then 
        sed -i "s+"ticket_page=".*+ticket_page=true+g" $CONFIGPATH
    else
        sed -i "s+"ticket_page=".*+ticket_page=false+g" $CONFIGPATH
    fi

    read -p "Is osticket installed in /srv/osticket? y / n : " CONFIRM
    if [ "$CONFIRM" != "y" ] 
    then 
        read -p "Please enter the path to osticket without / at the end:" OSTICKETPATH
        echo $OSTICKETPATH
    else
        OSTICKETPATH="/srv/osticket"
    fi

    # request owner of images
    printf "%s " "Please enter the user and group for the http/apache service (apache2: www-data:users, httpd: http:http):"
    read OWNER_OF_IMAGES
    OWNER_OF_IMAGES_OLD='owner_of_images = '
    OWNER_OF_IMAGES_NEW=$OWNER_OF_IMAGES_OLD'"'$OWNER_OF_IMAGES'"'
    echo "Setting to "$OWNER_OF_IMAGES
    read -p "Correct? y / n : " CONFIRM
    if [ "$CONFIRM" != "y" ]; then exit; fi
    sed -i "s+$OWNER_OF_IMAGES_OLD.*+$OWNER_OF_IMAGES_NEW+" /srv/ext-stor/autobackgroundrotation/main/plugins/osticket.py

    echo ""
    echo "Feel free to change those values in config.ini"
    echo ""
    sleep 1

    echo "osTicket path is now: "$OSTICKETPATH
    echo "Editing now osTicket config files"

    TICKETPAGEFILE=$OSTICKETPATH/upload/scp/css/scp.css
    LOGINPAGEFILE=$OSTICKETPATH/upload/scp/logo.php
    STARTPAGEFILE=$OSTICKETPATH/upload/assets/default/css/theme.css

    # replace for ticket page
    sed -i -e '/body, html {/,/}/!b' -i -e '/}/!d;r install/ticket_page.txt' -i -e 'd' $TICKETPAGEFILE
    # replace for start page
    sed -i -e '/body {/,/}/!b' -i -e '/}/!d;r install/start_page.txt' -i -e 'd' $STARTPAGEFILE
    # replace for login page
    OLDSTRING="Http::redirect('images/login-headquarters.jpg');"
    NEWSTRING="Http::redirect('images/autobackgroundrotation_agent-login.jpg');"
    sed -i 's+'$OLDSTRING+$NEWSTRING'+g' $LOGINPAGEFILE

fi

read -p "Should the local_domain plugin be enabled? y / n : " CONFIRM
if [ "$CONFIRM" != "n" ] 
then 
    sed -i "s+"local_domain=".*+local_domain=true+g" $CONFIGPATH
    echo "This plugin hasn't been developed yet"
fi

echo ""
echo "#########################################################"
echo "Installation complete!        "
echo "Upload your images to $MAINDIR/images/ "
echo "And then select any of the sub dirs, if timedependend changemode" 
echo "is selected any of those subdirs will be used"
echo ""
echo "If errors are occurring, check your config.ini"
echo "Log files are located here: $MAINDIR/logs/ "
echo "#########################################################"
echo ""
