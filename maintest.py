from machine import UART, Pin, ADC, PWM
import time

# UART setup
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

# ADC setup
adc = ADC(Pin(26))
print(f"Potentiometer Reader initialized")

# PWM setup
pwm_pin = Pin(16)              
pwm = PWM(pwm_pin)
pwm.freq(1000)            
print("PWM output initialized on Pin 16")

last_valid_time = time.time()   # last validated time
previous_pwm_value = 0         # previous pwm value

# SEND / RECEIVE FUNCTIONS
def send_message(value):
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message():
    data = uart.readline()
    if data:
        return data.decode().strip() # type: ignore 
    return None

# MAIN LOOP
print("___________________________________________________________")
print("      SENDER          |          RECEIVER         ")
print("__________________________________________________________")

while True:
    try:
        adc_value = adc.read_u16()  
        pwm.duty_u16(adc_value)

        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"
        receive_log_output = "---"  # Default log

        received_msg = read_message()

        if received_msg:
            receive_log_output = f"Received: {received_msg}"
            last_valid_time = time.time()
            

        if time.time() - last_valid_time > 5:
            print("\nSIGNAL LOST: No valid data received for 5 seconds. !!!\n")
            pwm.duty_u16(0) # after 5 seconds do the following
            receive_log_output = "Link Timeout - switching to pwm value #0"

        # Log the current status
        print(f"{send_log_output:<30} | {receive_log_output:<30} | PWM Value: {adc_value}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        time.sleep(1)

    time.sleep(0.3) # Increased refresh rate for better responsiveness
