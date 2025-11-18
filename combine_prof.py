from machine import PWM, UART, Pin
import time
from adc1 import adc, ADS1015_PWM

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1) 

pwm_singal = PWM(Pin(18), freq=1000) #automatically generates PWM signal on pin 18



def send_message():
    if uart.any():
        recieved_pwm_value = uart.read()
        try:
            ORIG_SENT_MESSAGE = recieved_pwm_value.decode().strip() #type:ignore
            return ORIG_SENT_MESSAGE
        except Exception as e:
            print("recieved undecodable data")
            return None
    else:
        return None
    


while True:
    desired_value = adc.read(0, ADS1015_PWM)
    echo_pwm_value = (str(desired_value) + '\n').encode()
    uart.write(echo_pwm_value) # send the converted PWM value
    ORIG_SENT_MESSAGE = send_message()
    if ORIG_SENT_MESSAGE is None:
        converted_pwm_value = "___N/A___"
    else:
        converted_pwm_value = ORIG_SENT_MESSAGE

    print(f"Desired raw PWM: {desired_value :<30} | Read converted in UART: {converted_pwm_value :<30}") 
    time.sleep(0.5) 
