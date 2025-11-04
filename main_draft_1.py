from machine import UART, Pin, PWM
import time

ack_message="ACK"
link_status = False
ack_timeout=0.5
link_check_interval = 5
last_link_check_time = time.time()





try: 
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART Initialized successfully")
except Exception as e:
    print("ERROR: Failed to initialize UART. Check your Pin ID's or hardware Confituration")
    while True:
        time.sleep(1)



def send_message(message): # define a function to send message
    uart.write(message.encode() + b'\n')  


#check for messages, if there is any messages, save to data, and print recieved
def read_message():
    time.sleep(0.5)
    if uart.any():
        data = uart.read()
        if data:
            message=data.decode().strip()
            if message != ack_message: # if the message that was recieved is not "ACK", print it.
                print("Received:", message)
            send_message(ack_message)
            return message ### IDK WHY
    return None

def send_and_confirm(message):
    """Sends a message and waits for an ACK to confirm the link is active."""
    global link_status

    uart.read()
    
    # 1. Send the message
    send_message(message)

    # 2. Wait for the ACK
    start_time = time.time()
    
    # Check the buffer until the timeout expires
    while (time.time() - start_time) < ack_timeout:
        if uart.any():
            data = uart.readline()
            if data:
                response = data.decode().strip()
                if response == ack_message:
                    if not link_status:
                        print("\n Link is back UP! Communication confirmed.")
                    link_status = True
                    return True # Success!

        time.sleep(0.01) # Small delay to avoid busy-waiting

    # 3. If the loop completes without ACK, the link is down
    if link_status:
        print("\nERROR: Link LOST! No acknowledgment received.")
    
    link_status = False
    return False
        
print("UART communication running. Link status: UNKNOWN.")

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
        user_message = input("Type message or press Enter to skip: ") 
        
        if user_message.strip():
            if link_status:
                print(f"Sending: {user_message}")
                # Use the confirmation function for all messages
                send_and_confirm(user_message) 
            else:
                print("⚠️ Cannot send message: Link is currently DOWN.")

    except EOFError:
        print("Input error or stream closed.")
        break
    except KeyboardInterrupt:
        print("\nExiting loop.")
        break
        
    time.sleep(0.1)