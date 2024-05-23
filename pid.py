import time

class PDController:
    def __init__(self, KP, KD):
        self.prev_error = 0
        self.KP = KP
        self.KD = KD
        self.prev_time = None

    def calculate(self, measurement, setpoint):
        error = setpoint - measurement

        if self.prev_time is None:
            deriv = 0
        
        else:
            dt = time.time() - self.prev_time
            deriv = (error - self.prev_error) / dt

        
        self.prev_time = time.time()
        self.prev_error = error

        return self.KP*error + self.KD*deriv
