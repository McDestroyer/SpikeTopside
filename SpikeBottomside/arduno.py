import serial
import time
ser = serial.Serial("/dev/ttyACM0", 9600)
ser.close()
ser.open()
time.sleep(3)
msg = b"hi :)\n"

while True:
	while ser.in_waiting:
		print(ser.read())

	ser.write(msg)

	time.sleep(0.1)
