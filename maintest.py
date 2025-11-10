from machine import UART, Pin, ADC
import time

# UART and ADC setup
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("✅ UART initialized")
except Exception as e:
    print(f"❌ UART init failed: {e}")

adc = ADC(Pin(26))
print("✅ Potentiometer Reader initialized")

# Function to send ADC value
def send_message(value):
    msg = f"DATA:{value}\n"
    uart.write(msg)
    return msg.strip()

# Function to read incoming UART message
def read_message():
    data = uart.readline()
    if data:
        try:
            decoded = data.decode().strip()
            if decoded.startswith("DATA:"):
                return int(decoded.split(":")[1])
        except:
            pass
    return None

# Track last time we got a valid message
last_valid_time = time.time()

print("___________________________________________________________")
print("      SENDER          |          RECEIVER         ")
print("___________________________________________________________")

while True:
    try:
        # Read potentiometer and send it
        adc_value = adc.read_u16()
        send_message(adc_value)

        # Try to read from the other Pico
        received_value = read_message()

        # If we got valid data, print and reset timer
        if received_value is not None:
            print(f"Sent: {adc_value:<10} | Received: {received_value}")
            last_valid_time = time.time()
        else:
            # Check how long since last valid message
            if time.time() - last_valid_time > 5:
                print("⚠️  Signal Lost: No valid data received for 5 seconds.")
            else:
                print(f"Sent: {adc_value:<10} | Waiting for data...")

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(1)
