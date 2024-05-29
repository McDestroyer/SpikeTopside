print("Importing libraries...")
from pc_connect import PcConnect
from video_capture import Camera
from arduino_communicator import Arduino
from imu import IMU
from arduino_communicator import Arduino
import board
import pickle
import cv2
import time

cams = []

for i in range(8):
	cam = Camera(i, 50, 100, 30)
	if cam.working:
		cams.append(cam)

print("Found", len(cams), "cameras")

print("Connecting to Arduino...")
ard = Arduino()
ard.setup()

i2c = board.I2C()
imu = IMU(i2c)
imu.calibrate_orientation()
pc = PcConnect()

start = time.time()

try:
	while 1:
		imu.update()
		try:
			data_in = pc.recv()
			if data_in is not None:
				data = {"cameras": len(cams), "imu": imu.data()}
				pc.send(pickle.dumps(data))
				msg = pickle.loads(data_in)
				config = msg["config"]
				for cam in cams:
					cam.fps = config.get("fps", cam.fps)
					cam.quality = config.get("quality", cam.quality)
					cam.height = config.get("height", cam.height)
					pc.send(cam.capture_frame())
				
				motors = msg.get("motors", [1500]*6)
				ard.send_pwm(motors)
				ard.get_message()
		except ConnectionResetError:
			pc.reconnect()
		except Exception as e:
			print(e)
			pc.reconnect()
		
finally:
	pc.close()
	ard.send_stop()

