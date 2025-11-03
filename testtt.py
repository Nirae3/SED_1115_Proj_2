import time
from machine import Pin, UART

# Set up UART with baudrate, TX and RX pins
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Function to send a message over UART
def send_message(message):
    uart.write(message)  # Send the message
    print(f"Sent: {message.strip()}")

# Function to receive a message over UART
def receive_message():
    if uart.any():  # Check if there is data available to read
        message = uart.read()  # Read the message
        return message.decode().strip()  # Decode and return the message as a string
    return None  # No message received

while True:
    # Wait for the user to input a message
    user_input = input("Enter a message to send: ")

    if user_input:  # If there is a message to send
        # Send the user input as a message over UART
        send_message(user_input)

    # Wait a moment before checking for a response
    time.sleep(1)

    # Check if a message has been received
    received = receive_message()
    if received:
        print(f"Received: {received}")
    else:
        print("No message received yet.")
    
    time.sleep(1)  # Add a small delay before repeating the cycle
