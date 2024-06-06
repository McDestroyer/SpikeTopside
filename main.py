import sys
import cv2

# silences annoying welcome message
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from pi_connection import PiConnection
from motors import motor_speed_calc
from controller import Controller

from pid import PIDController

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

# Yaw rate PID
dash.put_label("Yaw PID enabled", 2, 5, "Yaw PID enabled? (0/1)")
dash.put_label("Yaw KP",        3, 5, "Yaw KP")
dash.put_label("Yaw KI",        4, 5, "Yaw KI")
dash.put_label("Yaw KD",        5, 5, "Yaw KD")
dash.put_label("Yaw I region",  6, 5, "Yaw I_region")
dash.put_label("Yaw I max",     7, 5, "Yaw I_max")

dash.put_entry("Yaw PID enabled", 2, 6, float, "0")
dash.put_entry("Yaw KP",        3, 6,   float, "0")
dash.put_entry("Yaw KI",        4, 6,   float, "0")
dash.put_entry("Yaw KD",        5, 6,   float, "0")
dash.put_entry("Yaw I region",  6, 6,   float, "0")
dash.put_entry("Yaw I max",     7, 6,   float, "0")

dash.put_label("Yaw rate", 3, 7, "Yaw rate: N/A")
dash.put_label("Target", 4, 7, "Target rate: N/A")
dash.put_label("PID output", 5, 7, "PID output: N/A")

dash.pack()

yaw_PID = PIDController(0, 0, 0, 0, 0)

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
            
            if dash.get_entry("Yaw PID enabled") and pi.imu is not None:
                yaw_PID.KP = dash.get_entry("Yaw KP", 0)
                yaw_PID.KI = dash.get_entry("Yaw KI", 0)
                yaw_PID.KD = dash.get_entry("Yaw KD", 0)
                yaw_PID.I_region = dash.get_entry("Yaw I region", 0)
                yaw_PID.I_max = dash.get_entry("Yaw I max", 0)
                
                target = yaw*10 # deg/s
                yaw_rate = pi.imu.get("yaw rate", 0)
                yaw = yaw_PID.calculate(yaw_rate, target)
                
                dash.put_label("Yaw rate", f"Yaw rate: {yaw_rate}")
                dash.put_label("Target", f"Target rate: {target}")
                dash.put_label("PID output", f"PID output: {yaw}")
                
                # constrain
                yaw = min(1, max(-1, yaw))
            
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
            dash.rotate_image("sideview", pi.imu.get("pitch", 0))

            for i in range(min(2, len(pi.frames))):
                dash.update_display(f"frame{i}", pi.frames[i])

            dash.set_label("Temp", f"Temp: {pi.temp} C")

            #show_frame(pi.frames, pi.imu)
            
            root.update()

    except ConnectionError as e:
        print(e.with_traceback())
    except tk.TclError:
        pi.close()
        print("Window closed.")
        sys.exit()
    finally:
        pi.close()
    
