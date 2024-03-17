import RPi.GPIO as GPIO
import serial
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
