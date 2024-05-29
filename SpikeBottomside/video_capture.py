import cv2
import pickle
import time

class Camera:
        def __init__(self, _id, quality, height, fps, retry_interval=10):
                self.last_working = time.time() - retry_interval - 1
                self.retry_interval = retry_interval
                self.height = 200
                self.fps = fps
                self.quality = quality
                self._id = _id
                
                
                self.retry()

        def open(self):
                return self.cap is not None and self.cap.isOpened()


        def capture_frame(self):
                now = time.time()
                if not self.working and now - self.last_working > self.retry_interval:
                        self.retry()
                        return pickle.dumps(None)
                                
                if now - self.last_working < (1 / self.fps):
                        return pickle.dumps(None)
                
                ret, frame = self.cap.read()
                
                if frame is None:
                        self.working = False
                        return pickle.dumps(None)
                        
                self.last_working = now
                        
                h,w,c = frame.shape
                
                
                scaling = max(1, h // max(1, self.height))
                frame = cv2.resize(frame, (w//scaling,h//scaling))

                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]

                res, img = cv2.imencode(".jpg", frame, encode_param)

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
                
