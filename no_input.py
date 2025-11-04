from machine import UART, Pin, ADC
import time

#### ADC configuration#######

ADC_PIN = 26  
SEND_INTERVAL = 1  # Send/read every 2 seconds

###### UART initilization #####################
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

###### ADC initilization #####################
adc = ADC(Pin(26))
print(f"Potentiometer Reader initialized on GP")

# -------------------- SEND / RECEIVE FUNCTIONS --------------------
def send_message(value):
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message():
    data = uart.readline()
    if data:
        return data.decode().strip()
    return None

# -------------------- MAIN LOOP --------------------
print("___________________________________________________________")
print("      SENDER          |          RECIEVER         ")
print("__________________________________________________________")

while True:
    try:

        adc_value = adc.read_u16()
        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"  # send output

        received_msg = read_message()
        if received_msg:
            receive_log_output=f"Recieved: {received_msg}"
        else:
            print("One of the ports is closed. Waiting... ")
        
        try: 
            print(f"{send_log_output:<30} | {receive_log_output}")
        except: 
            print("waiting for both picos to come back up")
            time.sleep(2)

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(SEND_INTERVAL)
