#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

SDI   = 11
RCLK  = 12
SRCLK = 13

segCode = [
	0xff, # 8.
	0x3f, # 0
	0x06, # 1
	0x5b, # 2
	0x4f, # 3
	0x66, # 4
	0x6d, # 5
	0x7d, # 6
	0x07, # 7
	0x7f, # 8
	0x6f, # 9
	0x77, # A
	0x7c, # b
	0x39, # C
	0x5e, # d
	0x79, # E
	0x71, # F
	0x80  # .
]

carlosCode = [0x39,0x77,0xF3,0x38,0x3f,0x6d]

def print_msg():
	print 'Program is running...'
	print 'Please press Ctrl+C to end the program...'

def setup():
	GPIO.setmode(GPIO.BOARD)    #Number GPIOs by its physical location
	GPIO.setup(SDI, GPIO.OUT)
	GPIO.setup(RCLK, GPIO.OUT)
	GPIO.setup(SRCLK, GPIO.OUT)
	GPIO.output(SDI, GPIO.LOW)
	GPIO.output(RCLK, GPIO.LOW)
	GPIO.output(SRCLK, GPIO.LOW)

def hc595_shift(dat):
	for bit in range(0, 8):
		GPIO.output(SDI, 0x80 & (dat << bit))
		GPIO.output(SRCLK, GPIO.HIGH)
		time.sleep(0.001)
		GPIO.output(SRCLK, GPIO.LOW)
	GPIO.output(RCLK, GPIO.HIGH)
	time.sleep(0.001)
	GPIO.output(RCLK, GPIO.LOW)

def loop():
	while True:
		for i in range(0, len(carlosCode)):
			hc595_shift(carlosCode[i])
			time.sleep(0.5)

def destroy():   #When program ending, the function is executed.
	GPIO.cleanup()

if __name__ == '__main__': #Program starting from here
	print_msg()
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
