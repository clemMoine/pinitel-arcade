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
from evdev import UInput, ecodes
import time
import locale
from os import system

# Load kernal module
system("modprobe evdev")

# Initialize GPIO with physical board pin number
GPIO.setmode(GPIO.BOARD)

# Keyboard lines GPIO association
rows = [8, 10, 23, 16, 18, 22, 24, 26, 32]
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
    "Espace": ecodes.KEY_SPACE,
    "#": ecodes.KEY_NUMERIC_POUND, "3": ecodes.KEY_3, "6": ecodes.KEY_6, "?": ecodes.KEY_QUESTION, "I": ecodes.KEY_I, "O": ecodes.KEY_O, "9": ecodes.KEY_9, "X": ecodes.KEY_X,
    "0": ecodes.KEY_0, "2": ecodes.KEY_2, "5": ecodes.KEY_5, ":": ecodes.KEY_EQUAL, "U": ecodes.KEY_U, "P": ecodes.KEY_P, "8": ecodes.KEY_8, "C": ecodes.KEY_C,
    "*": ecodes.KEY_KPASTERISK, "1": ecodes.KEY_1, "4": ecodes.KEY_4, "-": ecodes.KEY_MINUS, "Y": ecodes.KEY_Y, "M": ecodes.KEY_M, "7": ecodes.KEY_7, "V": ecodes.KEY_V,
    "⏎": ecodes.KEY_ENTER, "Répétition": ecodes.KEY_F6, "Envoi": ecodes.KEY_F9, ";": ecodes.KEY_SEMICOLON, "T": ecodes.KEY_T, "K": ecodes.KEY_K, "L": ecodes.KEY_L, "Maj. D": ecodes.KEY_RIGHTSHIFT,
    "→": ecodes.KEY_RIGHT, "Retour": ecodes.KEY_F5, "Suite": ecodes.KEY_F8, "'": ecodes.KEY_APOSTROPHE, "R": ecodes.KEY_R, "H": ecodes.KEY_H, "J": ecodes.KEY_J, "N": ecodes.KEY_N,
    "←": ecodes.KEY_LEFT, "Annulation": ecodes.KEY_F4, "Correction": ecodes.KEY_BACKSPACE, ".": ecodes.KEY_DOT, "E": ecodes.KEY_E, "F": ecodes.KEY_F, "G": ecodes.KEY_G, "B": ecodes.KEY_B,
    "↓": ecodes.KEY_DOWN, "Sommaire": ecodes.KEY_F3, "Guide": ecodes.KEY_F7, ",": ecodes.KEY_COMMA, "Z": ecodes.KEY_Z, "S": ecodes.KEY_S, "D": ecodes.KEY_D, "W": ecodes.KEY_W,
    "↑": ecodes.KEY_UP, "Fnct": ecodes.KEY_F2, "Connexion / Fin": ecodes.KEY_F1, "Esc": ecodes.KEY_ESC, "A": ecodes.KEY_A, "Ctrl": ecodes.KEY_LEFTCTRL, "Q": ecodes.KEY_Q, "Maj. G": ecodes.KEY_LEFTSHIFT,
}

# Class Keyboard Configure
# Configures the GPIO pins state and mode
# Listen to rows as an input
class KeyboardConfigure:
    def __init__(self, device, columns, rows, matrix, keys):
        self.previousKeys = list()
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
            self.listenKeyboard()

    def onKeyDown(self, name, value, row, column):
        # Debug
        # print("[{row}:{column}] = {key}".format(row = rowIndex, column = columnIndex, key = name))

        # Previous state of the key
        previouslyPressed = name in self.previousKeys

        # Emit the keydown
        self.device.write(ecodes.EV_KEY, value, 1)
        self.device.syn()
        self.previousKeys.append(name)

    def onKeyUp(self, name, value, row, column):
        # Debug
        # print("[{row}:{column}] = {key}".format(row = rowIndex, column = columnIndex, key = name))

        # Emit the keyup
        self.device.write(ecodes.EV_KEY, value, 0)
        self.device.syn()
        self.previousKeys.remove(name)

    def listenKeyboard(self):
        # For each columns as output
        for columnIndex, columnPin in enumerate(self.columns):
            # Start listening to the column pin
            GPIO.output(columnPin, GPIO.LOW)

            # For each rows as input
            for rowIndex, rowPin in enumerate(self.rows):
                # Get the pressed key name and value
                name = self.matrix[rowIndex][columnIndex]
                value = self.keys.get(name)

                # Get the state of the row pin to know if a key is pressed on this column:row
                if GPIO.input(rowPin) == GPIO.LOW:
                    self.onKeyDown(name, value, row = rowIndex, column = columnIndex)
                elif name in self.previousKeys:
                    self.onKeyUp(name, value, row = rowIndex, column = columnIndex)

            # Stop listening to the line
            GPIO.output(columnPin, GPIO.HIGH)

# Create the UI input device
# device = uinput.Device(list(keysAssociation.values()))
device = UInput()

try:
    print('[+] Minitel Keyboard driver')

    # Set the locales
    locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
    print('[+] Locale set to {locale}'.format(locale = locale.getlocale()))

    # Configure the GPIO pins
    KeyboardConfigure(device, columns, rows, matrix = keyboardMatrix, keys = keysAssociation)
except KeyboardInterrupt:
    print('[-] Minitel Keyboard driver')

    # Destroy the device
    # device.destroy()

    # Clean the GPIO state on kill
    GPIO.cleanup() 