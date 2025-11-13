from machine import UART, Pin, ADC, PWM
import time

# ---------------------------------------------------------
# UART setup
# ---------------------------------------------------------
try:
    uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart.init(bits=8, parity=None, stop=1)
    print("UART initialized")
except Exception as e:
    print(f"UART initialization failed: {e}")

# ---------------------------------------------------------
# ADC setup (potentiometer / control input)
# ---------------------------------------------------------
adc = ADC(Pin(26))
print("Potentiometer Reader initialized")

# ---------------------------------------------------------
# PWM setup (output)
# ---------------------------------------------------------
pwm_pin = Pin(16)
pwm = PWM(pwm_pin)
pwm.freq(1000)
print("PWM output initialized on Pin 16")

# ---------------------------------------------------------
# Diagnostics setup
# ---------------------------------------------------------
# Sense the PWM line itself (optional connection: GP27 → GP16 via ~100kΩ resistor)
pwm_feedback = ADC(Pin(27))

last_valid_time = time.time()

# ---------------------------------------------------------
# SEND / RECEIVE FUNCTIONS
# ---------------------------------------------------------
def send_message(value):
    msg = f"{value}\n"
    uart.write(msg)
    return msg.strip()

def read_message():
    data = uart.readline()
    if data:
        return data.decode().strip()
    return None

# ---------------------------------------------------------
# Fault detection helper
# ---------------------------------------------------------
def check_pwm_health():
    """Check PWM line voltage to detect ground or signal faults."""
    val = pwm_feedback.read_u16()
    volts = val * 3.3 / 65535

    if volts > 3.0:
        return "⚠️ PWM line stuck HIGH — possible ground disconnect or short to 3.3V"
    elif volts < 0.1:
        return "⚠️ PWM line stuck LOW — possible disconnection"
    else:
        return None  # looks normal

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
print("___________________________________________________________")
print("      SENDER          |          RECEIVER         ")
print("___________________________________________________________")

while True:
    try:
        # --- Read and send ADC value ---
        adc_value = adc.read_u16()
        pwm.duty_u16(adc_value)

        sent_msg = send_message(adc_value)
        send_log_output = f"Sent: {sent_msg}"
        receive_log_output = "---"

        # --- UART Receive and validate ---
        received_msg = read_message()

        if received_msg:
            receive_log_output = f"Received: {received_msg}"
            last_valid_time = time.time()

            try:
                received_value = int(received_msg)
                pwm_diff = abs(adc_value - received_value)
                if pwm_diff > 1000:
                    receive_log_output += f" (DIFF: {pwm_diff}!)"
            except ValueError:
                receive_log_output += " (Bad Data!)"

        # --- UART Timeout Detection ---
        if time.time() - last_valid_time > 5:
            print("\n!!! SIGNAL LOST: No valid UART data for 5 seconds. !!!\n")
            last_valid_time = time.time()  # prevent repeated spam

        # --- PWM Health Check ---
        fault_msg = check_pwm_health()
        if fault_msg:
            print(fault_msg)

        # --- Print summary ---
        print(f"{send_log_output:<30} | {receive_log_output:<30} | PWM Value: {adc_value}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        time.sleep(1)

    time.sleep(0.3)
