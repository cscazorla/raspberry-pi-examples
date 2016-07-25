# RGB LED controlled via WebIOPi
# Electrical schematics:
#                      +---+
#                      +GND+
#                      +-+-+
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

import webiopi
import datetime

GPIO = webiopi.GPIO
pins = {'pin_R':17, 'pin_G':18, 'pin_B':27}  # GPIO0, GPIO1, GPIO2

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(R_val,G_val,B_val):
	R_val = map(R_val, 0, 255, 0, 1)
	G_val = map(G_val, 0, 255, 0, 1)
	B_val = map(B_val, 0, 255, 0, 1)

	GPIO.pwmWrite(pins['pin_R'], R_val)
	GPIO.pwmWrite(pins['pin_G'], G_val)
	GPIO.pwmWrite(pins['pin_B'], B_val)

# setup function is automatically called at WebIOPi startup
def setup():
	# LED pins' mode is output
	for i in pins:
		GPIO.setFunction(pins[i], GPIO.PWM)

	setColor(255,0,0)

# loop function is repeatedly called by WebIOPi
def loop():
    webiopi.sleep(1)

# destroy function is called at WebIOPi shutdown
def destroy():
	for i in pins:
		GPIO.pwmWrite(pins[i], 0)    # Turn off all leds

@webiopi.macro
def setLight(r,g,b):
	setColor(int(r),int(g),int(b))
