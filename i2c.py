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
while True:
    buffer = [0] * 6
    i2c.writeto_then_readfrom(address, bytes([0X28]), buffer)
    x = ((buffer[0]) | ((buffer[1]) << 8))
    y = ((buffer[2]) | ((buffer[3]) << 8))
    z = ((buffer[4]) | ((buffer[5]) << 8))
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767:
        z -= 65536
    x /= 100
    y /= 100
    z /= 100
    i2c.writeto_then_readfrom(address, bytes([0X1A]), buffer)
    a = ((buffer[0]) | ((buffer[1]) << 8))
    b = ((buffer[2]) | ((buffer[3]) << 8))
    c = ((buffer[4]) | ((buffer[5]) << 8))
    if a > 32767:
        a -= 65536
    if b > 32767:
        b -= 65536
    if c > 32767:
        c -= 65536
    a /= 16
    b /= 16
    c /= 16
    vel_x = 0.01 * x/(math.cos(math.pi/180 * a) + 0.0001)
    vel_y = 0.01 * y/(math.cos(math.pi/180 * b) + 0.0001)
    print(round(vel_x, 2), round(vel_y, 2))
    time.sleep(0.01)