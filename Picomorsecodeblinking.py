#the module machine contains the class files needed to send information between Picos
from machine import Pin, PWM, I2C
import time

#this is solely to give the user enough time to direct their eyes to the Pico which will dispaly morse code
time.sleep(1)

led1 = PWM(Pin(17)) #the LED on the Pico breadboard
dot = led1.freq(1000) #the frequency of the dots 
line = led1.freq(50000) #the frequency of the lines
#dot_led1 = PWM(Pin(17))
#led1.freq(5000)
led1.duty_u16(32768)

for i in range (3):
    led1.duty_u16(32768) #the brightness of the led
    time.sleep(.4) #the time between the dots and lines should always be set to 0.4 seconds
    led1.duty_u16(0) #indicating the brightness of the LED during a pause
    time.sleep(.4)
    print(dot)

for i in range (1):
    led1.duty_u16(32768)
    time.sleep(.4)
    led1.duty_u16(65535)
    time.sleep(.4)
    print(line)

#valueA = adcA.read_u16()