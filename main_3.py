#main 3

from machine import UART, Pin, PWM, ADC, I2C
import time
from ads1x15 import ADS1015

expected_msg_len=0
led1 = PWM(Pin(16), freq=(1000))
adcA = ADC(Pin(26))


################ INITIALIZE UART ##########################################
try:   # Handles if there is something wrong with the UART protocol. ex. Pin configuration is wrong
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initalized correctly")
   
except Exception as e:
    print(f"ERROR: failed to initialize UART. Please check your hardware configuration")

################ MORSE CODE DEFINITION  ########################################
# converts from a string to messasge
def string_to_morse(message):  
    allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .," # checks for the string to contain only the following letters

    try: # handles to make sure that the message is alsways a string 
        message=str(message)
    except Exception:
        raise TypeError("Input couldn't be converted to a string to convert to morse code")

    if len(message)>20: # lenght must only be 20 chars to make sure that all the string is sent and recieved
        raise ValueError("Input must be less than 20 characters")
    for char in message:
        if char.upper() not in allowed_chars: # checks if the characters are allowed
            raise ValueError("Input must only contain letters, numbers, and spaces")

    morse_dict = {
        'A' : '.-', 'B' : '-...', 'C' : '-.-.', 'D' : '-..', 'E' : '.', 'F' : '..-.', 'G' : '--.', 'H' : '....', 'I' : '..', 'J' : '.---',
        'K' : '-.-', 'L' : '.-..', 'M' : '--', 'N' : '-.', 'O' : '---', 'P' : '.--.', 'Q' : '--.-', 'R' : '.-.', 'S' : '...', 'T' : '-',
        'U' : '..-', 'V' : '...-', 'W' : '.--', 'X' : '-..-', 'Y' : '-.--', 'Z' : '--..', '0' : '-----', '1' : '.----', '2' : '..---',
        '3' : '...--', '4' : '....-', '5' : '.....', '6' : '-....', '7' : '--...', '8' : '---..', '9' : '----.', ' ' : ' ',
        ',' : '--..--', '.' : '.-.-.-'

    }
    morse_code = ' '.join(morse_dict.get(char.upper(), '') for char in message)  # convert char to upper, joins the chars into a single strip
    #print(morse_code)
    return morse_code

def morse_to_text(morse_code):
    # converts from morse code to message
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',  '..': 'I', '.---': 'J', 
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', 
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0',  ' ' : ' ',  
        '--..--': ',', '.-.-.-': '.'
    }

    # Split Morse code into words ("/" separates words)
    words = morse_code.strip().split(' / ') # split the words
    decoded_text = []

    for word in words:
        letters = word.split()
        decoded_word = ''.join(morse_dict.get(letter, '') for letter in letters) # takes individual morse code, looks at the dictionary, takes the letter,joins the letters
        decoded_text.append(decoded_word) # appends the list as it loops through the morse code.

    #print(' '.join(decoded_text))
    return ' '.join(decoded_text)

################### LED BLINKING (MORSE) ######################################
def dot():
    led1.duty_u16(32768)   # LED ON
    time.sleep(0.4)
    led1.duty_u16(0)       # LED OFF
    time.sleep(0.4)

def line():
    led1.duty_u16(32768)   # LED ON
    time.sleep(1.2)
    led1.duty_u16(0)       # LED OFF
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


################ INITIALIZING I2C ###############################

I2C_SDA = 14
I2C_SCL = 15
ads1015_addr = 0x48
ads1015_input_channel = 2

try:
    pwm_out = PWM(Pin(18), freq=1000)
    print(f"PWM output initialized on PIN 16")
except Exception as e:
    print(f"ERROR: Failed to initialize PWM output: {e}")


i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
adc = ADS1015(i2c, ads1015_addr, 1)

try:
    i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
    adc = ADS1015(i2c, ads1015_addr, 1)
    address = i2c.scan()
    print("I2C address found:", [hex(a) for a in address])
except Exception as e:
    print(f"ERROR: ADS1015/I2C initialization failed: {e}")

################### SEND MESSAGE, ACKNOWLEDGE, RECIEVE MESSAGE #######################
def send_message(message): # define a function to send message
    global expected_msg_len
    encoded_message = string_to_morse(message)
    expected_msg_len = len(encoded_message) # check the lenght of what we are sending
    uart.write(encoded_message + '\n')  

    print("Blinking the sent message in Morse...")
    blink_morse(encoded_message)


#check for messages, if there is any messages, save to data, and print recieved

def read_message(timeout_ms=5000):
    global expected_msg_len
    start_time = time.ticks_ms()
    received_morse = ""
    
    while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
        data = uart.readline() 
        
        if data:
            received_morse += data.decode() # if you recieve a message, format it
            current_len=len(received_morse.strip())
            if current_len < expected_msg_len and expected_msg_len > 0:
                print(f"WARNING: Only a fragment of message recieved ({current_len}/{expected_msg_len}). Waiting for more")
            elif current_len >= expected_msg_len and expected_msg_len > 0: 
                message=received_morse.strip()
                print("Received:", message)
                print("Here is the decoded message", morse_to_text(message))
                print("Blinking received Morse message...")
                blink_morse(message)

                expected_msg_len = 0 # after your'e done, clear up t he expected_msg_len
                return message
            
        time.sleep_ms(50)
    if expected_msg_len > 0:
        expected_msg_len = 0
        raise ValueError ("ERROR: Timeout. Message not recieved fully within the time limit")
    
    return None



################## GIVE USER A CHOICE TO CHOOSE FROM ###########################
# Place this function definition before your while True loop.

def handle_user_choice():
    print("\n--- Menu ---")
    print("1: Input a text message to send")
    print("2: Send current ADC/PWM sensor value")
    print("3: Check for received messages now")
    print("------------")
    choice = input("Enter option (1, 2, or 3): ").strip()
    
    if choice == '1':
        #  Option 1: Send a typed message
        user_message = input("Type your message: ")
        if user_message:
            send_message(user_message)
            return True # Indicates a send action occurred
            
    elif choice == '2':
        # Option 2: Send the ADC/PWM value
        global adc, ads1015_input_channel
        
        # Read the sensor value (assuming adc and channel are defined globally)
        raw_adc_value = adc.read(0, ads1015_input_channel)
        message_to_send = str(raw_adc_value)
        
        print(f"Read ADC Value: {raw_adc_value}. Sending via Morse...")
        send_message(message_to_send)
        return True # Indicates a send action occurred
        
    elif choice == '3':
        print("Checking for incoming message now...")
        read_message() 
        return True # Indicates a read action occurred
        
    else:
        print(f"Invalid choice: {choice}. Please enter 1, 2, or 3.")
        return False



# Ensure all global variables (expected_msg_len, adc, ADS1015_INPUT_CHANNEL)
# are defined at the top of your main.py file.

while True:
    try: 
        action_occurred = handle_user_choice()
        
        if action_occurred:
            time.sleep(0.1)
            print("Action completed. Checking for confirmation/reply...")
            recieved_reply = read_message(timeout_ms=5000)
            
            if recieved_reply is None and expected_msg_len > 0:

                raise ValueError("ERROR: Timeout reached. No reply was recieved from UART. Please check your hardware")
            elif recieved_reply is None:
                print("You didn't recieve a message")
            
    except EOFError:
        print("ERROR reading input") 
        pass
    except ValueError as e:
        print(f"COMMUNICATION FAILURE: {e}")
    except Exception as e:
        # Catch errors from ADC/general hardware issues
        print(f"HARDWARE ERROR: {e}")

    time.sleep(0.5) # General loop delay

    time.sleep(0.5)
