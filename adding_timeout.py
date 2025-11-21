from machine import PWM, UART, Pin, ADC, I2C
import time
from ads1x15 import ADS1015

# ---------------- PWM TIMEOUT CONFIG ----------------

PWM_INPUT_PIN = 18
PWM_TIMEOUT_THRESHOLD_US = 3000   # 3 ms timeout
last_pwm_edge_time = time.ticks_us()
pwm_signal_active = False

# Setup PWM input pin
pwm_in = Pin(PWM_INPUT_PIN, Pin.IN)

# Interrupt handler that updates last time we saw a PWM edge
def pwm_edge_handler(pin):
    global last_pwm_edge_time, pwm_signal_active
    last_pwm_edge_time = time.ticks_us()
    pwm_signal_active = True

# Trigger on RISING edges only (less CPU than both edges)
pwm_in.irq(trigger=Pin.IRQ_RISING, handler=pwm_edge_handler)

def check_pwm_timeout():
    """Return True if PWM signal has been missing too long."""
    global pwm_signal_active
    elapsed = time.ticks_diff(time.ticks_us(), last_pwm_edge_time)

    if elapsed > PWM_TIMEOUT_THRESHOLD_US:
        pwm_signal_active = False
        return True
    return False

# ----------------------------------------------------

ADS1015_PWM = 2

# Initialize I2C
i2c = I2C(1, sda=Pin(14), scl=Pin(15))
external_adc = ADS1015(i2c, 0x48, 1)

# UART setup
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

# ADC and PWM output
adc_pot = ADC(Pin(26))
pwm_signal = PWM(Pin(16), freq=5000)   # 5 kHz PWM output

# UART helper
def read_uart_line(uart, timeout=2):
    rx_buffer = ""
    start = time.ticks_ms()

    while True:
        if uart.any():
            ch = uart.read(1).decode()
            if ch == "\n":
                return int(rx_buffer)
            else:
                rx_buffer += ch

        if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
            raise ValueError("UART timeout")

# Scaling
ADS_MIN_RAW = 9
SCALING_FACTOR = 41.5

# ----------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------

while True:
    try:
        # Read the potentiometer and send PWM
        desired_pot_value = adc_pot.read_u16()
        pwm_signal.duty_u16(desired_pot_value)
        uart.write((str(desired_pot_value) + "\n").encode())

        # Read ADC measuring remote signal
        measured_signal_value_raw = external_adc.read(0, ADS1015_PWM)

        adjusted_raw = max(0, measured_signal_value_raw - ADS_MIN_RAW)
        measured_signal_value = int(adjusted_raw * SCALING_FACTOR)
        measured_signal_value = min(measured_signal_value, 65535)

        # Read UART response
        measured_uart_value = read_uart_line(uart)

        # Compare expected vs measured
        difference = measured_uart_value - measured_signal_value

        # Error if large difference
        if abs(difference) > 3000:
            print("Error! PWM signal connection lost, check wires")

        # Check PWM timeout
        if check_pwm_timeout():
            status = "PWM TIMEOUT"
        else:
            status = "PWM Active"

        print(
            f"Desired raw PWM: {desired_pot_value:<10} | "
            f"UART Received: {measured_uart_value:<10} | "
            f"Measured PWM: {measured_signal_value:<10} | "
            f"Diff: {difference:<10} | Status: {status}"
        )

        # Short sleep so timeout still makes sense
        time.sleep(0.005)

    except OSError as e:
        print("Error reading from ADS1015! Check wires")
        print(f"Details: {e}")
        time.sleep(1)

    except ValueError as e:
        print("Invalid data received through UART! Check signal")
        print(f"Details: {e}")
