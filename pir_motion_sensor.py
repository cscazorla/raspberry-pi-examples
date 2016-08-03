#!/usr/bin/python
# Playing with a PIR motion sensor and the RaspberryPi Camera
# to detect unwanted visitors to the room

# Required environment file: pir_motion_sensor.env
#  - SENDGRID_API_KEY
#  - FROM_EMAIL
#  - TO_EMAIL

# Instructions:
# 	- source ./pir_motion_sensor.env
# 	- sudo -E python pir_motion_sensor.py

import RPi.GPIO as GPIO
import time
import picamera
import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *
from time import sleep

# Main variables
sensorPin = 11
ledPin = 12
video_duration = 5 # seconds
cam = picamera.PiCamera()

def setup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(ledPin, GPIO.OUT)
	GPIO.output(ledPin, GPIO.LOW)
	print "\n"
	print "********************"
	print "Motion alarm working"
	print "********************"

def getFileName():
	return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def send_email(fileName):
	sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
	from_email = Email(os.environ.get('FROM_EMAIL'))
	subject = "Motion alarm"
	to_email = Email(os.environ.get('TO_EMAIL'))
	content = Content("text/plain", "Someone has penetrated your room. Check video file " + fileName)
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())

def destroy():
	GPIO.output(ledPin, GPIO.LOW) # turn off the led
	GPIO.cleanup()

def loop():
	prevState = False
	currState = False
	while True:
		time.sleep(.1)
		prevState = currState
		currState = GPIO.input(sensorPin)
		if currState != prevState:
			if currState:
				fileName = getFileName()
				print "Motion detected."
				print " - Recording a {0}(s) video in {1}".format(video_duration,fileName)
				GPIO.output(ledPin, GPIO.HIGH)
				cam.vflip = True
				cam.hflip = True
				cam.start_recording(fileName)
				sleep(video_duration)
				cam.stop_recording()
				send_email(fileName)
			else:
				print " - Video recording stopped.\n"
				GPIO.output(ledPin, GPIO.LOW)

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # 'Ctrl+C' pressed
		destroy()
