import cv2

# silences annoying welcome message
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from pi_connection import PiConnection
from motors import motor_speed_calc
from controller import Controller

from gui import show_frame, window, get_config

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

        pi.set_camera(**get_config())

        # perform exchange w/Pi
        pi.update()

        # show cameras
       # for i, frame in enumerate(pi.frames):
        #    if frame is None:
         #       continue
          #  cv2.imshow(f"Frame {i}", frame)

        show_frame(pi.frames)
        
        window.update()

      #  cv2.waitKey(1)

finally:
    pi.close()
  #  cv2.destroyAllWindows()
