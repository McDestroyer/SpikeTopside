import cv2
import pickle

def decode(frame_data):
    img = pickle.loads(frame_data)
    if img is None:
        return None
    frame = cv2.imdecode(img, 1)

    return frame