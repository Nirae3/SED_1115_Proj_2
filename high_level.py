# High level design
from machine import PWM, UART, Pin, ADC
import time

"""
WE FIGURED OUT
duty cycle = PWM value
PWM signal is the up and down diagram


SEND PICO()
1. set a PWM value (duty cycle) that it got from potentiometer
2. set PWM signal 
2. send PWM value through UART

4. for UART to understand how to send, we need to do the following:
    1. put data into a specific memory
    2. inform the hardware, it's ready to be sent

5. get mesaured value from recieved
6. compare with desired value 

RECIEVE PICO()

1. gets the desired PWM value = duty cycle from UART
2. trugger ADC to measure raw recieved PWM signal  
    adc_pin = machine.ADC(26)
    measured_pwm_value = adc_pin.read_u16()

2. get the ADC (measured PWM value) and compare with recieved PWM value = duty cycle
4. compare recieved PWM value (duty cycle) with desired PWM value (duty cycle) get difference
5. send meaasured PWM value value back to sender

"""