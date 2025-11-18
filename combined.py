
from machine import PWM, UART, Pin, ADC, I2C
import time
#from adc1 import adc, ADS1015_PWM
from ads1x15 import ADS1015


ADS1015_PWM = 2

i2c = I2C(1, sda=Pin(14), scl=Pin(15))
external_adc = ADS1015(i2c, 0x48, 1)


uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1) 

adc_pot = ADC(Pin(26)) 
pwm_singal = PWM(Pin(16), freq=1000) #automatically generates PWM signal on pin 18


def read_uart_line(uart):
    rx_buffer = ""
    while True:
        if uart.any():  # check if any byte has arrived
            char = uart.read(1).decode()  # read one byte
            if char == "\n":
                return int(rx_buffer)  # convert the received string to int
            else:
                rx_buffer += char


ADS_MIN_RAW = 9
SCALING_FACTOR = 41.5 # SCALING_FACTOR = 65535 / (  (ADS_MAX)/32  -  (ADS_MIN)/32   ) <- calculated as per

while True:
    desired_pot_value = adc_pot.read_u16() # read from potentiometer, 
    pwm_singal.duty_u16(desired_pot_value) # generate PWM signal

    uart.write((str(desired_pot_value) + "\n").encode()) # send the PWM value via UART

    pwm_singal.duty_u16(desired_pot_value) # set the duty cycle to PWM_signal
    time.sleep(0.6)

    measured_signal_value_raw = external_adc.read(0, ADS1015_PWM)

    adjusted_raw = max(0, measured_signal_value_raw - ADS_MIN_RAW)
    measured_signal_value = int(adjusted_raw * SCALING_FACTOR)
    measured_signal_value = min(measured_signal_value, 65535)
    
    measured_uart_value = read_uart_line(uart)

    difference = measured_uart_value - measured_signal_value

    print(f"Desired raw PWM: {desired_pot_value :<10} | Measured PWM: {measured_signal_value :<10} | UART Recieved: {measured_uart_value: <10}| Diff: {difference :<10} | Scaling {SCALING_FACTOR}" ) 
    #time.sleep(0.1) 
