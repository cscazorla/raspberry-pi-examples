#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

pins = [11, 12, 13, 15, 16, 18, 22, 7]
delay = 0.1

def setup():
	GPIO.setmode(GPIO.BOARD)        # Numbers GPIOs by physical location
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)   # Set all pins' mode is output
		GPIO.output(pin, GPIO.HIGH) # Set all pins to high(+3.3V) to off led

def loop():
	print 'Yes, Michael?'
	while True:
		for pin in pins:
			GPIO.output(pin, GPIO.LOW)
			time.sleep(delay)
			GPIO.output(pin, GPIO.HIGH)
		reduced_pins = pins[1:7]
		for pin in reversed(reduced_pins):
				GPIO.output(pin, GPIO.LOW)
				time.sleep(delay)
				GPIO.output(pin, GPIO.HIGH)

def destroy():
	for pin in pins:
		GPIO.output(pin, GPIO.HIGH)    # turn off all leds
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # 'Ctrl+C' pressed
		destroy()
