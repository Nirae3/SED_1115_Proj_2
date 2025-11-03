#the module machine contains the class files needed to send information between Picos
from machine import Pin, PWM, UART
import time

#this is solely to give the user enough time to direct their eyes to the Pico which will dispaly morse code
time.sleep(1)

#a UART object with 8 data bits, no parity, and 1 stop bit
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

#defining variable to the uart methods; that read and write data
mtr = uart.read
mts = uart.write

message_toreceive = mtr
message_tosend = mts

#mts(b"Hello"), same as uart.write(b"Hello")

led1 = PWM(Pin(17)) #the LED on the Pico breadboard
#dot = led1.freq(1000) #the frequency of the dots 
#line = led1.freq(50000) #the frequency of the lines

#led1.freq(5000)
led1.duty_u16(32768)

def dot():
#for i in range (1):
    led1.duty_u16(32768) #the brightness of the led
    time.sleep(.4) #the time between the dots and lines should always be set to 0.4 seconds
    led1.duty_u16(0) #indicating the brightness of the LED during a pause
    time.sleep(.4)
    #print(dot)
    return(dot)

def line():
#for i in range (1):
    led1.duty_u16(0)
    time.sleep(.4) #keeps the light at 0 Hz due to previous function
    led1.duty_u16(32768)
    time.sleep(1.5) #keeps light on at 32768 Hz due to previous function
    led1.duty_u16(0)
    #print(line)
    return(line)

#while I have a message to write, allow user input
#while there is a message to receive from the other pico read me the message
while True:
    #If there are no messages being sent or received; return a message saying i am up to date
    try:
        message = input("") #sending my message to other pico
        if message:
            mts(message.encode()) #the messaging I am writing is sent from my TX pin to the other picos RX pin
            print("Sent: ")
            time.sleep(.4) #a short break inbtween me sending messages and the reading for messages
        if uart.any():
            data = mtr() #no data eqauals None, data  = turns into bytes. data holds the message
            if data:
                print("Received:", data.decode()) #translates the bytes of data to words
            time.sleep(.4)
    except:
        print("*Read All Messages*")

#if uart.any():
    #try:
        #print("Received:", mtr)
    #except:
        #print("*Read all messages*")