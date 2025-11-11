from machine import UART, Pin, PWM, ADC, I2C
import time
from ads1x15 import ADS1015
import adc1

# UART setup
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

# PWM setup
pwm = PWM(Pin(26), freq=(1000))       
print("PWM output initialized on Pin 26")

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
        adc_value = adc1.value
        pwm.duty_u16(adc_value)
        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"
        receive_log_output = "---"  # Default log

        received_msg = read_message()

        if received_msg:
            receive_log_output = f"Received: {received_msg}"
            last_valid_time = time.time()
            adc_diff = adc_value - int(received_msg)
            if adc_diff >= 1000:
                print("\n ADC diff too big")
            else: 
                print("\n diff all good")

        if time.time() - last_valid_time > 5:
            print("\nSIGNAL LOST: No valid data received for 5 seconds. !!!\n")
        print(f"{send_log_output:<30} | {receive_log_output:<30} | PWM Value: {adc1.value}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        time.sleep(1)

    time.sleep(0.3) 