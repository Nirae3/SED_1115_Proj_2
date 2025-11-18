"""
SEND PICO()
1. set a PWM value (duty cycle) that it got from potentiometer
2. set PWM signal 
3. send PWM value through UART
4. for UART to understand how to send, we need to do the following:
    1. put data into a specific memory
    2. inform the hardware, it's ready to be sent

5. get mesaured value from recieved
6. compare with desired value 
"""

from machine import PWM, UART, Pin, ADC
import time

#UART and ADC
adc = ADC(26)
#a UART object with 8 data bits, no parity, and 1 stop bit
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

#PWM
pwm = PWM(Pin(16))
pwm.freq(1000)

#buffer for incoming data from receiver
rx_buffer = ""

while True:
    #calling the adc to read the duty cycle value read from the potentiometer
    desired_value = adc.read_u16()
    uart.write(str(desired_value) + "\n") #sending pwm value over UART #the MicroPython stores the bytes of data into a transmit buffer in the Pico’s memory
    pwm.duty_u16(desired_value)
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
