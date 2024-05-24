import math

def rotate_x_axis(vector, angle):
    """
    Rotate a 3D vector around the x-axis by a given angle in radians.
    
    Parameters:
        vector (tuple): The vector to be rotated.
        angle (float): The angle of rotation in radians.
    
    Returns:
        tuple: The rotated vector.
    """
    x, y, z = vector
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    rotated_y = y * cos_theta - z * sin_theta
    rotated_z = y * sin_theta + z * cos_theta
    return x, rotated_y, rotated_z

def rotate_y_axis(vector, angle):
    """
    Rotate a 3D vector around the y-axis by a given angle in radians.
    
    Parameters:
        vector (tuple): The vector to be rotated.
        angle (float): The angle of rotation in radians.
    
    Returns:
        tuple: The rotated vector.
    """
    x, y, z = vector
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    rotated_x = x * cos_theta + z * sin_theta
    rotated_z = -x * sin_theta + z * cos_theta
    return rotated_x, y, rotated_z

def calc_calib_angles(gvector):
    """Calculate the pitch and roll corrections needed to make gvector in the z axis"""
    x,y,z = gvector
    theta = -math.atan2(x, z)
    x,y,z = rotate_y_axis(gvector, theta)
    phi = math.atan2(y, z)
    return theta, phi

def apply_calib_angles(vec, theta, phi):
    """Apply pitch and roll corrections from calc_calib_angles"""
    return rotate_x_axis(rotate_y_axis(vec, theta), phi)
