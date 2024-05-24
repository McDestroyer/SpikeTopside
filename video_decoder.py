import cv2
import pickle

HEIGHT = 600

def decode(frame_data):
    img = pickle.loads(frame_data)
    if img is None:
        return None
    frame = cv2.imdecode(img, 1)

    h,w,c = frame.shape

    scaling = h/HEIGHT

    frame = cv2.resize(frame, (int(w/scaling), int(h/scaling)))

    return frame