from machine import UART, Pin
import time

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)
TEST_MESSAGE = b"LOOPBACK TEST\n" # Use bytes directly

print("Starting Loopback Test...")

while True:
    # 1. Clear any old data
    uart.read() 
    time.sleep(0.5)
    uart.read() 
    
    # 2. Send the message
    uart.write(TEST_MESSAGE)
    print("-> SENT: LOOPBACK TEST")
    
    start_time = time.time()
    received_data = None
    
    # 3. Wait to receive the message back
    while time.time() - start_time < 0.2: # Wait 200ms
        if uart.any():
            received_data = uart.readline()
            break
        time.sleep(0.01)

    # 4. Check the result
    if received_data == TEST_MESSAGE:
        print("<- RECEIVED: SUCCESS! Data matched.")
    else:
        print(f"<- FAILURE! Received: {received_data}")
        
    time.sleep(2)