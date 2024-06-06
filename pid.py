import time

class PIDController:
    """A PID controller."""
    def __init__(self, KP, KI, KD, I_region, I_max):
        """
        Initialize the PIDController with its parameters.

        Parameters:
        - KP (float): Proportional gain.
        - KI (float): Integral gain.
        - KD (float): Derivative gain.
        - I_region (float): Integral region.
        - I_max (float): Integral maximum.

        Attributes:
        - prev_error (float): Previous error value.
        - prev_time (float | None): Previous time value.
        - integrator (float): Integral value.
        """
        self.KP = KP
        self.KI = KI
        self.KD = KD

        self.I_region = I_region
        self.I_max = I_max
        
        self.prev_error = 0
        self.prev_time = None
        self.integrator = 0

    def calculate(self, measurement, setpoint):
        error = setpoint - measurement

        if self.prev_time is None:
            deriv = 0
            dt = 0
        
        else:
            dt = time.time() - self.prev_time
            deriv = (error - self.prev_error) / dt

        if abs(error) < self.I_region:
            self.integrator += error * dt * self.KI
            if self.integrator > self.I_max:
                self.integrator = self.I_max
            elif self.integrator < -self.I_max:
                self.integrator = -self.I_max
        
        self.prev_time = time.time()
        self.prev_error = error

        return self.KP*error + self.KD*deriv + self.integrator
