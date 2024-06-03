import subprocess
import time

def get_temp():
	"""Return CPU temperature in degrees Celsius"""
	res = subprocess.check_output(["vcgencmd", "measure_temp"])
	return float(res[5:-3])
	
def get_cameras():
	"""Return IDs of currently active USB cameras."""
	cameras = []
	res = subprocess.check_output(["v4l2-ctl", "--list-devices"])
	lines = res.decode().split("\n")
	i = 0
	while i < len(lines):
		line = lines[i]
		if "camera" in line.lower():
			cameras.append(int(lines[i+1][-1]))
			i += 1
		i += 1
	return cameras
