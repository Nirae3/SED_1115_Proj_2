from machine import UART, Pin, PWM, ADC
import time

adcA = ADC(Pin(26))
led1 = PWM(Pin(16), freq=(1000))
expected_msg_len=0

################ INITIALIZE UART ##########################################
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initalized correctly")
except Exception as e:
    print(f"ERROR: failed to initialize UART. Please check your hardware configuration")

################ MORSE CODE DEFINITION  ########################################
def string_to_morse(message):  
    allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,"
    try:
        message=str(message)
    except Exception:
        raise TypeError("Input couldn't be converted to a string to convert to morse code")

    if len(message)>20:
        raise ValueError("Input must be less than 20 characters")
    for char in message:
        if char.upper() not in allowed_chars:
            raise ValueError("Input must only contain letters, numbers, and spaces")

    morse_dict = {
        'A' : '.-', 'B' : '-...', 'C' : '-.-.', 'D' : '-..', 'E' : '.', 'F' : '..-.', 'G' : '--.', 'H' : '....', 'I' : '..', 'J' : '.---',
        'K' : '-.-', 'L' : '.-..', 'M' : '--', 'N' : '-.', 'O' : '---', 'P' : '.--.', 'Q' : '--.-', 'R' : '.-.', 'S' : '...', 'T' : '-',
        'U' : '..-', 'V' : '...-', 'W' : '.--', 'X' : '-..-', 'Y' : '-.--', 'Z' : '--..', '0' : '-----', '1' : '.----', '2' : '..---',
        '3' : '...--', '4' : '....-', '5' : '.....', '6' : '-....', '7' : '--...', '8' : '---..', '9' : '----.', ' ' : ' ',
        ',' : '--..--', '.' : '.-.-.-'
    }
    morse_code = ' '.join(morse_dict.get(char.upper(), '') for char in message)
    return morse_code

def morse_to_text(morse_code):
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',  '..': 'I', '.---': 'J', 
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', 
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0',  ' ' : ' ',  
        '--..--': ',', '.-.-.-': '.'
    }

    words = morse_code.strip().split(' / ')
    decoded_text = []
    for word in words:
        letters = word.split()
        decoded_word = ''.join(morse_dict.get(letter, '') for letter in letters)
        decoded_text.append(decoded_word)
    return ' '.join(decoded_text)

################### SEND MESSAGE, ACKNOWLEDGE, RECEIVE MESSAGE #######################
def send_message(message):
    global expected_msg_len
    encoded_message = string_to_morse(message)
    expected_msg_len = len(encoded_message)
    uart.write(encoded_message + '\n')

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
                expected_msg_len = 0
                
                # 🔹 FLASH LED IN MORSE WHEN MESSAGE RECEIVED
                flash_morse(message)
                
                return message
            
        time.sleep_ms(20)
    if expected_msg_len > 0:
        expected_msg_len = 0
        raise ValueError("ERROR: Timeout. Message not received fully within the time limit")
    
    return None

################### MORSE LED FLASH SECTION #######################
# LED already defined: led1 = PWM(Pin(18), freq=1000)
DOT_TIME = 0.3
DASH_TIME = DOT_TIME * 3
INTRA_CHAR = DOT_TIME
INTER_CHAR = DOT_TIME * 3

def led_on():
    led1.duty_u16(32768)

def led_off():
    led1.duty_u16(0)

def flash_dot():
    led_on()
    time.sleep(DOT_TIME)
    led_off()
    time.sleep(INTRA_CHAR)

def flash_dash():
    led_on()
    time.sleep(DASH_TIME)
    led_off()
    time.sleep(INTRA_CHAR)

def flash_morse(morse_code):
    """Blink the Morse code sequence on the Pico LED."""
    print("Blinking Morse:", morse_code)
    for symbol in morse_code:
        if symbol == '.':
            flash_dot()
        elif symbol == '-':
            flash_dash()
        elif symbol == ' ':
            time.sleep(INTER_CHAR)
    led_off()

################### MAIN LOOP #######################
while True:
    read_message()

    try: 
        user_message = input("Type a message: ")
        if user_message.strip():
            send_message(user_message)
            print("Message sent, waiting for confirmation/reply ...")
            
            # 🔹 Also flash LED when you send
            morse_to_send = string_to_morse(user_message)
            flash_morse(morse_to_send)
            
            received_reply = read_message(timeout_ms=5000)
            if received_reply is None:
                raise ValueError("ERROR: Timeout reached. No reply was received from UART.")
    except EOFError:
        print("ERROR reading input")
        pass
    except ValueError as e:
        print(f"COMMUNICATION FAILURE: {e}")
    time.sleep(0.5)
