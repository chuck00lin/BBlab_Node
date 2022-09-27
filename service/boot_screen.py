#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

# ---Server Info---
servInfo = [["piRemo", "--", "14091"],
            ["piHome", "--", "8123"],
            ["Gazebo", "--", "22512"]]

# -----------

def cmd(command):
    subp = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
    subp.wait(2)
    if subp.poll() ==0:
        return subp.communicate()[0]
    else:
        return "failed"
def wifiIp_cmd():
    command = "ip -4 addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'"
    return cmd(command)

def wifiName_cmd():
    command = "sudo iwconfig wlan0 | grep ESSID | cut -d \'\"\' -f2"
    return cmd(command)

def serverAlive_cmd(host,port):
    command = f"nc -v -z -w 3 {host} {port} &> /dev/null && echo 'Online' || echo 'Offline'"
    return cmd(command)
# -----------

try:
    logging.info("epd2in13_V2 Demo")
    
    epd = epd2in13_V2.EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    logging.info("---")
    # Drawing on the image
    font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    
    logging.info("1.Drawing on the image...")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame    
    draw = ImageDraw.Draw(image)

    # ---my info---
    # draw.text((5,0), "Raspscreen:", font = font15, fill =0) 
    name = wifiName_cmd()
    draw.text((5,5),name , font = font15, fill = 0) 
    draw.text((130,5), chr(8214) + wifiIp_cmd(), font = font15, fill = 0) 
    
    # ---Banner line---
    draw.line([(0,35),(235,35)], fill = 0, width = 1)

    # ---My Server Info---
    # draw.text((10,35), servInfo[0][0], font = font15, fill = 0)
    # draw.text((100,35), serverAlive_cmd(servInfo[0][1],servInfo[0][2]), font = font15, fill = 0)
    for i, row in enumerate(servInfo):
        status= serverAlive_cmd( servInfo[i][1],servInfo[i][2]) 
        textInfo = servInfo[i][0] + ": " + servInfo[i][1] + "---" + status 
        draw.text((5,40+i*25), textInfo, font = font15, fill = 0) 
    epd.display(epd.getbuffer(image)) 
    logging.info("Goto Sleep...")
    time.sleep(2)         
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13_V2.epdconfig.module_exit()
    exit()
