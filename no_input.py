from machine import UART, Pin, PWM, ADC
import time

# -------------------- GLOBAL VARIABLES --------------------
expected_msg_len = 0
led1 = PWM(Pin(16), freq=1000)  # LED for Morse blinking feedback
pot_adc = ADC(Pin(26))          # Internal ADC for potentiometer on GP26 (ADC0)

# -------------------- INITIALIZE UART --------------------
try:
    # UART 1 on GP8 (TX) and GP9 (RX)
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initialized correctly on GP8/GP9")
except Exception as e:
    print(f"ERROR: failed to initialize UART. Please check your hardware configuration: {e}")



# -------------------- SEND / RECEIVE MESSAGE --------------------
def send_message(message): # define a function to send message
    uart.write(message + '\n')  

def read_message(timeout_ms=5000):
    global expected_msg_len
    start_time = time.ticks_ms()
    received_morse = ""

    while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
        data = uart.readline()
        if data:
            received_morse += data.decode()
            current_len = len(received_morse.strip())

            if current_len >= expected_msg_len and expected_msg_len > 0:
                message = received_morse.strip()
                print("Received:", message)

                expected_msg_len = 0
                return message

        time.sleep_ms(50)

    if expected_msg_len > 0:
        expected_msg_len = 0
        # Timeout error is commented to prevent spamming if no reply
        # raise ValueError("ERROR: Timeout. Message not received fully within the time limit")

    return None

# -------------------- AUTOMATIC POTENTIOMETER SENDER LOOP --------------------
while True:
    try:
        # 1. READ POTENTIOMETER VALUE (0 to 65535)
        raw_adc_value = pot_adc.read_u16()

        # 2. PREPARE MESSAGE
        message_to_send = str(raw_adc_value)

        # 3. SEND MESSAGE
        print(f"Reading Potentiometer (GP26): {raw_adc_value}. Sending via Morse...")
        send_message(message_to_send)

        # 4. CHECK FOR REPLY/ACK
        print("Message sent, checking for reply...")
        received_reply = read_message(timeout_ms=2000)  # Short timeout for responsiveness

        if received_reply is None:
            print("No reply received.")

    except ValueError as e:
        print(f"COMMUNICATION FAILURE: {e}")
    except Exception as e:
        print(f"HARDWARE ERROR: {e}")

    time.sleep(2)  # Send a new message every 2 seconds
