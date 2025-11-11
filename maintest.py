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
pwm.freq(1000)                 # 1 kHz frequency (adjust as needed)
print("PWM output initialized on Pin 16")

last_valid_time = time.time()   # last validated time
previous_pwm_value = 0         # previous pwm value

################################
# SEND / RECEIVE FUNCTIONS
################################
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
        pwm.duty_u16(adc_value)      # Output PWM signal proportional to ADC value

        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"

        received_msg = read_message()
        if received_msg:
            receive_log_output = f"Received: {received_msg}"
            last_valid_time = time.time()

            try:
                received_value = int(received_msg)
                pwm_diff = abs(adc_value - received_value)
                if pwm_diff > 1000:   # Threshold — tweak as needed
                    print(f" PWM difference detected: {pwm_diff}")
            except ValueError:
                print("Received non-numeric data")

        else:
            # No data — check timeout
            print("One of the ports is closed. Waiting... ")
            if time.time() - last_valid_time > 5:
                print("🚨 Signal Lost: No valid data received for 5 seconds.")
            else:
                print(f"Sent: {adc_value:<10} | Waiting for data...")

        try:
            print(f"{send_log_output:<30} | {receive_log_output if received_msg else '---':<30} | PWM: {adc_value:<10}")
        except:
            print("waiting for both picos to come back up")
            time.sleep(2)

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(0.5)
