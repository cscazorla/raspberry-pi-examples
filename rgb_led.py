#!/usr/bin/env python
# Flashing a RGB LED with a couple of buttons
# Electrical schematics:
#          +---+       +---+     +---+
# GPIO7+---+BTN+-------+GND+-----+BTN+----+GPIO6
#          +---+       +-+-+     +---+
#                        |
#                        |
#                        | A
#                        |
#                      +-+-+
#                      |RGB| B  +----+
#                      |LED+----+220R+--+GPIO3
#                      +---+    +----+
#                      |   |
#                    R |   |G
#                      |   |
#                      |   |
#                   +--+   +--+
#               220R|  |   |  | 220R
#                   |  |   |  |
#                   ++-+   +--+
#                    |        |
#                    +        +
#                  GPIO1     GPIO2

import RPi.GPIO as GPIO
import time

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
pins = {'pin_R':11, 'pin_G':12, 'pin_B':13}  # GPIO1, GPIO2, GPIO3
SlowBtnPin = 22 # GPIO6
FastBtnPin = 7 # GPIO7
speed = 1

GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
# Set buttons mode as input, and pull up to high level(3.3V)
GPIO.setup(FastBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SlowBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# LED pins' mode is output
for i in pins:
	GPIO.setup(pins[i], GPIO.OUT)
	GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
p_G = GPIO.PWM(pins['pin_G'], 2000)
p_B = GPIO.PWM(pins['pin_B'], 5000)
p_R.start(0)      # Initial duty Cycle = 0(leds off)
p_G.start(0)
p_B.start(0)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):   # For example : col = 0x112233
	R_val = (col & 0xFF0000) >> 16
	G_val = (col & 0x00FF00) >> 8
	B_val = (col & 0x0000FF) >> 0

	R_val = map(R_val, 0, 255, 0, 100)
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)

	p_R.ChangeDutyCycle(R_val)     # Change duty cycle
	p_G.ChangeDutyCycle(G_val)
	p_B.ChangeDutyCycle(B_val)

def increaseSpeed(ev=None):
	global speed
	speed = speed * 0.5
	print '==> Faster'

def decreaseSpeed(ev=None):
	global speed
	speed = speed * 2
	print '==> Slower'

def loop():
	GPIO.add_event_detect(FastBtnPin, GPIO.FALLING, callback=increaseSpeed)
	GPIO.add_event_detect(SlowBtnPin, GPIO.FALLING, callback=decreaseSpeed)
	while True:
		for col in colors:
			# print "- {0}".format(hex(col))
			setColor(col)
			time.sleep(speed)

def destroy():
	p_R.stop()
	p_G.stop()
	p_B.stop()
	for i in pins:
		GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
	GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
	try:
		print "========="
		print " Rainbow "
		print "========="
		loop()
	except KeyboardInterrupt:  # 'Ctrl+C' pressed
		destroy()
