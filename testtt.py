from machine import UART, Pin
import time

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)


def send_message(message): # define a function to send message
    uart.write(message + '\n')  


#check for messages, if there is any messages, save to data, and print recieved
def read_message():
    if uart.any():
        data = uart.read()
        if data:
            print("Received:", data.decode())

        

while True: # always loop to keep checking for messages.
    t = time.localtime() # format the time prettily
    time_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])  
    send_message("KEEP_ALIVE: " + time_str) # call function to send message keep alive
    read_message() # read the message always

    try: 
        user_message = input("Type a message: ") # takes input message
        if user_message.strip():
            send_message(user_message) # if there is input, send that message
    except EOFError:
        print("there was an error with the input") # otherwise throw an error
        pass
    time.sleep(0.5)
