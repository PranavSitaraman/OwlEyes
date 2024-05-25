DEBUG = False
DISPLAY = True

import math
import time
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from enum import Enum, IntEnum
import pyttsx3
import subprocess

DISPLAY = DISPLAY and (not DEBUG)

if DISPLAY:
    plt.ion()
    plt.figure(figsize=(10,6))

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 250)
tts_engine.setProperty('volume', 1.0)

if not DEBUG:
    import serial
    from adafruit_extended_bus import ExtendedI2C as I2C

CrcTable = [
    0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae, 0xf2, 0xbf, 0x68, 0x25,
    0x8b, 0xc6, 0x11, 0x5c, 0xa9, 0xe4, 0x33, 0x7e, 0xd0, 0x9d, 0x4a, 0x07,
    0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8, 0xf5, 0x1f, 0x52, 0x85, 0xc8,
    0x66, 0x2b, 0xfc, 0xb1, 0xed, 0xa0, 0x77, 0x3a, 0x94, 0xd9, 0x0e, 0x43,
    0xb6, 0xfb, 0x2c, 0x61, 0xcf, 0x82, 0x55, 0x18, 0x44, 0x09, 0xde, 0x93,
    0x3d, 0x70, 0xa7, 0xea, 0x3e, 0x73, 0xa4, 0xe9, 0x47, 0x0a, 0xdd, 0x90,
    0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f, 0x62, 0x97, 0xda, 0x0d, 0x40,
    0xee, 0xa3, 0x74, 0x39, 0x65, 0x28, 0xff, 0xb2, 0x1c, 0x51, 0x86, 0xcb,
    0x21, 0x6c, 0xbb, 0xf6, 0x58, 0x15, 0xc2, 0x8f, 0xd3, 0x9e, 0x49, 0x04,
    0xaa, 0xe7, 0x30, 0x7d, 0x88, 0xc5, 0x12, 0x5f, 0xf1, 0xbc, 0x6b, 0x26,
    0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99, 0xd4, 0x7c, 0x31, 0xe6, 0xab,
    0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14, 0x59, 0xf7, 0xba, 0x6d, 0x20,
    0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1, 0x36, 0x7b, 0x27, 0x6a, 0xbd, 0xf0,
    0x5e, 0x13, 0xc4, 0x89, 0x63, 0x2e, 0xf9, 0xb4, 0x1a, 0x57, 0x80, 0xcd,
    0x91, 0xdc, 0x0b, 0x46, 0xe8, 0xa5, 0x72, 0x3f, 0xca, 0x87, 0x50, 0x1d,
    0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2, 0xef, 0x41, 0x0c, 0xdb, 0x96,
    0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1, 0xec, 0xb0, 0xfd, 0x2a, 0x67,
    0xc9, 0x84, 0x53, 0x1e, 0xeb, 0xa6, 0x71, 0x3c, 0x92, 0xdf, 0x08, 0x45,
    0x19, 0x54, 0x83, 0xce, 0x60, 0x2d, 0xfa, 0xb7, 0x5d, 0x10, 0xc7, 0x8a,
    0x24, 0x69, 0xbe, 0xf3, 0xaf, 0xe2, 0x35, 0x78, 0xd6, 0x9b, 0x4c, 0x01,
    0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17, 0x5a, 0x06, 0x4b, 0x9c, 0xd1,
    0x7f, 0x32, 0xe5, 0xa8]

def CalCRC8(data, len):
    crc = 0
    for i in range(len):
        crc = CrcTable[(crc ^ data[i]) & 0xff]
    return crc

def LagrangeInterpolate(pointList, x):
    sum = 0
    for j in range(len(pointList)):
        value = 1
        for k in range(len(pointList)):
            if k != j:
                value *= (x - pointList[k][0]) / (pointList[j][0] - pointList[k][0])
        sum += pointList[j][1] * value
    return sum

STATE = Enum('STATE',['HEADER', 'VER_LEN','DATA'])
POINT = IntEnum('POINT',['DISTANCE', 'INTENSITY', 'ANGLE', 'TIME'], start=0)

SPEEDS = {
    0: "strolling person",
    1: "walking person",
    2: "running person",
    5: "biking person",
    9: "approaching car",
    13: "driving car",
    22: "speeding car"
}
SPEED_KEYS = list(reversed(SPEEDS.keys()))
GRID_SIZE = 50
COMPONENT_THRESH = 5
MAX_RANGE = 5
NUM_ITERATIONS = 10
MAX_DISPLACEMENT = 3
INTERPOLATION_DIST = 0.05
VEL_THRESH = 0.7
HEADER_BYTE = 0x54
VER_BYTE = 0x2C
MAC_ADDRESS = 'AC:12:2F:BF:F1:60'
START_TIME = time.time()

if not DEBUG:
    subprocess.run('rfkill unblock all', shell=True)
    time.sleep(5)
    subprocess.run('bluetoothctl power on', shell=True)
    time.sleep(5)
    subprocess.run(f'bluetoothctl connect {MAC_ADDRESS}', shell=True)

tts_engine.say('Welcome to OwlEyes. Booting OwlEyes version 1.0. Please stand by.')
tts_engine.runAndWait()

if DEBUG:
    DATA_LENGTH = 30
    MAX_SEGMENTS = 40
    RAW_VEL = [(0, 0)] * DATA_LENGTH
    RAW_DATA = [int(i, 16) for i in open("data.txt", "r").read().replace(' ', '').split(',')[:-1]]
    figure, axis = plt.subplots(math.ceil(DATA_LENGTH / 4), 4, figsize=(14, 24))
    color_options = cm.rainbow(np.linspace(0, 1, MAX_SEGMENTS))
else:
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

current_frame = []
prev_frame = []
prev_vel = []
frame_count = 0

def algorithm(frame):
    global frame_count
    global prev_vel
    global prev_frame
    global current_frame
    global color_options
    global axis
    global buffer
    global vel_x
    global vel_y
    if not DEBUG:
        i2c.writeto_then_readfrom(address, bytes([0X28]), buffer)
        x = ((buffer[0]) | ((buffer[1]) << 8))
        y = ((buffer[2]) | ((buffer[3]) << 8))
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        x /= 100
        y /= 100
        vel_x *= 0.8
        vel_y *= 0.8
        if abs(x) > 0.5:
            vel_x += 1/6 * x
        if abs(y) > 0.5:
            vel_y += 1/6 * y
    current_frame = [time.time() - START_TIME, [0, 0, 0, [], []]]
    points = [[i[0], i[1]] for i in frame if abs(i[0]) < MAX_RANGE and abs(i[1]) < MAX_RANGE]
    grid = [[0 for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
    components = []
    for i in points:
        a, b = [int(math.floor(j / ((2 * MAX_RANGE) / GRID_SIZE)) + GRID_SIZE / 2) for j in i]
        grid[a][b] -= 1
        if grid[a][b] == -COMPONENT_THRESH:
            components.append((a, b))
    components.sort()
    label = 1
    for (a, b) in components:
        if grid[a][b] >= 0:
            continue
        neighbors = [(a, b)]
        index = 0
        while index < len(neighbors):
            (i, j) = neighbors[index]
            index += 1
            if grid[i][j] >= 0:
                continue
            neighbors.extend([(i - 1, j)] if i > 0 and grid[i - 1][j] <= 0 else [])
            neighbors.extend([(i - 1, j - 1)] if i > 0 and j > 0 and grid[i - 1][j - 1] <= 0 else [])
            neighbors.extend([(i - 1, j + 1)] if i > 0 and j < GRID_SIZE - 1 and grid[i - 1][j + 1] <= 0 else [])
            neighbors.extend([(i, j + 1)] if j < GRID_SIZE - 1 and grid[i][j + 1] <= 0 else [])
            neighbors.extend([(i, j - 1)] if j > 0 and grid[i][j - 1] <= 0 else [])
            neighbors.extend([(i + 1, j)] if i < GRID_SIZE - 1 and grid[i + 1][j] <= 0 else [])
            neighbors.extend([(i + 1, j - 1)] if i < GRID_SIZE - 1 and j > 0 and grid[i + 1][j-1] <= 0 else [])
            neighbors.extend([(i + 1, j + 1)] if i < GRID_SIZE - 1 and j < GRID_SIZE - 1 and grid[i + 1][j + 1] <= 0 else [])
            grid[i][j] = label
        current_frame.append([label, 0, 0, [], []])
        label += 1
    for i in points:
        a, b = [int(math.floor(j / ((2 * MAX_RANGE) / GRID_SIZE)) + GRID_SIZE / 2) for j in i]
        current_frame[max(grid[a][b], 0) + 1][3].append(i[0])
        current_frame[max(grid[a][b], 0) + 1][4].append(i[1])
    for i in range(2, len(current_frame)):
        current_frame[i][1], current_frame[i][2] = [sum(j) / len(j) for j in current_frame[i][3:]]
    if frame_count >= 1:
        old = [(i[1], i[2], i[0]) for i in prev_frame[0][2:]]
        new = [(i[1], i[2], i[0]) for i in current_frame[2:]]
        for i in range(NUM_ITERATIONS):
            for j in old:
                for k in new:
                    if (k[0] - j[0]) ** 2 + (k[1] - j[1]) ** 2 <= (MAX_DISPLACEMENT * (2 * MAX_RANGE) / GRID_SIZE * i / NUM_ITERATIONS) ** 2:
                        old.remove(j)
                        new.remove(k)
                        current_frame[k[2] + 1][0] = j[2]
                        break
        new_max = max([j[0] for j in prev_frame[0][2:]] + [0]) + 1
        for i in new:
            current_frame[i[2] + 1][0] = new_max
            new_max += 1
    
    if DEBUG:
        axis[frame_count // 4, frame_count % 4].scatter(current_frame[1][3], current_frame[1][4], color='white')
        for i in range(2, len(current_frame)):
            axis[frame_count // 4, frame_count % 4].scatter(current_frame[i][3], current_frame[i][4], color=color_options[current_frame[i][0] - 1], s=5, label=current_frame[i][0])
            axis[frame_count // 4, frame_count % 4].scatter(current_frame[i][1], current_frame[i][2], color='black', marker='*')
        axis[frame_count // 4, frame_count % 4].scatter(0, 0, color='red', marker='x')
        axis[frame_count // 4, frame_count % 4].arrow(0, 0, RAW_VEL[frame_count][0], RAW_VEL[frame_count][1], color='red', width=0.01, head_width=0.07)
    elif DISPLAY:
        color_options = cm.rainbow(np.linspace(0, 1, len(current_frame) - 2))
        plt.scatter(current_frame[1][3], current_frame[1][4], color='white')
        for i in range(2, len(current_frame)):
            plt.scatter(current_frame[i][3], current_frame[i][4], color=color_options[current_frame[i][0] - 1], s=5, label=current_frame[i][0])
            plt.scatter(current_frame[i][1], current_frame[i][2], color='black', marker='*')
        plt.scatter(0, 0, color='red', marker='x')
        plt.arrow(0, 0, vel_y, vel_x, color='red', width=0.01, head_width=0.07)

    if len(prev_frame) == 3:
        current_vel = []
        for i in current_frame[2:]:
            if i[0] in [j[0] for j in prev_frame[0][1:]] and i[0] in [j[0] for j in prev_frame[1][1:]] and i[0] in [j[0] for j in prev_frame[2][1:]]:
                points_x, points_y = [[(k[0],k[[j for j in range(1, len(k)) if k[j][0] == i[0]][0]][p]) for k in prev_frame] + [(current_frame[0], i[p])] for p in range(1, 3)] 
                points_x.sort()
                points_y.sort()
                v_x = (LagrangeInterpolate(points_x, points_x[3][0] + INTERPOLATION_DIST) - LagrangeInterpolate(points_x, points_x[0][0] - INTERPOLATION_DIST))/(points_x[3][0] - points_x[0][0] + 2 * INTERPOLATION_DIST)
                v_y = (LagrangeInterpolate(points_y, points_y[3][0] + INTERPOLATION_DIST) - LagrangeInterpolate(points_y, points_y[0][0] - INTERPOLATION_DIST))/(points_y[3][0] - points_y[0][0] + 2 * INTERPOLATION_DIST)
                
                if DEBUG:
                    v_x += RAW_VEL[frame_count][0]
                    v_y += RAW_VEL[frame_count][1]
                    axis[frame_count // 4, frame_count % 4].arrow(points_x[3][1], points_y[3][1], v_x, v_y, color='black', width=0.01, head_width=0.07)
                else:
                    v_x += vel_y
                    v_y += vel_x
                    if DISPLAY:
                        plt.arrow(points_x[3][1], points_y[3][1], v_x, v_y, color='black', width=0.01, head_width=0.07)
                
                current_vel.append((i[0], v_x, v_y))
                if len(prev_vel) == 3:
                    if i[0] in [j[0] for j in prev_vel[0]] and i[0] in [j[0] for j in prev_vel[1]] and i[0] in [j[0] for j in prev_vel[2]]:
                        works = True
                        for j in range(3):
                            a, b = [prev_vel[j][[k for k in range(len(prev_vel[j])) if prev_vel[j][k][0] == i[0]][0]][p] for p in range(1, 3)]
                            if a * v_x + b * v_y < VEL_THRESH * ((v_x ** 2 + v_y ** 2) ** 0.5) * ((a ** 2 + b ** 2) ** 0.5):
                                works = False
                                break
                        if works:
                            clock_time = round(((450 - round((math.degrees(math.atan2(i[2], i[1])) + 360) % 360)) % 360)/30)
                            if clock_time == 0:
                                clock_time = 12
                            raw_speed = round((v_x ** 2 + v_y ** 2) ** 0.5, 2)
                            speed_translate = round((v_x ** 2 + v_y ** 2) ** 0.5, 2)
                            output_direction = round((math.degrees(math.atan2(v_y, v_x)) + 360) % 360)
                            for key in SPEED_KEYS:
                                if raw_speed >= key:
                                    speed_translate = key
                                    break
                            if speed_translate > 0:
                                print(f'Time {round(current_frame[0], 2)} s - object {i[0]} @ {clock_time}:00, {SPEEDS[speed_translate]} ({raw_speed} m/s) @ {output_direction}°')
                                tts_engine.say(f'{clock_time} o\'clock, {SPEEDS[speed_translate]} at {output_direction} degrees')
                                tts_engine.runAndWait()
        prev_vel = [current_vel] + prev_vel[:2]

    if DEBUG:
        axis[frame_count // 4, frame_count % 4].set_xlim(-MAX_RANGE, MAX_RANGE)
        axis[frame_count // 4, frame_count % 4].set_ylim(-MAX_RANGE, MAX_RANGE)
        axis[frame_count // 4, frame_count % 4].set_title(f'Time: {round(current_frame[0], 2)} s')
        axis[frame_count // 4, frame_count % 4].legend()
    elif DISPLAY:
        plt.set_xlim(-MAX_RANGE, MAX_RANGE)
        plt.set_ylim(-MAX_RANGE, MAX_RANGE)
        plt.show()
        plt.pause(0.01)

    prev_frame = [[current_frame[0]] + [i[:3] for i in current_frame[1:]]] + prev_frame[:2]
    frame_count += 1

tmp = []
frame = []
prev_timestamp = 0
last_shift_delta = 0
first = True
state = STATE.HEADER
byte_counter = 0
byte = 0

if not DEBUG:
    ser = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=230400,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
    )

while True:
    if DEBUG:
        if byte_counter == len(RAW_DATA):
            break
        byte = RAW_DATA[byte_counter]
        byte_counter += 1
    else:
        byte_read = ser.read()
        if len(byte_read) == 0:
            continue
        byte = byte_read[0]
    
    if state == STATE.HEADER:
        if byte == HEADER_BYTE:
            tmp.append(byte)
            state = STATE.VER_LEN
    elif state == STATE.VER_LEN:
        if byte == VER_BYTE:
            tmp.append(byte)
            state = STATE.DATA
        else:
            tmp = []
            state = STATE.HEADER
    elif state == STATE.DATA:
        tmp.append(byte)
        if len(tmp) == 47:
            crc = CalCRC8(tmp, len(tmp) - 1)
            if crc != tmp[len(tmp) - 1]:
                tmp = []
                state = STATE.HEADER
                continue
            last_angle = 0
            speed = 256 * tmp[3] + tmp[2]
            start_angle = 256 * tmp[5] + tmp[4]
            points = []
            for i in range(12):
                points.append([256 * tmp[7 + 3 * i] + tmp[6 + 3 * i], tmp[8 + 3 * i], 0])
            end_angle = 256 * tmp[43] + tmp[42]
            timestamp = 256 * tmp[45] + tmp[44]
            tmp = []
            state = STATE.HEADER
            diff = (end_angle / 100 - start_angle / 100 + 360) % 360
            if prev_timestamp == 0:
                prev_timestamp = timestamp
                continue
            time_step = (timestamp - prev_timestamp)/11
            angle_step = diff/11
            start = start_angle/100
            for i in range(12):
                points[i][POINT.ANGLE] = start + i * angle_step
                points[i][POINT.ANGLE] = (points[i][POINT.ANGLE] + 360) % 360
                frame.append(points[i])
            prev_timestamp = timestamp
            if speed < 0:
                continue
            for i in range(1, len(frame)):
                if (frame[0][POINT.ANGLE] - frame[i][POINT.ANGLE] + 360) % 360 > 2:
                    continue
                for n in frame:
                    angle = 0
                    if n[POINT.DISTANCE] > 0:
                        x = n[POINT.DISTANCE] + 5.9
                        y = n[POINT.DISTANCE] * 0.11923 - 18.975571
                        shift = math.atan(y / x) * 180 / math.pi
                        angle = n[POINT.ANGLE] - shift
                        last_shift_delta = shift
                    else:
                        angle = n[POINT.ANGLE] - last_shift_delta
                    angle = (angle + 360) % 360
                    n[POINT.ANGLE] = angle
                    if n[POINT.DISTANCE] == 0:
                        n[POINT.INTENSITY] = 0
                if first:
                    first = False
                    break
                final_frame = []
                for i in frame:
                    i[POINT.ANGLE] = (810 - i[POINT.ANGLE]) % 360
                    i[POINT.DISTANCE] /= 1000
                    x = i[POINT.DISTANCE] * math.cos(math.radians(i[POINT.ANGLE]))
                    y = i[POINT.DISTANCE] * math.sin(math.radians(i[POINT.ANGLE]))
                    if x != 0 or y != 0:
                        final_frame.append((x, y))
                frame = []
                algorithm(final_frame)
                if not DEBUG:
                    ser.reset_input_buffer()
                break

if DEBUG:
    plt.tight_layout()
    plt.savefig('main.png')
