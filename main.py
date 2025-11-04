from machine import UART, Pin, PWM, ADC
import time

adcA = ADC(Pin(26))
led1 = PWM(Pin(18), freq=(1000))

################ INITIALIZE UART ##########################################
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initalized correctly")
   
except Exception as e:
    print(f"ERROR: failed to initialize UART. Please check your hardware configuration")

################ MORSE CODE DEFINITION  ########################################

def string_to_morse(message):
    morse_dict = {
        'A' : '.-', 'B' : '-...', 'C' : '-.-.', 'D' : '-..', 'E' : '.', 'F' : '..-.', 'G' : '--.', 'H' : '....', 'I' : '..', 'J' : '.---',
        'K' : '-.-', 'L' : '.-..', 'M' : '--', 'N' : '-.', 'O' : '---', 'P' : '.--.', 'Q' : '--.-', 'R' : '.-.', 'S' : '...', 'T' : '-',
        'U' : '..-', 'V' : '...-', 'W' : '.--', 'X' : '-..-', 'Y' : '-.--', 'Z' : '--..', '0' : '-----', '1' : '.----', '2' : '..---',
        '3' : '...--', '4' : '....-', '5' : '.....', '6' : '-....', '7' : '--...', '8' : '---..', '9' : '----.','.' : '.-.-.-', ',' : '--..--',
        '?' : '..--..', '/' : '--..-.', '@' : '.--.-.', '!' : '-.-.--', ' ' : ' '
    }
    morse_code = ' '.join(morse_dict.get(char.upper(), '') for char in message)
    #print(morse_code)
    return morse_code

def morse_to_text(morse_code):
    # Morse code dictionary (reversed for decoding)
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',  '..': 'I', '.---': 'J', 
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', 
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0', '--..--': ',', 
        '.-.-.-': '.', '..--..': '?', '-..-.': '/', '-....-': '-', '-.--.': '(', '-.--.-': ')'
    }

    # Split Morse code into words ("/" separates words)
    words = morse_code.strip().split(' / ')
    decoded_text = []

    for word in words:
        letters = word.split()
        decoded_word = ''.join(morse_dict.get(letter, '') for letter in letters)
        decoded_text.append(decoded_word)

    #print(' '.join(decoded_text))
    return ' '.join(decoded_text)


################### SEND MESSAGE, ACKNOWLEDGE, RECIEVE MESSAGE #######################
def send_message(message): # define a function to send message
    encoded_message = string_to_morse(message)
    uart.write(encoded_message + '\n')  

'''def wait_for_ack(timeout=2):
    start=time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start)< timeout*1000:
        if uart.any():
            data=uart.readline()
            if data and data.decode().strip() == "ACK":   
                print("ACK RECIEVED")                     
                return True                               
    print("NO ACK recieved")
    return False

'''


#check for messages, if there is any messages, save to data, and print recieved
def read_message():
    if uart.any():
        data = uart.read()
        if data:
            message=data.decode().strip()
            print("Received:", message)
            print("here is the decoded message", morse_to_text(message))
            #uart.write("ACK\n")                          CODE FOR ACK
            return message
    return None


        

while True: # always loop to keep checking for messages.
    read_message() # read the message always

    try: 
        user_message = input("Type a message: ") # takes input message
        if user_message.strip():
            send_message(user_message) # if there is input, send that message
            #wait_for_ack()                             CODE FOR ACK
            #time.sleep(2)                              CODE FOR ACK
    except EOFError:
        print("there was an error with the input") # otherwise throw an error
        pass
    time.sleep(0.5)