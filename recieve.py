"""
RECIEVE PICO()

1. gets the desired PWM value = duty cycle from UART
2. trIgger ADC to measure raw recieved PWM signal to get PWM value  
3. compare recieved PWM value (duty cycle) with desired PWM value (duty cycle) get difference
4. send meaasured PWM value value back to sender
"""

from machine import PWM, UART, Pin, ADC
import time

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1) 

adcA = ADC(Pin(26))
pwm_singal = PWM(Pin(18), freq=1000) #automatically generates PWM signal on pin 18



def get_pwm_value(): 
    pwm_value = adcA.read_u16()
    #print(pwm_value)
    return pwm_value
    #pwm_singal.duty_u16(pwm_value)   DON'T THINK WE NEED THIS

def compare_pwm_values(desired_value: int, pwm_value: int):
    diff = desired_value - pwm_value
    return diff

 
break_point = "\n".encode() 
while True:
    pwm_value = get_pwm_value()
    decoded_pwm_value = str(pwm_value)
    uart.write(decoded_pwm_value.encode()) # send the converted PWM value
    recieved_data = b""
    if uart.any():
        byte = uart.read(1)
        if byte == break_point:
            break
        recieved_data += byte
    else: print("___")

    print(f"Recieved: {pwm_value :<30}") #type:ignore
    time.sleep(0.5) 

"""
send pwm_values it gets

once the reciever gets pwm_values, pring it
"""
