# from smbus2 import SMBus
# import time
# address = 0x28
# bus = SMBus(1)
# bus.write_i2c_block_data(address, 0, [0X3D, 0X00])
# bus.write_i2c_block_data(address, 0, [0X3F, 0x20])
# time.sleep(1)
# bus.write_i2c_block_data(address, 0, [0X3E, 0X00])
# time.sleep(0.01)
# bus.write_i2c_block_data(address, 0, [0X07, 0])
# bus.write_i2c_block_data(address, 0, [0X3F, 0])
# time.sleep(0.01)
# bus.write_i2c_block_data(address, 0, [0X3D, 0X0C])
# time.sleep(0.02)

# while True:
#     bus.write_i2c_block_data(address, 0, [0X28])
#     buffer = bus.read_i2c_block_data(address, 0, 6)
#     x = ((buffer[0]) | ((buffer[1]) << 8)) / 100
#     y = ((buffer[2]) | ((buffer[3]) << 8)) / 100
#     z = ((buffer[4]) | ((buffer[5]) << 8)) / 100
#     print(x, y, z)

# bus.close()

from adafruit_extended_bus import ExtendedI2C as I2C
import time
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
    print(x, y, z)
