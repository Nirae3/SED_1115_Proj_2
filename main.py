from machine import UART, Pin, PWM, ADC
import time

adcA = ADC(Pin(26))
led1 = PWM(Pin(18), freq=(1000))
expected_msg_len=0

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


################### SEND MESSAGE, ACKNOWLEDGE, RECIEVE MESSAGE #######################
def send_message(message): # define a function to send message
    global expected_msg_len
    encoded_message = string_to_morse(message)
    expected_msg_len = len(encoded_message) # check the lenght of what we are sending
    uart.write(encoded_message + '\n')  


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
                expected_msg_len = 0 # after your'e done, clear up t he expected_msg_len
                return message
            
        time.sleep_ms(20)
    if expected_msg_len > 0:
        expected_msg_len = 0
        raise ValueError ("ERROR: Timeout. Message not recieved fully within the time limit")
    
    return None


    
while True: # always loop to keep checking for messages.
    read_message() # read the message always

    try: 
        user_message = input("Type a message: ") # takes input message
        if user_message.strip():
            send_message(user_message) # if there is input, send that message
            print("Message sent, waiting for confermation/reply ...")
            recieved_reply = read_message(timeout_ms=5000)
            if recieved_reply is None:
                raise ValueError("ERROR: Timeout reached. No reply was recieved from UART. Please check your hardware")
            #wait_for_ack()                             CODE FOR ACK
            #time.sleep(2)                              CODE FOR ACK
    except EOFError:
        print("ERROR reading input") # otherwise throw an error
        pass
    except ValueError as e:
        print(f"COMMUNICATION FAILURE: {e}")
    time.sleep(0.5)