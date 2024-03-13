import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
print("Working")
time.sleep(5)
GPIO.cleanup()
