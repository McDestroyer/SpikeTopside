import socket
import struct
import pickle
import time

from video_decoder import decode
from motors import motor_speed_pwm

length_packet_size = struct.calcsize("L")

BUFFER_SIZE = 8096

TIMEOUT_MSG = "Timed out while recv'ing packet (got {}, wanted {} more bytes)"

class PiConnection:
    """Interface for communicating with a Raspberry Pi.

    Attributes:
        self.imu - dictionary containing IMU information if available, else None
        self.frames - list of latest opencv frames from each camera
        
    Methods:
        self.update() - perform a data exchange with the Pi
        self.set_camera() - configure camera compression parameters
        self.set_motors() - set motor outputs
    """


    TCP_IP = "192.168.2.2"
    TCP_PORT = 5005

    def __init__(self, recv_timeout=3):
        """Initialize a PiConnection.

        Args:
            recv_timeout (int, optional): Time to wait for a reply from Pi. Defaults to 3.
        """
        self.s = None

        self.config = {"fps": 20, "quality": 40, "height": 200}
        self.motors = []

        self.send_reset_ard = False

        self.imu = None
        self.temp = None

        self.frames = []
        self.cameras = 0

        self.recv_timeout = recv_timeout

        self.check_temp_time = None

    def setup_socket(self) -> None:
        """Initialize the socket connection"""
        start = time.time()
        while time.time() < start + 5:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.s.connect((self.TCP_IP, self.TCP_PORT))
                break
            except ConnectionRefusedError as e:
                print(e.with_traceback(e.__traceback__))

    def set_camera(self, fps=None, quality=None, height=None):
        """Set camera compression parameters."""
        if fps is not None and fps > 0:
            self.config["fps"] = fps
        if quality is not None and quality > 0:
            self.config["quality"] = quality
        if height is not None and height > 0:
            self.config["height"] = height
    
    def reset_ard(self):
        self.send_reset_ard = True

    def set_motors(self, motors):
        """Set motor outputs."""
        self.motors = list(motor_speed_pwm(motors))

    def set_check_temp_time(self, check_temp_time):
        self.check_temp_time = check_temp_time

    def update(self):
        """Perform a data exchange with the Pi and PC"""
        out_data = {"config": self.config, "motors": self.motors, "reset_ard": self.send_reset_ard}
        self.send_reset_ard = False
        if self.check_temp_time is not None:
            out_data["check_temp_time"] = self.check_temp_time
        self._send(pickle.dumps(out_data))

        in_data = pickle.loads(self._recv())
        self.cameras = in_data["cameras"]
        self.imu = in_data["imu"]
        self.temp = in_data["temp"]

        self.frames = []
        for _ in range(self.cameras):
            # decompress frames
            self.frames.append(decode(self._recv()))

    def _send(self, message):
        """Send a message."""
        # first send the message length
        self.s.send(struct.pack("L", len(message)))

        # then send message BUFFER_SIZE bytes at a time
        while message:
            self.s.send(message[:BUFFER_SIZE])
            message = message[BUFFER_SIZE:]

    def _recv(self):
        """Receive a message."""
        # first get the length of the message
        length_bytes = b""

        start = time.time()
        while len(length_bytes) < length_packet_size:
            remaining = length_packet_size - len(length_bytes)
            # throw exception if timeout occurs
            if time.time() - start > self.recv_timeout:
                raise ConnectionError(
                    TIMEOUT_MSG.format(length_bytes, remaining)
                )

            # attempt to read remaining bytes
            length_bytes += self.s.recv(remaining)


        # convert to an int
        length = struct.unpack("L", length_bytes)[0]

        # now get the message itself
        msg = b""

        start = time.time()
        while len(msg) < length:
            # same timeout mechanics
            if time.time() - start > self.recv_timeout:
                raise Exception(
                    TIMEOUT_MSG.format(msg, length-len(msg))
                )
            # attempt to read remaining bytes
            msg += self.s.recv(length - len(msg))


        return msg

    def close(self):
        """Close the connection."""
        self.s.close()

    def __del__(self):
        self.s.close()
