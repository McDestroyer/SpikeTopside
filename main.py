import pickle
import cv2
from pi_connection import PiConnection
from video_decoder import decode
from motors import motor_speed_calc

# silences annoying welcome message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

from controller import Controller


pygame.init()

pi = PiConnection()

cont = Controller()

try:
    while 1:
        cont.update()
        lateral, forward = cont.get_left()
        yaw, pitch = cont.get_right()
        throttle = cont.get_trigger()
        motor_speeds = motor_speed_calc(0, pitch, yaw, throttle, forward, lateral)

        pi.set_motors(motor_speeds)

        pi.update()

        print(pi.imu)

        for i,frame in enumerate(pi.frames):
            if frame is None:
                continue
            cv2.imshow(f"Frame {i}", frame)

finally:
    pi.close()
    cv2.destroyAllWindows()