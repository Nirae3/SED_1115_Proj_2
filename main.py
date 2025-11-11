# notes, we need to calculate the difference between the pwm values, so that if one wire is out, it accurately they pico that's recieving code, no longer recieving, takes the difference of the analog values.... 

from machine import UART, Pin, ADC
import time


# note we need to add a time-out for the reciever. If data hasn't been sent for 2 seconds
# it needs to throw an error.

"""
def timee_out_detect():
    wait for ack. 
    for i in range(2 seconds):
        data didn't arrive
        return ("No data recieved")
"""

###### UART and ADC initilizations #####################
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

adc = ADC(Pin(26))
print(f"Potentiometer Reader initialized")

################################  SEND / RECEIVE FUNCTION ###############################

def send_message(value):
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message():
    data = uart.readline()
    if data:
        return data.decode().strip() # type: ignore
    return None

last_valid_time = time.time() # get current time
################################ MAIN ###############################

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
            if time.time() - last_valid_time > 5: #if current time - last validated time >5, throw error
                print("Signal Lost: No valid data received for 5 seconds.")
            else:
                print(f"Sent: {adc_value:<10} | Waiting for data...")

        try: 
            print(f"{send_log_output:<30} | {receive_log_output :<30} | ADC: {adc_value :< 30} | UART: {uart.readline()}")
        except: 
            print("waiting for both picos to come back up")
            time.sleep(2)

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(1)
