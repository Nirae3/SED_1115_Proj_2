from machine import UART, Pin, ADC
import time

# -------------------- CONFIGURATION --------------------

ADC_PIN = 26     # Potentiometer on GP26
SEND_INTERVAL = 0.05  # Send/read every 50ms (20Hz)

# -------------------- INITIALIZE UART --------------------
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

# -------------------- INITIALIZE ADC --------------------
adc = ADC(Pin(26))
print(f"Potentiometer Reader initialized on GP")

# -------------------- SEND / RECEIVE FUNCTIONS --------------------
def send_message(value: int) -> str:
    """Send ADC value over UART as a string terminated by newline."""
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message(timeout_ms: int = 50) -> str:
    data = uart.readline()
    if data:
        return data.decode().strip()
    return "nooooo"

# -------------------- MAIN LOOP --------------------
print("-" * 60)
print(f"{'LOCAL SENDER LOG (GP26)':<30} | {'REMOTE RECEIVER LOG (GP9)'}")
print("-" * 60)

while True:
    try:
        # --- STEP 1: READ AND SEND ---
        local_value = adc.read_u16()
        sent_msg = send_message(local_value)

        # --- STEP 2: RECEIVE ---
        received_msg = read_message()

        # --- STEP 3: LOG OUTPUT ---
        send_log_output = f"Sent: {sent_msg}"
        receive_log_output = f"Received: {received_msg}" if received_msg else "No message."

        # Two-column console log
        print(f"{send_log_output:<30} | {receive_log_output}")

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(SEND_INTERVAL)
