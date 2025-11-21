from machine import PWM, UART, Pin, ADC
import time
from adc1 import adc, ADS1015_PWM  # Assuming adc1.py contains ADS1015 setup

# UART for sending desired PWM (optional)
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

# PWM output
pwm_signal = PWM(Pin(18), freq=1000)

# Function to read measured PWM from ADS1015
def get_pwm_value(): 
    pwm_value = adc.read(0, ADS1015_PWM)  # channel 0, PWM input defined in adc1.py
    return pwm_value

# Function to compare desired vs measured PWM
def compare_pwm_values(desired_value: int, pwm_value: int):
    return desired_value - pwm_value

while True:
    # 1. Read desired PWM from potentiometer
    desired_value = ADC(26).read_u16()
    
    # 2. Send desired value over UART (optional)
    uart.write(str(desired_value) + "\n")
    
    # 3. Set PWM output
    pwm_signal.duty_u16(desired_value)
    
    # 4. Read measured PWM from ADS1015
    measured_value = get_pwm_value()

    measured_value_scaled = int((measured_value / 4095) * 65535)
    difference = desired_value - measured_value_scaled

    #measured_value_scaled = int (measured_value * 65535 / 4095) # 12-bit to 16-bit. 65535 is 16-bit, 4095 is 12-bit
    
    # 5. Compare desired vs measured
    difference = compare_pwm_values(desired_value, measured_value_scaled)

    # 6. Print for monitoring
    print(f"Desired: {desired_value} | Measured: {measured_value_scaled} | Difference: {difference}")
    
    time.sleep(0.5)  # optional, adjust as needed
