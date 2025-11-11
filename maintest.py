from machine import UART, Pin, ADC
import time

###### UART and ADC initializations #####################
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

adc = ADC(Pin(26))
print(f"Potentiometer Reader initialized")

################################  SEND / RECEIVE FUNCTION ###############################

def send_message(value):
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message():
    data = uart.readline()
    if data:
        try:
            return int(data.decode().strip())  # Convert received ADC string to int
        except:
            return None
    return None

################################ MAIN ###############################

last_valid_time = time.time()
signal_lost = False
mismatch_count = 0
DIFF_THRESHOLD = 3000       # ADC difference threshold
TIMEOUT_SECONDS = 2         # Timeout for UART
MAX_MISMATCHES = 3          # Consecutive mismatch readings before error

print("___________________________________________________________")
print("      SENDER          |          RECEIVER         | STATUS")
print("__________________________________________________________")

while True:
    try:
        adc_value = adc.read_u16()
        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"  # send output
        received_value = read_message()

        if received_value is not None:
            diff = abs(adc_value - received_value)
            receive_log_output = f"Received: {received_value} | Δ={diff}"

            # Reset last valid time
            last_valid_time = time.time()

            # Check for analog mismatch
            if diff > DIFF_THRESHOLD:
                mismatch_count += 1
                status = f"⚠️ Analog mismatch ({mismatch_count}/{MAX_MISMATCHES})"
            else:
                mismatch_count = 0
                status = "✅ OK"

            # If mismatch persists, declare signal lost
            if mismatch_count >= MAX_MISMATCHES:
                status = "💥 ERROR: PWM/Voltage link issue detected!"
                signal_lost = True
            else:
                signal_lost = False

        else:
            receive_log_output = "No data received"
            # Check timeout
            if time.time() - last_valid_time > TIMEOUT_SECONDS:
                status = "💥 ERROR: UART disconnected or signal lost!"
                signal_lost = True
            else:
                status = "⌛ Waiting for data..."

        try:
            print(f"{send_log_output:<30} | {receive_log_output:<30} | {status}")
        except:
            print("Waiting for both Picos to come back up")
            time.sleep(2)

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(1)
