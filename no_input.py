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
    led1.duty_u16(32768)  # LED ON (50% brightness)
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

            if current_len >= expected_msg_len and expected_msg_len > 0:
                message = received_morse.strip()
                print("Received:", message)
                print("Decoded message:", morse_to_text(message))
                print("Blinking received Morse message...")
                blink_morse(message)

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
