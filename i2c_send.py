from machine import Pin, I2C

# initialise i2c protocol on one pico
i2c = I2C(1, scl=Pin(15), sda=Pin(14)) # (id, *, scl, sda, freq=400000, timeout=50000)

message = "here is a message" # prepare a message
scan_addr = i2c.scan() # scan for connected devices, returns a list

try:
    i2c.writeto(scan_addr[0], message.encode()) #(addr, buf, stop=True, /) buf = encoded message.
    print("message has been sent to address: ", hex(scan_addr[0]))
except OSError as e:
    print("The master pico wasn't able to send the data")



