#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

SDI   = 11
RCLK  = 12
SRCLK = 13

#===============   LED Mode Defne ================
#	You can define yourself, in binay, and convert it to Hex
#	8 bits a group, 0 means off, 1 means on
#	like : 0101 0101, means LED1, 3, 5, 7 are on.(from left to right)
#	and convert to 0x55.
BLINKS = [
	[0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80],
	[0x01,0x03,0x07,0x0f,0x1f,0x3f,0x7f,0xff],
	[0x01,0x05,0x15,0x55,0xb5,0xf5,0xfb,0xff],
	[0x02,0x03,0x0b,0x0f,0x2f,0x3f,0xbf,0xff],
	[0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA],
	[0x01,0x81,0x83,0xC3,0xC7,0xE7,0xEF,0xFF],
	[0x18,0x3C,0x7E,0xFF,0x18,0x3C,0x7E,0xFF],
]
#=================================================

def print_msg():
	print 'Program is running...'
	print 'Please press Ctrl+C to end the program...'

def setup():
	GPIO.setmode(GPIO.BOARD)    # Number GPIOs by its physical location
	GPIO.setup(SDI, GPIO.OUT)
	GPIO.setup(RCLK, GPIO.OUT)
	GPIO.setup(SRCLK, GPIO.OUT)
	GPIO.output(SDI, GPIO.LOW)
	GPIO.output(RCLK, GPIO.LOW)
	GPIO.output(SRCLK, GPIO.LOW)

def hc595_in(dat):
	for bit in range(0, 8):
		GPIO.output(SDI, 0x80 & (dat << bit))
		GPIO.output(SRCLK, GPIO.HIGH)
		time.sleep(0.001)
		GPIO.output(SRCLK, GPIO.LOW)

def hc595_out():
	GPIO.output(RCLK, GPIO.HIGH)
	time.sleep(0.001)
	GPIO.output(RCLK, GPIO.LOW)

def loop():
	sleeptime = 0.1		# Change speed, lower value, faster speed
	while True:
		for WhichLeds in BLINKS:
			for i in range(0, len(WhichLeds)):
				hc595_in(WhichLeds[i])
				hc595_out()
				time.sleep(sleeptime)
			for i in range(len(WhichLeds)-2, -1, -1):
				hc595_in(WhichLeds[i])
				hc595_out()
				time.sleep(sleeptime)

def destroy():   # When program ending, the function is executed.
	GPIO.cleanup()

if __name__ == '__main__': # Program starting from here
	print_msg()
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
