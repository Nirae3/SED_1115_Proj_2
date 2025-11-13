"""
RECIEVE PICO()

1. gets the desired PWM value = duty cycle from UART
2. trugger ADC to measure raw recieved PWM signal  
    adc_pin = machine.ADC(26)
    measured_pwm_value = adc_pin.read_u16()

2. get the ADC (measured PWM value) and compare with recieved PWM value = duty cycle
4. compare recieved PWM value (duty cycle) with desired PWM value (duty cycle) get difference
5. send meaasured PWM value value back to sender
"""

from machine import PWM, UART, Pin, ADC
import time