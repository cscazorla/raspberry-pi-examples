#!/usr/bin/python

# Time-lapse application for RaspberryPi Camera.
# It takes pictures at intervals and store them in a dynamically named folder
# Created by CScazorla on 07/08/2016.
# Inspired by fotosyn:
# - http://www.fotosyn.com
# - https://bitbucket.org/fotosyn

import os
import time
import logging
from datetime import datetime

# Global variables
pictures_directory = "/home/pi/timelapse" # Within this directory new folders will be created
imgWidth = 1024 # Max = 3280
imgHeight = 768 # Max = 2464
waitSeconds = 10 # Seconds to wait before next capture. (Minimum is 6 secs)
pictureSerial = 1 # Serial for saved image filenames (0001.jpg, 0002.jpg, etc)

# Grab the current datetime to create the folder
d = datetime.now()
initYear = "%04d" % (d.year)
initMonth = "%02d" % (d.month)
initDay = "%02d" % (d.day)
initHour = "%02d" % (d.hour)
initMins = "%02d" % (d.minute)
initSecs = "%02d" % (d.second)
folder = pictures_directory + "/" + str(initYear) + str(initMonth) + str(initDay) + str(initHour) + str(initMins) + str(initSecs)
os.mkdir(folder)

# Setting up a log file
logging.basicConfig(filename=str(pictures_directory) + ".log",level=logging.DEBUG)
logging.debug("Started log for " + str(folder))

# Picture:
# - Options: sharpening, auto white balance, average metering mode, vertical/horizontal rotation
# - Dimensions
pictureOptions = "-sh 40 -awb auto -mm average -vf -hf"
pictureDimensions = "-w " + str(imgWidth) + " -h " + str(imgHeight)

# Main Loop
try:
	while True:
		d = datetime.now()

		# Set pictureSerialNumber to 000X using four digits
		pictureSerialNumber = "%04d" % (pictureSerial)

		# Capture the CURRENT time to insert into each capture image filename
		hour = "%02d" % (d.hour)
		mins = "%02d" % (d.minute)
		secs = "%02d" % (d.second)
		pictureFilename = str(folder) + "/" + str(pictureSerialNumber) + ".jpg"

		# Capture the image using raspistill.
		os.system("raspistill " + pictureDimensions + " -o " + pictureFilename + " " + pictureOptions)

		# Write out to log file
		logging.debug('Image saved at ' + hour + ':' + mins + ':' + secs + ' ==> ' + pictureFilename)

		# Increment the pictureSerial
		pictureSerial += 1

		# Wait for the next capture. Note that we take into account the length
		# of time it took to capture the image when calculating the delay
		e = datetime.now()
		time.sleep(waitSeconds - (e-d).total_seconds())
except Exception as e:
	logging.debug(e)
