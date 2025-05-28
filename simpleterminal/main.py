from machine import Pin, UART, SPI, ADC, idle
import uos
import os
from time import sleep
import utime
# Save this file as ili9341.py https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from ili9341 import Display, color565
# Save this file as xglcd_font.py https://github.com/rdagger/micropython-ili9341/blob/master/xglcd_font.py
from xglcd_font import XglcdFont

# Acknowledgements: 
# Huge thanks to the following resources for their help in creating this terminal:
# https://randomnerdtutorials.com/esp32-cheap-yellow-display-cyd-pinout-esp32-2432s028r/
# https://randomnerdtutorials.com/micropython-cheap-yellow-display-board-cyd-esp32-2432s028r/
# https://github.com/rdagger/micropython-ili9341
# Andrew Markham 28/05/2025

VERSION = "0.1"

# To switch between REPL and serial mode, connect this pin to ground
# REPL = GPIO pin connected
# Normal operation = GPIO pin not connected (floating)
safe_pin = Pin(22, Pin.IN, Pin.PULL_UP)  # e.g. use GPIO22
# Set to 1 to use serial input, 0 to use fake serial input for testing
SERIAL_INPUT = 1
# Maximum number of lines to display in the terminal display
MAX_LINES = 25
# Status led (red)
led = Pin(4, Pin.OUT)
led.value(1)

# Set colors
white_color = color565(255, 255, 255)  # white color
black_color = color565(0, 0, 0)        # black color
orange_color = color565(255, 165, 0)   # orange color
font_size = 8
# Line buffer
lines = []

def initDisplay():
    # Turn on display backlight
    backlight = Pin(21, Pin.OUT)
    backlight.on()
    # Clear display
    display.clear(black_color)
    # Draw the text on the right with rotation
    display.draw_text8x8(0, display.height-font_size,
                         "morphocam X wildpose v"+VERSION, orange_color, black_color, 0)

def addLine(text,lineBuffer):
    """Add a line to the display buffer, keeping only the last MAX_LINES lines."""
    lineBuffer.append(text)
    if len(lineBuffer) > MAX_LINES:
        lineBuffer = lineBuffer[-MAX_LINES:]
    offset = 0
    MAX_LEN=int(display.width/font_size)
    for line in lineBuffer:
        offset = offset + font_size
        # We also clear the end of line to avoid ghosting
        display.draw_text8x8(0, offset, line+' '*(MAX_LEN-len(line)), white_color, black_color, 0)
        
def writeTick(counter):
    """Write the current tick count to the display."""
    text = "%010.3f" % (counter/1000.0)
    display.draw_text8x8(display.width-font_size*13, display.height-font_size,
                         text, white_color, black_color, 0)
    

# Entry - decide whether to use REPL or serial input    
if safe_pin.value():
    led.value(0) # Only detach REPL if pin is not grounded
    # Function to set up SPI for TFT display
    display_spi = SPI(1, baudrate=60000000, sck=Pin(14), mosi=Pin(13))
    # Set up display
    display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(15),
                      width=320, height=240, rotation=90)
    initDisplay()
    if SERIAL_INPUT:
        uos.dupterm(None, 0) # Detach UART0 from REPL
        # Create a UART object on UART 1, which overloads UART 0 (REPL)
        serialport = UART(1, baudrate=115200, tx=1, rx=3, timeout=100)
        serialport.write("Morphocam terminal online!\n")
    count = 0
    while True:
      # Send a string to UART
      led.value(not led.value())
      if SERIAL_INPUT:
          #serialport.write("tick %d \n"%count)
          line = serialport.readline()
      else:
          # Fake serial input for testing
          if count % 2 == 0:
              line = "fake serial input tick %d \n"%count
          else:
              line = "%d\n"%count
      if line is not None:
          addLine(line,lines)
          writeTick(utime.ticks_ms())
      else:
          writeTick(utime.ticks_ms())
          sleep(0.1)
      count+=1


