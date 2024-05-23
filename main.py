import time
import cv2
from pi_connection import PiConnection
from video_decoder import decode

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
        pi.send(str(cont.get_left()).encode())
        frame_data = pi.recv()
        frame = decode(frame_data)
        if frame is not None:
            cv2.imshow("frame", frame)

finally:
    pi.close()
    cv2.destroyAllWindows()