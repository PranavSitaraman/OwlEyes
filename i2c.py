from adafruit_extended_bus import ExtendedI2C as I2C
import time
import math
i2c = I2C(1)
address = 0x28
i2c.writeto(address, bytes([0X3D, 0X00]))
i2c.writeto(address, bytes([0X3F, 0x20]))
time.sleep(1)
i2c.writeto(address, bytes([0X3E, 0X00]))
time.sleep(1)
i2c.writeto(address, bytes([0X07, 0]))
i2c.writeto(address, bytes([0X3F, 0]))
time.sleep(1)
i2c.writeto(address, bytes([0X3D, 0X0C]))
time.sleep(1)
vel_x = 0
vel_y = 0
buffer = [0] * 6
while True:
    time.sleep(1/6 - 0.02)
    i2c.writeto_then_readfrom(address, bytes([0X28]), buffer)
    x = ((buffer[0]) | ((buffer[1]) << 8))
    y = ((buffer[2]) | ((buffer[3]) << 8))
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    x /= 100
    y /= 100
    vel_x *= 0.7
    vel_y *= 0.7
    if abs(x) > 0.2:
        vel_x += 1/6 * x
    if abs(y) > 0.2:
        vel_y += 1/6 * y
    print(round(vel_x, 2), round(vel_y, 2))