import RPi.GPIO as GPIO
import serial
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
ser = serial.Serial(
    port="/dev/ttyAMA0",
    baudrate=230400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)
start = time.time()
while time.time() < start + 5:
    read_byte = ser.read()
    print("0x" + read_byte.hex() + ", ", end=" ")
GPIO.output(18, GPIO.LOW)
GPIO.cleanup()