from machine import Pin, I2C

# initialise i2c protocol on one pico
i2c = I2C(2, scl=Pin(15), sda=Pin(14)) # (id, *, scl, sda, freq=400000, timeout=50000)

i2c.scan() # scan for master pico

if message.any():
    print("")
else:
    print("waitig for messages")