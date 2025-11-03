from machine import UART, Pin, PWM
import time

# --- CONFIGURATION VARIABLES ---
ack_message="ACK"
link_status = False
ack_timeout=0.5 # Wait 500ms for ACK confirmation
link_check_interval = 5 # Check link status every 5 seconds
last_link_check_time = time.time()

# NEW: Maximum message length to limit blocking time during LED flashing
MAX_MESSAGE_LENGTH = 25

# --- LED FLASHING CONSTANTS ---
UNIT_TIME = 0.2  # Base time unit (seconds) for Morse signaling
LED_BRIGHTNESS = 32768 # 50% duty cycle

# --- MORSE CODE MAPPING ---
# Dictionary for encoding text to standard international Morse code.
TEXT_TO_MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    # Space between words is represented by a forward slash for transmission
    ' ': '/',
}
# Dictionary for decoding Morse code back to text (Reverse lookup of the above).
MORSE_TO_TEXT = {v: k for k, v in TEXT_TO_MORSE.items()}

# --- UTILITY FUNCTIONS FOR MORSE CODE ---

def text_to_morse(text):
    """Converts a string of text to a string of Morse code."""
    # Convert to uppercase to match the dictionary keys
    text = text.upper()
    morse_code = []
    
    for char in text:
        if char in TEXT_TO_MORSE:
            # Append the morse code for the character, followed by a single space
            # This space separates the codes of individual letters.
            morse_code.append(TEXT_TO_MORSE[char])
        else:
            # Skip characters not in the dictionary
            pass
            
    # Join all the letter codes with a space, then join the whole list.
    return ' '.join(morse_code)

def morse_to_text(morse_string):
    """Converts a string of Morse code back to a readable text message."""
    # Split the morse string by the single space that separates letter codes
    morse_letters = morse_string.split(' ')
    text_message = []
    
    for code in morse_letters:
        if code in MORSE_TO_TEXT:
            text_message.append(MORSE_TO_TEXT[code])
        elif code == '/':
            # The forward slash means a space between words
            text_message.append(' ')
            
    return ''.join(text_message)

# --- LED FLASHING IMPLEMENTATION (Timing Ratios: 1:3:1:3:7) ---

def flash_off(duration):
    """Turns the LED off for a specified duration to create a gap."""
    led1.duty_u16(0)
    time.sleep(duration)

def dot_flash():
    """Flashes the LED for a dot (1 unit ON, 1 unit OFF)."""
    led1.duty_u16(LED_BRIGHTNESS)
    time.sleep(UNIT_TIME * 1) # Dot duration (1 unit)
    flash_off(UNIT_TIME * 1) # Inter-element space (1 unit)

def dash_flash():
    """Flashes the LED for a dash (3 units ON, 1 unit OFF)."""
    led1.duty_u16(LED_BRIGHTNESS)
    time.sleep(UNIT_TIME * 3) # Dash duration (3 units)
    flash_off(UNIT_TIME * 1) # Inter-element space (1 unit)

def flash_morse_code(morse_string):
    """Flashes the LED according to the Morse code string."""
    print("--- Flashing Morse Code ---")
    
    # Split the message into words by the word separator (' / ')
    morse_words = morse_string.split(' / ')
    
    for i, word in enumerate(morse_words):
        # Split the word into letters by the letter separator (' ')
        morse_letters = word.split(' ')
        
        for j, letter_code in enumerate(morse_letters):
            # Flash the symbols (dots and dashes) of the letter
            for symbol in letter_code:
                if symbol == '.':
                    dot_flash()
                elif symbol == '-':
                    dash_flash()
            
            # Inter-letter gap (3 units total, but 1 unit already covered by the last dot/dash flash_off)
            if j < len(morse_letters) - 1:
                flash_off(UNIT_TIME * 2) 

        # Inter-word gap (7 units total, but 1 unit already covered by the last dot/dash flash_off)
        if i < len(morse_words) - 1:
            flash_off(UNIT_TIME * 6)
        else:
            # End of message gap (3 units before loop continues)
            flash_off(UNIT_TIME * 3)
            
    print("--- Flashing Complete ---")


# --- HARDWARE INITIALIZATION ---

try: 
    # UART 1 on GP8 (TX) and GP9 (RX)
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initialized successfully")
    
    # LED setup (PWM on GP17)
    led1 = PWM(Pin(17)) 
    led1.duty_u16(LED_BRIGHTNESS)
    
except Exception as e:
    print(f"ERROR: Failed to initialize UART. Check your Pin IDs or hardware configuration: {e}")
    while True:
        time.sleep(1)


# --- COMMUNICATION FUNCTIONS ---

def send_message(message):
    """Sends a raw string message over UART."""
    # Note: message is already Morse or a control message (ACK/KEEP_ALIVE)
    uart.write(message.encode() + b'\n')


def read_message():
    """Checks for messages, decodes user messages, sends an ACK, and flashes the LED."""
    time.sleep(0.01) # Small delay for responsiveness
    if uart.any():
        # Read until newline character (sent by send_message)
        data = uart.readline() 
        if data:
            message = data.decode().strip()
            
            # 1. Handle user message (Morse code)
            if message != ack_message and message != "KEEP_ALIVE": 
                try:
                    decoded_text = morse_to_text(message)
                    print("--- Message Received ---")
                    print(f"Received Morse: '{message}'")
                    print(f"Decoded Text: '{decoded_text}'")
                    print("--------------------------")
                    
                    # Receive: Flash the received Morse code on the LED
                    flash_morse_code(message)
                    
                except:
                    # Fallback for unexpected or poorly formatted data
                    print(f"Received unknown data: '{message}'")
            
            # 2. Send ACK regardless of message type
            # The other Pico's send_and_confirm function relies on receiving this plain string
            send_message(ack_message)
            return message 
    return None

def send_and_confirm(message):
    """Sends a message (encoded if user text) and waits for an ACK."""
    global link_status

    uart.read() # Clear buffer before sending to avoid stale ACKs
    
    message_to_send = message
    
    # 1. Encode message if it's not a control command
    if message != "KEEP_ALIVE":
        message_to_send = text_to_morse(message)
        print(f"Sending Morse: '{message_to_send}'")
        
        # Send (Flash) the Morse code signal on the sending Pico's LED (PWM output)
        flash_morse_code(message_to_send)
        
    else:
        # For KEEP_ALIVE, print status but don't encode
        print("Checking link status...")

    # 2. Send the message
    send_message(message_to_send)

    # 3. Wait for the ACK
    start_time = time.time()
    
    while (time.time() - start_time) < ack_timeout:
        if uart.any():
            data = uart.readline()
            if data:
                response = data.decode().strip()
                if response == ack_message:
                    if not link_status:
                        print("\n✅ Link is back UP! Communication confirmed.")
                    link_status = True
                    return True # Success!

        time.sleep(0.01) # Small delay to avoid busy-waiting

    # 4. If the loop completes without ACK, the link is down
    if link_status:
        print("\n ERROR: Link LOST! No acknowledgment received.")
    
    link_status = False
    return False

print("UART communication running. Link status: UNKNOWN.")

# --- MAIN COMMUNICATION LOOP ---

while True:
    # 1. --- Handle Incoming Messages (Non-Blocking) ---
    # Call read_message() to handle any incoming data and send the ACK
    read_message() 

    # 2. --- Send Keep-Alive Message (Timed) ---
    current_time = time.time()
    if current_time - last_link_check_time >= link_check_interval:
        # Check the link status by sending a message and waiting for confirmation
        send_and_confirm("KEEP_ALIVE")
        last_link_check_time = current_time

    # 3. --- Handle User Input ---
    # Only allow user messages to be sent if the link is active
    try: 
        user_message = input(f"Type message (Max {MAX_MESSAGE_LENGTH} chars, or press Enter): ") 
        
        if user_message.strip():
            # Check message length based on the new maximum limit
            if len(user_message) > MAX_MESSAGE_LENGTH:
                print(f"Message too long! Max length is {MAX_MESSAGE_LENGTH} characters. Your message has {len(user_message)} characters.")
                continue
                
            if link_status:
                # Use the confirmation function for all messages
                send_and_confirm(user_message) 
            else:
                print("Cannot send message: Link is currently DOWN.")

    except EOFError:
        print("Input error or stream closed.")
        break
    except KeyboardInterrupt:
        print("\nExiting loop.")
        break
        
    time.sleep(0.1)
