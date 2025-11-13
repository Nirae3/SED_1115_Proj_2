"""
SEND PICO()
1. set a PWM value (duty cycle) that it got from potentiometer
2. set PWM signal 
2. send PWM value through UART

4. for UART to understand how to send, we need to do the following:
    1. put data into a specific memory
    2. inform the hardware, it's ready to be sent

5. get mesaured value from recieved
6. compare with desired value 
"""

from machine import PWM, UART, Pin, ADC
import time