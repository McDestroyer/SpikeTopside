import cv2
import pickle


def decode(frame_data, height=600):
    """Load and decompress a pickled frame"""
    img = pickle.loads(frame_data)

    # handles camera disconnect
    if img is None:
        return None

    # decompress
    frame = cv2.imdecode(img, 1)

    h, w, c = frame.shape

    # scale so height is constant regardless of actual resolution
    scaling = h / height

    frame = cv2.resize(frame, (int(w / scaling), int(h / scaling)))

    return frame
