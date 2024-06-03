import numpy as np

# I honestly don't think abstraction will help this,
# best to keep it obvious what it's doing and quick to debug

# use to set polarity and adjust power
motor_coeffs = np.array([-0.6, 0.6, -0.6, -0.6, 1.0, 1.0])


# same matrix as BlueOS, but I split it into the vertical and planar components
# for convienience
plan_m = np.array([[0.0,  0.0,  1.0,  0.0,  1.0, -1.0],
                   [0.0,  0.0, -1.0,  0.0,  1.0,  1.0],
                   [0.0,  0.0,  1.0,  0.0,  1.0,  1.0],
                   [0.0,  0.0, -1.0,  0.0,  1.0, -1.0],
                   [0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [0.0,  0.0,  0.0,  0.0,  0.0,  0.0]])

vert_m = np.array([[0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
                   [0.0,  1.0,  0.0, -1.0,  0.0,  0.0],
                   [0.0, -1.0,  0.0, -1.0,  0.0,  0.0]])

def motor_speed_calc_raw(matrix, roll=0, pitch=0, yaw=0, throttle=0, forward=0, lateral=0):
    v = np.array([roll, pitch, yaw, throttle, forward, lateral])
    # do initial multiplication
    m = matrix @ v
    # if we get a zero vector, we're done
    if np.max(np.abs(m)) == 0.0:
        return m
    # otherwise, scale by (max input / max motor) to insure when our max input is 1
    # we give a maximum motor output
    k = np.max(np.abs(v)) / np.max(np.abs(m))
    return k * m

def motor_speed_calc(roll=0, pitch=0, yaw=0, throttle=0, forward=0, lateral=0):
    # find vertical and planar components
    vert = motor_speed_calc_raw(vert_m, pitch=pitch, roll=roll, throttle=throttle)
    plan = motor_speed_calc_raw(plan_m, yaw=yaw, forward=forward, lateral=lateral)

    # multiply coeffs in
    return (vert + plan) * motor_coeffs

def motor_speed_pwm(motors, min_pwm=1100, max_pwm=1900):
    slope = (max_pwm-min_pwm)/(1.0 - (-1.0))
    return slope*(motors - 1) + max_pwm
