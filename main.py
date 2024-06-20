import sys
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

# Labels
dash.put_label("Height",        2, 2,   "Height")
dash.put_label("FPS",           3, 2,   "FPS")
dash.put_label("Quality",       4, 2,   "Quality")
dash.put_label("Temp interval", 5, 2,   "Temp interval")
dash.put_label("Temp",          6, 2,   "Temp", cspan=3)

# Slider bars
dash.put_scale("Height",        2, 3,   50, 300, 150, cspan=2)
dash.put_scale("FPS",           3, 3,   1, 30, 15, cspan=2)
dash.put_scale("Quality",       4, 3,   1, 100, 75, cspan=2)
dash.put_scale("Temp interval", 5, 3,   1, 3000, 1000, cspan=2)

# Orientation markers
dash.put_image("topview",       1, 2,   125, 125, "assets/topview.png", cspan=2)
dash.put_image("sideview",      1, 4,   125, 125, "assets/sideview.png")

# Cameras
dash.put_display("frame0",      1, 0,   rspan=5)
dash.put_display("frame1",      6, 0,   rspan=5)

dash.pack()

# ssh rovrunners@192.168.2.2

while True:
    pi.setup_socket()
    try:
        while 1:
            # Update controller
            cont.update()

            # Grab movement commands
            lateral, forward = cont.get_left()
            yaw, pitch = cont.get_right()
            throttle = cont.get_trigger()
            # convert to motor speeds
            motor_speeds = motor_speed_calc(0, pitch, yaw, throttle, forward, -lateral)

            # set motors
            pi.set_motors(motor_speeds)

            pi.set_camera(fps=dash.get_scale("FPS"),
                        quality=dash.get_scale("Quality"),
                        height=dash.get_scale("Height"))
            pi.set_check_temp_time(dash.get_scale("Temp interval") / 1000.0)
            # perform exchange w/Pi
            pi.update()

            dash.rotate_image("topview", pi.imu.get("yaw", 0))
            dash.rotate_image("sideview", pi.imu.get("roll", 0))

            for i in range(min(2, len(pi.frames))):
                if pi.frames[i] is not None:
                    dash.update_display(f"frame{i}", pi.frames[i])

            dash.set_label("Temp", f"Temp: {pi.temp} C")

            #show_frame(pi.frames, pi.imu)
            
            root.update()

    except ConnectionError as e:
        print(e.with_traceback(e.__traceback__))
    except tk.TclError:
        pi.close()
        print("Window closed.")
        sys.exit()
    finally:
        pi.close()
    
