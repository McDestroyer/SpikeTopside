print("Importing libraries...")
from pc_connect import PcConnect
from video_capture import Camera
from arduino_communicator import Arduino
from imu import IMU
from arduino_communicator import Arduino
from shell import get_temp, get_cameras
import board
import pickle
import time

cams = []

for i in get_cameras():
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

temp = get_temp()
temp_checked = time.time()
check_temp_time = 1.0 # seconds

log = print

try:
	while 1:
		log("Updating IMU...")
		imu.update()
		try:
			log("Receiving data from PC...")
			data_in = pc.recv()
			imu.update()
			
			log("Checking temp...")
			now = time.time()
			if now - temp_checked > check_temp_time:
				temp = get_temp()
				temp_checked = now
				
			
			if data_in is not None:
				log("Sending data...")
				data = {"cameras": len(cams), "imu": imu.data(), "temp": temp}
				pc.send(pickle.dumps(data))
				log("Sending cameras...")
				msg = pickle.loads(data_in)
				config = msg["config"]
				for cam in cams:
					imu.update()
					cam.fps = config.get("fps", cam.fps)
					cam.quality = config.get("quality", cam.quality)
					cam.height = config.get("height", cam.height)
					pc.send(cam.capture_frame())
				
				log("Sending motors...")
				motors = msg.get("motors", [1500]*6)
				check_temp_time = msg.get("check_temp_time", check_temp_time)
				ard.send_pwm(motors)
				print(motors)
				ard.get_message()
			time.sleep(.005)
		except ConnectionResetError:
			pc.reconnect()
		except Exception as e:
			print(e)
			pc.reconnect()
		
finally:
	pc.close()
	ard.send_stop()

