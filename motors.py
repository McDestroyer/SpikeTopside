import numpy as np

motor_scalars = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

plan_m = np.array([[0.0,  0.0,  1.0,  0.0, -1.0,  1.0],
                   [0.0,  0.0, -1.0,  0.0, -1.0, -1.0],
                   [0.0,  0.0, -1.0,  0.0,  1.0,  1.0],
                   [0.0,  0.0,  1.0,  0.0,  1.0, -1.0],
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
    v = v * v * np.sign(v)
    m = matrix @ v
    if np.max(np.abs(m)) == 0.0:
        return m
    k = np.max(np.abs(v)) / np.max(np.abs(m))
    return k * m

def motor_speed_calc(roll=0, pitch=0, yaw=0, throttle=0, forward=0, lateral=0):
    vert = motor_speed_calc_raw(vert_m, pitch=pitch, roll=roll, throttle=throttle)
    plan = motor_speed_calc_raw(plan_m, yaw=yaw, forward=forward, lateral=lateral)

    return vert + plan
