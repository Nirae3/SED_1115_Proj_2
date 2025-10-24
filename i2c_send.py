from machine import Pin, I2C

# initialise i2c protocol on one pico
i2c = I2C(1, scl=Pin(15), sda=Pin(14)) # (id, *, scl, sda, freq=400000, timeout=50000)
scan_addr = i2c.scan() # scan for connected devices, returns a list

message = "here is a message" # prepare a message

# handle address not found



try scan_addr:
    print("I'll be sending to the following address: ",hex(scan_addr[0]))
exception BlockingIOError as e:
    if e.

except OSError as e:
    if e.ENXIO == errno.ENXIO:
        print("No address found")
    elif e.



try scan_addr:
    print ("I'll be sending to the following address: ",hex(scan_addr[0]))
except

def send_message(message): # need to handle empty string of a message
    try:
        i2c.writeto(scan_addr[0], message.encode()) #write to address with encoded message
        print("the message has been successfully send to address \n", )
    except OSError
        print("The master pico wasn't able to send the data")
    # need to add error case handling




if scan_addr:
    send_message


""""

convert_message_to_morse_code()


send_message(message)
    call convert_message_to_morse_code()



I2C.readfrom(scan_addr[0], 7,)


""""


############# TO add for recieve ############

"""
create a function to send a message

Create an error handling case in case message isn't recieved.

"""
