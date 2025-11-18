"""
RECIEVE PICO()

1. gets the desired PWM value = duty cycle from UART
2. trIgger ADC to measure raw recieved PWM signal to get PWM value  
3. compare recieved PWM value (duty cycle) with desired PWM value (duty cycle) get difference
4. send meaasured PWM value value back to sender
"""

from machine import PWM, UART, Pin, ADC
import time
#from adc1 import adc, ADS1015_PWM

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1) 

adcA = ADC(Pin(26)) #I DON'T THINK I MAY NEED THIS? 
pwm_singal = PWM(Pin(18), freq=1000) #automatically generates PWM signal on pin 18

def get_pwm_value(): 
    pwm_value = adcA.read_u16
    return pwm_value

def compare_pwm_values(desired_value: int, pwm_value: int):
    diff = desired_value - pwm_value
    return diff

while True:
    measured_pwm_value = get_pwm_value()
    echo_pwm_value = str(measured_pwm_value).encode()
    uart.write(echo_pwm_value) # send the converted PWM value
    if uart.any():
        recieved_pwm_value = uart.read()
        try: 
            ORIG_SENT_MESSAGE = recieved_pwm_value.decode().strip() # type: ignore
            print(f"Send UART message:{ORIG_SENT_MESSAGE}")
        except Exception as e:
            print("Recieved undecodable data")
        print(f"I SENT: {recieved_pwm_value.decode()}") #type: ignore
    else: print("__N/A__")

    print(f"Recieved: {measured_pwm_value :<30}") #type:ignore
    time.sleep(0.5) 
