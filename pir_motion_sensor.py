#!/usr/bin/python
# Playing with a PIR motion sensor and the RaspberryPi Camera
# to detect unwanted visitors to the room


'''
            +--+
            |5V|
            +-++
              |
+---+ GPIO0 +-+-+    +---+
|   +-------+PIR+----+GND+--+
| R |       +---+    +-+-+  |
| A |                  |    |
| S |                  |    |
| P |                  |    |
| B | GPIO1 +----+   +-+-+  |
| E +-------+220R+---+LED|  |
| R |       +----+   +---+  |
| R |                       |
| Y | GPIO2 +---+           |
|   +----+--+BTN+--+--------+
+---+    |  +---+  |
         |         |
         +---------+
         |CAPACITOR|
         |   104   |
         +---------+
'''

# Required environment file: pir_motion_sensor.env
#  - SENDGRID_API_KEY
#  - FROM_EMAIL
#  - TO_EMAIL
#  - s3BucketName
#  - s3URL

# AWS S3 boto3 (https://github.com/boto/boto3)
# 1 - set up credentials (in e.g. ~/.aws/credentials):
# 	[default]
# 	aws_access_key_id = YOUR_KEY
# 	aws_secret_access_key = YOUR_SECRET
# 2 - set up a default region (in e.g. ~/.aws/config):
# 	[default]
# 	region=eu-west-1

# Instructions:
# 	- source ./pir_motion_sensor.env
# 	- (sudo -E) python pir_motion_sensor.py

import RPi.GPIO as GPIO
import time
import picamera
import datetime
import sendgrid
import os
import boto3
from sendgrid.helpers.mail import *
from time import sleep

# Main variables
sensorPin = 11
ledPin = 12
enableButtonPin = 13
videoDuration = 5 # seconds
cam = picamera.PiCamera()
s3 = boto3.resource('s3')
prevState = False
currState = False
systemEnabled = False
s3BucketName = os.environ.get('s3BucketName')
s3URL = os.environ.get('s3URL')

def setup():
	print " - Setting up the system."
	GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)
	GPIO.setup(ledPin, GPIO.OUT)
	GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(enableButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set enableButtonPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(enableButtonPin, GPIO.FALLING, callback=toggleSystem,bouncetime=200)

def enableSystem():
	global systemEnabled
	GPIO.output(ledPin, GPIO.HIGH)
	systemEnabled = True
	print " - System up and running."

def disableSystem():
	global systemEnabled,currState,prevState
	GPIO.output(ledPin, GPIO.LOW)
	GPIO.remove_event_detect(sensorPin)
	systemEnabled = False
	prevState = False
	currState = False
	print " - System disabled."

def getFileName():
	return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def send_email(fileName):
	global s3BucketName,s3URL
	sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
	from_email = Email(os.environ.get('FROM_EMAIL'))
	subject = "Motion alarm"
	to_email = Email(os.environ.get('TO_EMAIL'))
	video_link = s3URL + s3BucketName + "/" + fileName
	content = Content("text/plain", "Someone has penetrated your room. Check video file at " + video_link)
	mail = Mail(from_email, subject, to_email, content)
	try:
		response = sg.client.mail.send.post(request_body=mail.get())
		print " - Email notification sent."
	except Exception as e:
		print " - Error sending the email notification: {0}".format(e)

def upload_video_to_s3(fileName):
	print " - Uploading video to S3 ..."
	data = open(fileName, 'rb')
	try:
		s3.Bucket(s3BucketName).put_object(Key=fileName, Body=data)
		print " - File uploaded succesfully."
		os.remove(fileName)
		print " - File removed locally."
	except Exception as e:
		print " - Error uploading the file: {0}".format(e)


def destroy():
	print "\n - Cleaning up everything..."
	GPIO.output(ledPin, GPIO.LOW) # turn off the led
	GPIO.cleanup()

def toggleSystem(ev=None):
	global systemEnabled
	if systemEnabled:
		disableSystem()
	else:
		print " - Booting up the system ..."
		for x in range(1,10):
			GPIO.output(ledPin, GPIO.HIGH)
			sleep(0.5)
			GPIO.output(ledPin, GPIO.LOW)
			sleep(0.5)
		enableSystem()

def loop():
	while True:
		time.sleep(.1)
		global systemEnabled,currState,prevState
		if systemEnabled:
			prevState = currState
			currState = GPIO.input(sensorPin)
			if currState != prevState:
				if currState:
					fileName = getFileName()
					cam.vflip = True
					cam.hflip = True
					cam.start_recording(fileName)
					print " - Motion detected:"
					print "   - Recording a {0}(s) video in {1}".format(videoDuration,fileName)
					sleep(videoDuration)
					cam.stop_recording()
					print "   - Video recording stopped."
					upload_video_to_s3(fileName)
					send_email(fileName)
					print " - System ready again."

if __name__ == '__main__':     # Program start from here
	print "\n"
	print "****************"
	print "* Alarm system *"
	print "****************"
	setup()
	enableSystem()
	try:
		loop()
	except KeyboardInterrupt:  # 'Ctrl+C' pressed
		destroy()
		print " - Good bye!"
