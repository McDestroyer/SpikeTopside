import cv2

# silences annoying welcome message
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from pi_connection import PiConnection
from motors import motor_speed_calc
from controller import Controller

#from gui import show_frame, window, get_config, get_temp_interval

from dashboard import Dashboard
import tkinter as tk

pygame.init()

pi = PiConnection()

cont = Controller()

root = tk.Tk()
root.wm_title("ROV monitor")
dash = Dashboard(root)

dash.put_label("Height", 2, 1, "Height")
dash.put_label("FPS", 3, 1, "FPS")
dash.put_label("Quality", 4, 1, "Quality")
dash.put_label("Temp interval", 5, 1, "Temp interval")

dash.put_scale("Height", 2, 2, 50, 300, 150)
dash.put_scale("FPS", 3, 2, 1, 30, 15)
dash.put_scale("Quality", 4, 2, 1, 100, 75)
dash.put_scale("Temp interval", 5, 2, 1, 3000, 1000)

dash.put_image("topview", 6, 0, 200, 200, "assets/topview.png")
dash.put_image("sideview", 6, 4, 300, 300, "assets/sideview.png")

dash.put_display("frame0", 1, 0)
dash.put_display("frame1", 1, 4)

dash.pack()

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

        pi.set_camera(fps=dash.get_scale("FPS"),
                      quality=dash.get_scale("Quality"),
                      height=dash.get_scale("Height"))
        pi.set_check_temp_time(dash.get_scale("Temp interval") / 1000.0)
        # perform exchange w/Pi
        pi.update()

        dash.rotate_image("topview", pi.imu.get("yaw", 0))
        dash.rotate_image("sideview", pi.imu.get("pitch", 0))

        for i in range(min(2, len(pi.frames))):
            dash.update_display(f"frame{i}", pi.frames[i])

        print(pi.temp)

        #show_frame(pi.frames, pi.imu)
        
        root.update()

finally:
    pi.close()
