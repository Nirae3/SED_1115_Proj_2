from machine import UART, Pin, ADC
import time

# UART and ADC setup
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("✅ UART initialized")
except Exception as e:
    print(f"❌ UART initialization failed: {e}")

adc = ADC(Pin(26))
print("✅ Potentiometer Reader initialized")

# Send / receive functions
def send_message(value):
    msg = f"DATA:{value}\n"
    uart.write(msg)
    return msg.strip()

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

# --- Main loop ---
last_valid_time = time.time()
signal_lost = False

print("___________________________________________________________")
print("      SENDER          |          RECEIVER         |  STATUS")
print("___________________________________________________________")

while True:
    try:
        # Read and send ADC
        adc_value = adc.read_u16()
        send_message(adc_value)

        # Read incoming data
        received_value = read_message()

        # Check for valid message
        if received_value is not None:
            diff = abs(adc_value - received_value)
            print(f"Sent: {adc_value:<10} | Received: {received_value:<10} | Δ={diff}")
            last_valid_time = time.time()
            signal_lost = False
        else:
            if time.time() - last_valid_time > 2 and not signal_lost:
                print("⚠️  ERROR: Signal lost - no valid data received for >2s.")
                signal_lost = True
            else:
                print(f"Sent: {adc_value:<10} | Waiting for data...")

    except Exception as e:
        print(f"💥 ERROR: {e}")

    time.sleep(1)

