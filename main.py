import cv2

# silences annoying welcome message
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from pi_connection import PiConnection
from motors import motor_speed_calc
from controller import Controller

pygame.init()

pi = PiConnection()

cont = Controller()

try:
    while 1:
        # update controller
        cont.update()

        # grab movement commands
        lateral, forward = cont.get_left()
        yaw, pitch = cont.get_right()
        throttle = cont.get_trigger()

        # convert to motor speeds
        motor_speeds = motor_speed_calc(0, pitch, yaw, throttle, forward, lateral)

        # set motors
        pi.set_motors(motor_speeds)

        # perform exchange w/Pi
        pi.update()

        # print IMU state
        print(pi.imu)

        # show cameras
        for i, frame in enumerate(pi.frames):
            if frame is None:
                continue
            cv2.imshow(f"Frame {i}", frame)

finally:
    pi.close()
    cv2.destroyAllWindows()
