print("Importing libraries...")
import RPi.GPIO as GPIO


red_pin = 12
green_pin = 16
blue_pin = 20

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(blue_pin, GPIO.OUT)

def set_color(r: bool = False, g: bool = False, b: bool = False):
        GPIO.output(red_pin, r)
        GPIO.output(green_pin, g)
        GPIO.output(blue_pin, b)

set_color(r=True)


from pc_connect import PcConnect
from video_capture import Camera
from arduino_communicator import Arduino
from imu import IMU
from arduino_communicator import Arduino
from shell import get_temp, get_cameras
import board
import pickle
import cv2
import time


cams = []
"""
for i in get_cameras():
        cam = Camera(i, 50, 100, 30)
        if cam.working:
                cams.append(cam)

print("Found", len(cams), "cameras")
"""
print("Connecting to Arduino...")
ard = Arduino()
ard.setup()

i2c = board.I2C()
imu = IMU(i2c)
#imu.calibrate_orientation()
set_color(b=True)
pc = PcConnect()
set_color(g=True)

start = time.time()

temp = get_temp()
temp_checked = time.time()
check_temp_time = 1.0 # seconds

#log = lambda *_: None
log = print

try:
        while 1:
                try:
                        log("Updating IMU...")
                        imu.update()
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
                                if msg.get("reset_ard", False):
                                        ard.reset()
                                for cam in cams:
                                        imu.update()
                                        cam.fps = config.get("fps", cam.fps)
                                        cam.quality = config.get("quality", cam.quality)
                                        cam.height = config.get("height", cam.height)
                                        pc.send(cam.capture_frame())

                                log("Sending motors...")
                                motors = msg.get("motors", [1500]*6)
                                check_temp_time = msg.get("check_temp_time", check_temp_time)
                                motors = [str(int(v)) for v in motors]
                                log("Sending:", motors)
                                ard.send_pwm(motors)
                                while ard.serial_port.inWaiting(): print("Got:", ard.get_message())
                        time.sleep(.005)
                except ConnectionResetError:
                        ard.send_stop()
                        set_color(b=True)
                        pc.reconnect()
                        set_color(g=True)
                except Exception as e:
                        print(e)
                        ard.send_stop()
                        set_color(b=True)
                        pc.reconnect()
                        set_color(g=True)
                except KeyboardInterrupt:
                        raise KeyboardInterrupt

finally:
        pc.close()
        ard.send_stop()
        set_color(r=True)
        ard.close()
