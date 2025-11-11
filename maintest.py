from machine import UART, Pin, ADC, PWM
import time

# --- Configuration ---
TIMEOUT_SECONDS = 5  # <-- DEFINED HERE
SAFE_PWM_DUTY = 0    # Set PWM to 0% duty cycle (OFF) in case of signal loss

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

last_valid_time = time.time()  # last time any data was successfully received

# SEND / RECEIVE FUNCTIONS
def send_message(value):
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message():
    data = uart.readline()
    if data:
        return data.decode().strip()
    return None

# MAIN LOOP
print("___________________________________________________________")
print("           SENDER            |           RECEIVER          ")
print("___________________________________________________________")

while True:
    try:
        # Read local ADC and drive local PWM
        adc_value = adc.read_u16()  
        pwm.duty_u16(adc_value) 

        # Send our local ADC value to the other Pico
        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"
        receive_log_output = "No Data Yet"  # Default log

        # Try to read data from the other Pico
        received_msg = read_message()

        if received_msg:
            receive_log_output = f"Received: {received_msg}"
            last_valid_time = time.time()
            
            try:
                # Optionally, convert the received string to int for logging/use
                received_value = int(received_msg)
            except ValueError:
                receive_log_output = "Received: Invalid (non-numeric) Data"
        
        # --- LINK RELIABILITY & SAFE MODE LOGIC ---
        
        time_since_last_valid = time.time() - last_valid_time
        
        if time_since_last_valid > TIMEOUT_SECONDS:
            # If the link has been lost for longer than the timeout:
            print(f"\n!!! SIGNAL LOST ({TIMEOUT_SECONDS}s+): Executing SAFE MODE !!!\n")
            # Set the local PWM to a safe state (e.g., turn it off)
            pwm.duty_u16(SAFE_PWM_DUTY) 
            receive_log_output = "Link Timeout - SAFE MODE ON"
        
        # Log the current status
        print(f"{send_log_output:<30} | {receive_log_output:<30} | My PWM Value: {adc_value:<10} | Time Delta: {time_since_last_valid:.2f}s")

    except Exception as e:
        # Catches major hardware or communication errors and prevents a crash
        print(f"CRITICAL ERROR: {e}. Waiting for recovery.")
        time.sleep(1)

    time.sleep(0.3)