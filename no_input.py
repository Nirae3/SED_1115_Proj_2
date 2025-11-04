# main 3

from machine import UART, Pin, PWM, ADC, I2C
import time
from ads1x15 import ADS1015

# -------------------- GLOBAL VARIABLES --------------------
expected_msg_len = 0
led1 = PWM(Pin(16), freq=1000)
adcA = ADC(Pin(26))

# -------------------- INITIALIZE UART --------------------
try:  
    # Handles if there is something wrong with the UART protocol, e.g., Pin configuration
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initialized correctly")
except Exception as e:
    print(f"ERROR: failed to initialize UART. Please check your hardware configuration")

# -------------------- MORSE CODE DEFINITION --------------------
def string_to_morse(message):
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,"

    try:
        message = str(message)
    except Exception:
        raise TypeError("Input couldn't be converted to a string to convert to morse code")

    if len(message) > 20:
        raise ValueError("Input must be less than 20 characters")

    for char in message:
        if char.upper() not in allowed_chars:
            raise ValueError("Input must only contain letters, numbers, and spaces")

    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', ' ': ' ', ',': '--..--', '.': '.-.-.-'
    }

    morse_code = ' '.join(morse_dict.get(char.upper(), '') for char in message)
    return morse_code


def morse_to_text(morse_code):
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
        '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
        '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
        '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
        '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
        '----.': '9', '-----': '0', ' ': ' ', '--..--': ',', '.-.-.-': '.'
    }

    words = morse_code.strip().split(' / ')
    decoded_text = []

    for word in words:
        letters = word.split()
        decoded_word = ''.join(morse_dict.get(letter, '') for letter in letters)
        decoded_text.append(decoded_word)

    return ' '.join(decoded_text)

# -------------------- LED BLINKING (MORSE) --------------------
def dot():
    led1.duty_u16(32768)  # LED ON
    time.sleep(0.4)
    led1.duty_u16(0)      # LED OFF
    time.sleep(0.4)

def line():
    led1.duty_u16(32768)  # LED ON
    time.sleep(1.2)
    led1.duty_u16(0)      # LED OFF
    time.sleep(0.4)

def blink_morse(morse_code):
    for symbol in morse_code:
        if symbol == '.':
            dot()
        elif symbol == '-':
            line()
        elif symbol == ' ':
            time.sleep(0.8)
        elif symbol == '/':
            time.sleep(1.5)

# -------------------- INITIALIZE I2C / ADC / PWM --------------------
I2C_SDA = 14
I2C_SCL = 15
ads1015_addr = 0x48
ads1015_input_channel = 2

try:
    pwm_out = PWM(Pin(18), freq=1000)
    print("PWM output initialized on PIN 18")
except Exception as e:
    print(f"ERROR: Failed to initialize PWM output: {e}")

try:
    i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
    adc = ADS1015(i2c, ads1015_addr, 1)
    address = i2c.scan()
    print("I2C address found:", [hex(a) for a in address])
except Exception as e:
    print(f"ERROR: ADS1015/I2C initialization failed: {e}")

# -------------------- SEND / RECEIVE MESSAGE --------------------
def send_message(message):
    global expected_msg_len
    encoded_message = string_to_morse(message)
    expected_msg_len = len(encoded_message)
    uart.write(encoded_message + '\n')

    print("Blinking the sent message in Morse...")
    blink_morse(encoded_message)

def read_message(timeout_ms=5000):
    global expected_msg_len
    start_time = time.ticks_ms()
    received_morse = ""

    while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
        data = uart.readline()
        if data:
            received_morse += data.decode()
            current_len = len(received_morse.strip())
            if current_len < expected_msg_len and expected_msg_len > 0:
                print(f"WARNING: Only a fragment of message received ({current_len}/{expected_msg_len}). Waiting for more")
            elif current_len >= expected_msg_len and expected_msg_len > 0:
                message = received_morse.strip()
                print("Received:", message)
                print("Here is the decoded message:", morse_to_text(message))
                print("Blinking received Morse message...")
                blink_morse(message)

                expected_msg_len = 0
                return message

        time.sleep_ms(50)

    if expected_msg_len > 0:
        expected_msg_len = 0
        raise ValueError("ERROR: Timeout. Message not received fully within the time limit")

    return None

# -------------------- AUTOMATIC ADC SENDER LOOP --------------------
while True:
    try:
        # 1. READ ADC VALUE
        raw_adc_value = adc.read(0, ads1015_input_channel)
        message_to_send = str(raw_adc_value)

        # 2. SEND MESSAGE
        print(f"Read ADC Value: {raw_adc_value}. Sending via Morse...")
        send_message(message_to_send)

        # 3. WAIT FOR REPLY/ACK
        print("Message sent, checking for reply...")
        received_reply = read_message(timeout_ms=5000)

        if received_reply is None and expected_msg_len > 0:
            raise ValueError("ERROR: Timeout reached. No reply was received from UART. Please check your hardware")
        elif received_reply is None:
            print("No reply received.")

    except ValueError as e:
        print(f"COMMUNICATION FAILURE: {e}")
    except Exception as e:
        print(f"HARDWARE ERROR: {e}")

    time.sleep(2)  # Send a new message every 2 seconds
