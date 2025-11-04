from machine import UART, Pin, PWM, ADC
import time

# -------------------- CONFIGURATION --------------------
IS_SENDER = True  # True if this Pico reads potentiometer and sends, False if it receives and outputs PWM
UART_BAUDRATE = 9600
TX_PIN = 8
RX_PIN = 9
PWM_PIN = 16
ADC_PIN = 26

# -------------------- INITIALIZE UART --------------------
try:
    uart = UART(1, baudrate=UART_BAUDRATE, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    uart.init(bits=8, parity=None, stop=1)
    print(f"UART initialized (TX={TX_PIN}, RX={RX_PIN})")
except Exception as e:
    print(f"UART initialization failed: {e}")

# -------------------- INITIALIZE HARDWARE --------------------
if IS_SENDER:
    adc = ADC(Pin(ADC_PIN))
    print(f"Sender mode: Reading potentiometer on GP{ADC_PIN}")
else:
    pwm_out = PWM(Pin(PWM_PIN))
    pwm_out.freq(1000)  # 1 kHz PWM
    print(f"Receiver mode: Outputting PWM on GP{PWM_PIN}")

# -------------------- SEND / RECEIVE FUNCTIONS --------------------
def send_message(value: int):
    """Send the PWM value over UART"""
    # Ensure value is integer between 0-65535
    value = max(0, min(65535, value))
    msg = str(value) + '\n'
    uart.write(msg)
    # Optional debug print
    print(f"Sent: {value}")

def read_message(timeout_ms=2000):
    """Read a value from UART"""
    start_time = time.ticks_ms()
    received = b''

    while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
        data = uart.readline()
        if data:
            received += data
            if b'\n' in received:
                msg = received.decode().strip()
                return msg
        time.sleep_ms(10)
    return None

# -------------------- MAIN LOOP --------------------
while True:
    try:
        if IS_SENDER:
            # Read potentiometer and send value
            adc_value = adc.read_u16()  # 0-65535
            send_message(adc_value)
        else:
            # Receive value and apply to PWM
            msg = read_message(timeout_ms=2000)
            if msg:
                try:
                    pwm_value = int(msg)
                    # Apply directly to PWM duty
                    pwm_out.duty_u16(pwm_value)
                    print(f"Received {pwm_value}, applied to PWM")
                except ValueError:
                    print(f"Invalid message received: {msg}")
            else:
                print("No message received.")

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(0.1)  # Shorter delay for smoother control
