#!/usr/bin/python
# sudo apt-get install python-rpi.gpio python3-rpi.gpio
# sudo pip install python-uinput
# modprobe -i uinput
# sudo chmod 755 /home/pi/pinitel/keyboard.py
# sudo nano /etc/rc.local
## Run the keyboard driver
# sudo python3 /home/pi/pinitel/keyboard.py &

import RPi.GPIO as GPIO
import uinput
from evdev import UInput, ecodes as e
import time
from os import system

# Load kernal module
system("modprobe uinput")

# Initialize GPIO with physical board pin number
GPIO.setmode(GPIO.BOARD)

# Keyboard lines GPIO association
rows = [8, 10, 12, 16, 18, 22, 24, 26, 32]
columns = [36, 38, 40, 7, 11, 13, 15, 19, 21]

# Mapping matrix keyboard layout
keyboardMatrix = [
    [None, "Espace", None, None, None, None, None, None, None],
    [None, "#", "3", "6", "?", "I", "O", "9", "X"],
    [None, "0", "2", "5", ":", "U", "P", "8", "C"],
    [None, "*", "1", "4", "-", "Y", "M", "7", "V"],
    [None, "⏎", "Répétition", "Envoi", ";", "T", "K", "L", "Maj. D"],
    [None, "→", "Retour", "Suite", "'", "R", "H", "J", "N"],
    [None, "←", "Annulation", "Correction", ".", "E", "F", "G", "B"],
    [None, "↓", "Sommaire", "Guide", ",", "Z", "S", "D", "W"],
    [None, "↑", "Fnct", "Connexion / Fin", "Esc", "A", "Ctrl", "Q", "Maj. G"]
]

# Associated keys and events
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h#L74
keysAssociation = {
    "Espace": uinput.KEY_SPACE,
    "#": uinput.KEY_NUMERIC_POUND, "3": uinput.KEY_3, "6": uinput.KEY_6, "?": uinput.KEY_QUESTION, "I": uinput.KEY_I, "O": uinput.KEY_O, "9": uinput.KEY_9, "X": uinput.KEY_X,
    "0": uinput.KEY_0, "2": uinput.KEY_2, "5": uinput.KEY_5, ":": uinput.KEY_EQUAL, "U": uinput.KEY_U, "P": uinput.KEY_P, "8": uinput.KEY_8, "C": uinput.KEY_C,
    "*": uinput.KEY_KPASTERISK, "1": uinput.KEY_1, "4": uinput.KEY_4, "-": uinput.KEY_MINUS, "Y": uinput.KEY_Y, "M": uinput.KEY_M, "7": uinput.KEY_7, "V": uinput.KEY_V,
    "⏎": uinput.KEY_ENTER, "Répétition": uinput.KEY_F6, "Envoi": uinput.KEY_F9, ";": uinput.KEY_SEMICOLON, "T": uinput.KEY_T, "K": uinput.KEY_K, "L": uinput.KEY_L, "Maj. D": uinput.KEY_RIGHTSHIFT,
    "→": uinput.KEY_RIGHT, "Retour": uinput.KEY_F5, "Suite": uinput.KEY_F8, "'": uinput.KEY_APOSTROPHE, "R": uinput.KEY_R, "H": uinput.KEY_H, "J": uinput.KEY_J, "N": uinput.KEY_N,
    "←": uinput.KEY_LEFT, "Annulation": uinput.KEY_F4, "Correction": uinput.KEY_BACKSPACE, ".": uinput.KEY_DOT, "E": uinput.KEY_E, "F": uinput.KEY_F, "G": uinput.KEY_G, "B": uinput.KEY_B,
    "↓": uinput.KEY_DOWN, "Sommaire": uinput.KEY_F3, "Guide": uinput.KEY_F7, ",": uinput.KEY_COMMA, "Z": uinput.KEY_Z, "S": uinput.KEY_S, "D": uinput.KEY_D, "W": uinput.KEY_W,
    "↑": uinput.KEY_UP, "Fnct": uinput.KEY_F2, "Connexion / Fin": uinput.KEY_F1, "Esc": uinput.KEY_ESC, "A": uinput.KEY_A, "Ctrl": uinput.KEY_LEFTCTRL, "Q": uinput.KEY_Q, "Maj. G": uinput.KEY_LEFTSHIFT,
}

# Class Keyboard Configure
# Configures the GPIO pins state and mode
# Listen to rows as an input
class KeyboardConfigure:
    def __init__(self, device, columns, rows, matrix, keys):
        self.columns = columns
        self.device = device
        self.matrix = matrix
        self.keys = keys
        self.rows = rows

        # Configure the GPIO
        self.configureGPIO()

    def configureGPIO(self):
        # Configure the columns to output mode with initial state to HIGH
        for column in self.columns:
            GPIO.setup(column, GPIO.OUT, initial = GPIO.HIGH)
            
        # Configure the rows to input mode with pud_up
        for row in self.rows:
            GPIO.setup(row, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        # Infinite loop
        while True:
            self.onKeyPress()

    def onKeyPress(self):
        (name, value) = self.getKey()

        if value is not None:
            self.device.emit_click(value)

    def getKey(self):
        name = None
        value = None

        # For each columns as output
        for columnIndex, columnPin in enumerate(self.columns):
            # Start listening to the column pin
            GPIO.output(columnPin, GPIO.LOW)

            # For each rows as input
            for rowIndex, rowPin in enumerate(self.rows):
                # Get the state of the row pin to know if a key is pressed on this column:row
                if GPIO.input(rowPin) == GPIO.LOW:
                    # Get the pressed key name and value
                    name = self.matrix[rowIndex][columnIndex]
                    value = self.keys.get(name)

                    # Debug
                    # print("[{row}:{column}] = {key}".format(row = rowIndex, column = columnIndex, key = name))
                    break

            # Stop listening to the line
            GPIO.output(columnPin, GPIO.HIGH)

        return name, value

# Create the UI input device
device = uinput.Device(list(keysAssociation.values()))

try:
    print('[+] Minitel Keyboard driver')

    # Configure the GPIO pins
    KeyboardConfigure(device, columns, rows, matrix = keyboardMatrix, keys = keysAssociation)
except KeyboardInterrupt:
    print('[-] Minitel Keyboard driver')
    # Destroy the device
    device.destroy()

    # Clean the GPIO state on kill
    GPIO.cleanup() 