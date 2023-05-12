# Autobackgroundrotation

This script is able to change backgrounds of osTicket and samba-domain-system either daytime dependend or after x hours. It has a config file 

## Quick Jump
- [Installation](#installation)
- [Config](#config)
- [Features coming soon](#features-coming-soon)

## Features
- Change background for osTicket (ticket, start and login page)
- Change either daytime based or after a fixed cycle duration (daytime can be set within the config file)
- Included logging feature
- Automatically restart php and httpd (in case of using the osTicket plugin)

## Installation
Firstly clone this repository (recommended to ```/srv/```)
```
$ git clone https://github.com/Zyzonix/autobackgroundrotation.git
```
And then execute as **root** and follow the install script:
```
$ cd autobackgroundrotation
$ sh install.sh
```
The installation script can be executed more than one time (if not completed on first run).

## Config
Configuration under ```config.ini```.
Logs are located under ```logs/```.

## Features coming soon
- Plugin for samba-domain


Readme version: 1.0
