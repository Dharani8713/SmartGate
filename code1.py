import serial
import time

# Replace 'COM3' with your Arduino's port (e.g., '/dev/ttyACM0' on Linux)
arduino_port = 'COM3'
baud = 115200

ser = serial.Serial(arduino_port, baud)
time.sleep(2)  # wait for Arduino to reset

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            print(f"IR Sensor Output: {data}")
except KeyboardInterrupt:
    ser.close()
