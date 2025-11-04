from machine import UART, Pin
import time
import sys
import select

# Initialize UART1 on TX = GP8, RX = GP9
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

def send_message(message):
    """Send a message through UART."""
    uart.write(message + '\n')
    print("Sent:", message)

def read_message():
    """Read a full line from UART if available."""
    if uart.any():
        data = uart.readline()  # Reads up to newline
        if data:
            try:
                message = data.decode().strip()
                print("Received:", message)
                # Auto-reply with ACK if not an ACK itself
                if message != "ACK":
                    send_message("ACK")
                return message
            except UnicodeError:
                print("Received undecodable data:", data)
    return None

def nonblocking_input():
    """Check for user input without blocking program."""
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip()
    return None

print("UART communication test started. Type a message to send.")

while True:
    # Send KEEP_ALIVE every 0.5 seconds
    t = time.localtime()
    time_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
    send_message("KEEP_ALIVE: " + time_str)
    time.sleep(0.1)

    # Check for incoming messages
    read_message()

    # Check for user input
    user_message = nonblocking_input()
    if user_message:
        send_message(user_message)

    time.sleep(0.5)
