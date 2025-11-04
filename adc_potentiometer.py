from machine import Pin, PWM,ADC

import time
adcA = ADC(Pin(26))
led1 = PWM(Pin(17))
led1.freq(1000)

adcB = ADC(Pin(27))
led2 = PWM(Pin(16))
led2.freq(1000)
# This could also be written as: led1 = PWM(Pin(18), freq=1000)
valueA = adcA.read_u16()

print ("I got here")
#fun thing to do: change while True to while valueA is < 50000:, [;D]
while True:
    valueA = adcA.read_u16()
    valueB = adcB.read_u16()
    print(valueA, valueB)
    led1.duty_u16(valueA)
    led2.duty_u16(valueB)
    time.sleep_ms(50)

#print("done")
