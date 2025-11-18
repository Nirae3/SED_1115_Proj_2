from machine import PWM, UART, Pin, ADC
import time
from adc1 import adc, ADS1015_PWM

#UART and ADC
adc = ADC(26)
#a UART object with 8 data bits, no parity, and 1 stop bit
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

#PWM
pwm_singal = PWM(Pin(18), freq=1000)

def get_pwm_value(): 
    pwm_value = adc.read(0, ADS1015_PWM)
    return pwm_value

def compare_pwm_values(desired_value: int, pwm_value: int):
    diff = desired_value - pwm_value
    return diff

#buffer for incoming data from receiver
rx_buffer = ""

while True:
    #calling the adc to read the duty cycle value read from the potentiometer
    desired_value = adc.read_u16()
    uart.write(str(desired_value) + "\n") #sending pwm value over UART #the MicroPython stores the bytes of data into a transmit buffer in the Pico’s memory
    pwm_singal.duty_u16(desired_value)
    time.sleep(0.5) #remove

    rx_buffer = ""
    while True:
        if uart.any():  # check if any byte has arrived
            char = uart.read(1).decode()  # read one byte
            if char == "\n":
                #what the reciever sends
                measured_value = int(rx_buffer)

                #comparing with desired PWM
                difference = desired_value - measured_value
                print("Desired:", desired_value,
                      "| Measured:", measured_value,
                      "| Difference:", difference)
                break
            else:
                rx_buffer += char
