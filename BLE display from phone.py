from machine import Pin
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import tm1637
from utime import sleep, ticks_ms, ticks_diff

# Initialize display
mydisplay = tm1637.TM1637(clk=Pin(16), dio=Pin(17))

# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()

# Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)

# Create a Pin object for the onboard LED, configure it as an output
led = Pin("LED", Pin.OUT)

# Initialize the LED state to 0 (off)
led_state = 0

# Initialize variables for handling display timeout
last_data_time = ticks_ms()
display_timeout = 5000  # Display timeout duration in milliseconds

# Function to clear the display
def clear_display():
    mydisplay.show("    ")

# Define a callback function to handle received data
def on_rx(data):
    global last_data_time
    try:
        data_str = data.decode().strip()
        
        # Update the display with the received data
        clear_display()
        mydisplay.show(data_str)
        
        # Print the received data
        print("Data received: ", data_str)
        
        # Update last data received time
        last_data_time = ticks_ms()
        
        # Toggle the LED if the received data is "toggle"
        global led_state
        if data_str == 'toggle':
            led.value(not led_state)
            led_state = 1 - led_state
    except Exception as e:
        print("Unhandled exception in IRQ callback handler:", e)

# Start an infinite loop
while True:
    if sp.is_connected():  # Check if a BLE connection is established
        sp.on_write(on_rx)  # Set the callback function for data reception
        
    # Check if display timeout has occurred
    if ticks_diff(ticks_ms(), last_data_time) >= display_timeout:
        clear_display()  # Clear the display if timeout occurred

