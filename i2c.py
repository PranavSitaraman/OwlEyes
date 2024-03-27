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
v_x = 0
v_y = 0
cur_x = 0
cur_y = 0
buffer = [0] * 6
start = time.time()
count = 0
while True:
    i2c.writeto_then_readfrom(address, bytes([0X28]), buffer)
    x = ((buffer[0]) | ((buffer[1]) << 8))
    y = ((buffer[2]) | ((buffer[3]) << 8))
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    x /= 100
    y /= 100
    cur_x += x
    cur_y += y
    count += 1
    v_x *= 0.95
    v_y *= 0.95
    if time.time() - start > 1/6 - 0.02:
        cur_x /= count
        cur_y /= count
        if abs(cur_x) > 0.25:
            v_x += 1/6 * cur_x
        if abs(cur_y) > 0.25:
            v_y += 1/6 * cur_y
        cur_x = 0
        cur_y = 0
        count = 0
        print(round(v_x, 2), round(v_y, 2))
        start = time.time()
