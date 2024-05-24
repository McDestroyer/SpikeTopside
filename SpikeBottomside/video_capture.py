import cv2
import pickle
import time


class Camera:
    def __init__(self, _id, quality, height, fps, retry_interval=5):
        self.retry_interval = retry_interval
        self.height = height
        self.fps = fps
        self.quality = quality
        self._id = _id

        self.retry()

    def open(self):
        return self.cap is not None and self.cap.isOpened()

    def capture_frame(self):
        now = time.time()
        
        # If we're not working, retry if we've hit the interval and give up
        if not self.working:
            if now - self.last_working > self.retry_interval:
                self.retry()
            return pickle.dumps(None)

        # If called too soon, give ups
        if now - self.last_working < (1 / self.fps):
            return pickle.dumps(None)

        # Grab frame
        ret, frame = self.cap.read()

        if frame is None:
            print("No frame")
            self.working = False
            return pickle.dumps(None)

        self.last_working = now

        h, w, c = frame.shape

        # Downscale and compress
        scaling = h // self.height
        frame = cv2.resize(frame, (w // scaling, h // scaling))

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]

        res, img = cv2.imencode(".jpg", frame, encode_param)

        # Convert to bytes and send off
        data = pickle.dumps(img)

        return data

    def show_frame(self):
        frame_data = self.capture_frame()
        frame = pickle.loads(frame_data)
        if frame is not None:
            cv2.imshow("frame", cv2.imdecode(frame, 1))
            cv2.waitKey(1)

    def retry(self):
        print(f"Connecting camera {self._id}...")
        self.cap = cv2.VideoCapture(self._id)
        self.working = self.open()
        self.last_working = time.time()
