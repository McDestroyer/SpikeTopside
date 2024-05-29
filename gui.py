import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk

#Set up GUI
window = tk.Tk()  #Makes main window
window.wm_title("ROV monitor")

#Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.grid(row=0, column=0, padx=10, pady=2)

#Capture video frames

def show_frame(frames):
    for frame, display in zip(frames, displays):
        if frame is None:
            continue
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        display.imgtk = imgtk
        display.configure(image=imgtk)

def get_config():
    q = jpeg_quality.get()
    h = height.get()
    f = fps.get()
    return {
        "quality": int(q) if q else None,
        "height": int(h) if h else None,
        "fps": int(f) if f else None
    }

display1 = tk.Label(imageFrame)
display1.grid(row=1, column=0, padx=10, pady=2)  #Display 1
display2 = tk.Label(imageFrame)
display2.grid(row=1, column=1) #Display 2



jpeg_quality = tk.Scale(imageFrame, from_=1, to=100, orient=tk.HORIZONTAL)
height = tk.Scale(imageFrame, from_=50, to=300, orient=tk.HORIZONTAL)
fps = tk.Scale(imageFrame, from_=1, to=30, orient=tk.HORIZONTAL)

jpeg_quality.set(50)
height.set(150)
fps.set(15)

tk.Label(imageFrame, text="JPEG quality").grid(row=2, column=0)
tk.Label(imageFrame, text="Height").grid(row=3, column=0)
tk.Label(imageFrame, text="FPS").grid(row=4, column=0)

jpeg_quality.grid(row=2, column=1)
height.grid(row=3, column=1)
fps.grid(row=4, column=1)


displays = [display1, display2]
