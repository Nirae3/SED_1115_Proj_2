from machine import PWM, UART, Pin, ADC, I2C
import time
#from adc1 import adc, ADS1015_PWM
from ads1x15 import ADS1015

#ADS1015 is 12-bit. reads analog voltages and turns them into digital values
ADS1015_PWM = 2

#initializing i2c bus
i2c = I2C(1, sda=Pin(14), scl=Pin(15))
external_adc = ADS1015(i2c, 0x48, 1) #(I2C bus, I2C address, parameter)

#setting up the UART
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1) 

#turns this pin to and analog-to-digital value converter 
adc_pot = ADC(Pin(26)) 
pwm_singal = PWM(Pin(16), freq=1000) #automatically generates PWM signal on pin 18

DISCONNECT_THRESHOLD = 5
DISCONNECT_COUNT_LIMIT = 10
disconnect_counter = 0

MISMATCH_LIMIT = 3000
BAD_COUNT_LIMIT = 5
bad_count = 0

#for reaceiving values from the other pico
def read_uart_line(uart, timeout=2):
    rx_buffer = ""
    start = time.ticks_ms()
    while True:
        if uart.any(): #checks if any byte has arrived
            char = uart.read(1).decode() #read one byte at a time
            if char == "\n":
                return int(rx_buffer)  #convert the received string to int
            else:
                rx_buffer += char
        #this is to make sure that if the receiver doesn't receive anything past a certain amount of time, it sends a timeout
        if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000: #multiplying by 1000 is conversion to miliseconds
            raise ValueError("UART timeout")

#storing raw values in a variable called ADS_MIN_RAW
ADS_MIN_RAW = 9
#converting raw ADS1015 reading to 16-bit value
SCALING_FACTOR = 41.5 # SCALING_FACTOR = 65535 / (  (ADS_MAX)/32  -  (ADS_MIN)/32   ) <- calculated as per

while True:
    try:
        desired_pot_value = adc_pot.read_u16() #reads from potentiometer, 
        pwm_singal.duty_u16(desired_pot_value) #generate PWM signal

        uart.write((str(desired_pot_value) + "\n").encode()) #sending the PWM value via UART

        measured_signal_value_raw = external_adc.read(0, ADS1015_PWM) #receiving and storing the measured analog value in the external_adc variable

        adjusted_raw = max(0, measured_signal_value_raw - ADS_MIN_RAW) #setting the maximum signal that can be sent through at a time
        measured_signal_value = int(adjusted_raw * SCALING_FACTOR) #turning th analog values to an integer
        measured_signal_value = min(measured_signal_value, 65535) ##setting the minimum signal that can be sent through at a time
        
        measured_uart_value = read_uart_line(uart) #reading the value gotten through uart

        difference = measured_uart_value - measured_signal_value #getting the difference in the value sent and the on received
        if difference > 3000 or difference < -3000:
            print("Error! PWM signal connection lost, check wires")

        print(f"Desired raw PWM: {desired_pot_value :<10} | Supposed to Recieve: {measured_uart_value: <10} | Measured PWM: {measured_signal_value :<10} | Diff: {difference :<10}" ) 
        time.sleep(0.5)

        # Method 1: direct wire disconnect detection
        if measured_signal_value_raw <= DISCONNECT_THRESHOLD:
            disconnect_counter += 1
        else:
            disconnect_counter = 0

        if disconnect_counter >= DISCONNECT_COUNT_LIMIT:
            print("ERROR: PWM wire disconnected from GP16!")
            disconnect_counter = 0

        # Method 2: mismatch detection
        if abs(difference) > MISMATCH_LIMIT:
            bad_count += 1
        else:
            bad_count = 0

        if bad_count >= BAD_COUNT_LIMIT:
            print("ERROR: PWM mismatch → check wires or connection lost!")
            bad_count = 0


    except OSError as e: #this catches any errors with the ADC / PWM conversion
        print("Error reading from ADS1015! Check wires")
        print(f"Details: {e}")
        time.sleep(1)
    
    except ValueError as e:
        print("Invalid data received through UART! Check signal")
        print(f"Details: {e}")
