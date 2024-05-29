import math, time
import angles
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX

gyro_deadband = 0.02 # deg/sec

class IMU:
    def __init__(self, i2c, theta=0, phi=0, alpha=0.5):
        self.working = True
        self.i2c = i2c
        try:
            self.sensor = LSM6DSOX(i2c)
        except ValueError:
            self.working = False

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.theta = theta
        self.phi = phi

        self.alpha = alpha

        self.prev_time = None
        
        self.pitch_rate = 0
        self.roll_rate = 0
        self.yaw_rate = 0

        self.gyro_x_off = 0
        self.gyro_y_off = 0
        self.gyro_z_off = 0
        
    def attempt_restart(self):
        try:
            self.sensor = LSM6DSOX(self.i2c)
            self.working = True
        except:
            self.working = False
            
    def data(self):
        if not self.working:
            return None
        return {
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
            "roll rate": self.roll_rate,
            "pitch rate": self.pitch_rate,
            "yaw rate": self.yaw_rate
        }

    def calibrate_orientation(self, duration=5):
        if not self.working:
            return
        print("Calibrating IMU...")
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.theta = 0
        self.phi = 0

        xacc = 0
        yacc = 0
        zacc = 0

        xgy = 0
        ygy = 0
        zgy = 0

        count = 0

        start = time.time()
        while time.time() - start < duration:
            try:
                xacc += self.sensor.acceleration[0]
                yacc += self.sensor.acceleration[1]
                zacc += self.sensor.acceleration[2]
                xgy += self.sensor.gyro[0]
                ygy += self.sensor.gyro[1]
                zgy += self.sensor.gyro[2]
                count += 1
                time.sleep(0.05)
            except OSError as e:
                if e.errno == 121:
                    print("Lost gyroscope.")
                    self.working = False
                    return

        xacc /= count
        yacc /= count
        zacc /= count

        xgy /= count
        ygy /= count
        zgy /= count

        self.gyro_x_off = -xgy
        self.gyro_y_off = -ygy
        self.gyro_z_off = -zgy
        
        self.theta, self.phi = angles.calc_calib_angles((xacc, yacc, zacc))

    def update(self):
        if not self.working:
                self.attempt_restart()
                return
        if self.prev_time is not None:
            dt = time.time() - self.prev_time
        else:
            dt = 0.0

        self.prev_time = time.time()

        try:
            accel_x, accel_y, accel_z = angles.apply_calib_angles(self.sensor.acceleration, self.theta, self.phi)
            gyro_x, gyro_y, gyro_z = self.sensor.gyro
        except OSError as e:
            if e.errno == 121:
                print("Lost gyroscope.")
                self.working = False
                return

        gyro_x += self.gyro_x_off
        gyro_y += self.gyro_y_off
        gyro_z += self.gyro_z_off

        gyro = (gyro_x, gyro_y, gyro_z)

        gyro_x, gyro_y, gyro_z = angles.apply_calib_angles(gyro, self.theta, self.phi)

        if abs(gyro_x) < gyro_deadband:
            gyro_x = 0
        if abs(gyro_y) < gyro_deadband:
            gyro_y = 0
        if abs(gyro_z) < gyro_deadband:
            gyro_z = 0

        pitch_acc = math.degrees(math.atan2(accel_x, math.sqrt(accel_z ** 2 + accel_y ** 2)))
        roll_acc = math.degrees(math.atan2(accel_y, math.sqrt(accel_z ** 2 + accel_x ** 2)))
        #pitch_acc = math.degrees(math.atan2(math.sqrt(accel_x ** 2 + accel_y ** 2), accel_z))

        self.yaw += math.degrees(gyro_z * dt)

        self.roll = self.alpha * (self.roll + math.degrees(gyro_x * dt)) + (1 - self.alpha) * roll_acc
        self.pitch = self.alpha * (self.pitch + math.degrees(gyro_y * dt)) + (1 - self.alpha) * pitch_acc

        self.pitch_rate = gyro_y
        self.roll_rate = gyro_x
        self.yaw_rate = gyro_z
        

if __name__ == "__main__":
    import board
    i2c = board.I2C()
    imu = IMU(i2c)
    
    if imu.working:
        imu.calibrate_orientation()
    while 1:
        if imu.working:
            imu.update()
            print("Pitch:", imu.pitch)
            print("Roll:", imu.roll)
            print("Yaw:", imu.yaw)
            time.sleep(0.02)
        else:
            print(":(")
            imu.attempt_restart()
