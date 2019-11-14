#!/usr/bin/python
# sudo apt-get install python-rpi.gpio python3-rpi.gpio
import RPi.GPIO as GPIO
import time

# Initialize GPIO with physical board pin number
GPIO.setmode(GPIO.BOARD)

# Keyboard lines GPIO association
outputLines = [8, 10, 12, 16, 18, 22, 24, 26, 32]
inputLines = [36, 38, 40, 7, 11, 13, 15, 19, 21]

# Mapping matrix keyboard layout
keyboardLayout = [
    [None, "Espace", None, None, None, None, None, None, None, None],
    [None, "#", "3", "6", "?", "I", "O", "9", "X"],
    [None, "0", "2", "5", ":", "U", "P", "8", "C"],
    [None, "*", "1", "4", "-", "Y", "M", "7", "V"],
    [None, "⏎", "Répétition", "Envoi", ";", "T", "K", "L", "Maj. D"],
    [None, "→", "Retour", "Suite", "'", "R", "H", "J", "N"],
    [None, "←", "Annulation", "Correction", ".", "E", "F", "G", "B"],
    [None, "↓", "Sommaire", "Guide", ",", "Z", "S", "D", "W"],
    [None, "↑", "Fnct", "Connexion / Fin", "Esc", "A", "Ctrl", "Q", "Maj. G", None],
]

# Configure the output lines GPIO pins to output mode with initial state to HIGH
for outputLine in outputLines:
    GPIO.setup(outputLine, GPIO.OUT, initial=GPIO.HIGH)

# Configure the input lines GPIO pins to input mode with pud_up
for inputLine in inputLines:
    GPIO.setup(inputLine, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    # For each output lines
    for lineX, outputPin in enumerate(outputLines):
        # Start listening to the line
        GPIO.output(outputPin, GPIO.LOW)

        # For each input lines
        for lineY, inputPin in enumerate(inputLines):
            # Get the state of the input line to know if a key is pressed on this line
            isKeyPressed = GPIO.input(inputPin) == GPIO.LOW

            if isKeyPressed:
                # Get the pressed key
                pressedKey = keyboardLayout[lineX][lineY]

                # Log the pressed key
                print("pressedKey: ", str(pressedKey))

                # Sleep 150ms between each press
                time.sleep(.15)

        # Stop listening to the line
        GPIO.output(outputPin, GPIO.HIGH)

# Clean the GPIO state on kill
GPIO.cleanup() 