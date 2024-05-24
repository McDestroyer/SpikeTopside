import socket
import struct
import pickle
import time

from video_decoder import decode

length_packet_size = struct.calcsize("L")

BUFFER_SIZE = 8096

class PiConnection:
    """Interface for communicating with a Raspberry Pi."""

    TCP_IP = "172.17.254.121"
    TCP_PORT = 5005

    def __init__(self, recv_timeout=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.TCP_IP, self.TCP_PORT))

        self.config = {"fps": 20, "quality": 40, "height": 200}
        self.motors = []

        self.imu = None

        self.frames = []
        self.camera = False

        self.recv_timeout = recv_timeout

    def set_camera(self, fps=None, quality=None, height=None):
        if fps is not None:
            self.config["fps"] = fps
        if quality is not None:
            self.config["quality"] = quality
        if height is not None:
            self.config["height"] = height

    def set_motors(self, motors):
        self.motors = motors[:]

    def update(self):
        out_data = {"config": self.config, "motors": self.motors}
        self._send(pickle.dumps(out_data))

        in_data = pickle.loads(self._recv())
        self.cameras = in_data["cameras"]
        self.imu = in_data["imu"]

        self.frames = []
        for _ in range(self.cameras):
            self.frames.append(decode(self._recv()))

    def _send(self, message):
        """Send a message."""
        self.s.send(struct.pack("L", len(message)))
        while message:
            self.s.send(message[:BUFFER_SIZE])
            message = message[BUFFER_SIZE:]

    def _recv(self):
        """Receive a message."""
        length_bytes = b""
        start = time.time()
        while len(length_bytes) < length_packet_size:
            length_bytes += self.s.recv(length_packet_size - len(length_bytes))
            if time.time() - start > self.recv_timeout:
                raise Exception(f"Timed out while recieving packet length (got {length_bytes}, wanted {length_packet_size-len(length_bytes)} more bytes)")
        length = struct.unpack("L", length_bytes)[0]
        msg = b""
        start = time.time()
        while len(msg) < length:
            msg += self.s.recv(length - len(msg))
            if time.time() - start > self.recv_timeout:
                raise Exception(f"Timed out while recieving packet (got {msg}, wanted {length-len(msg)} more bytes)")
        return msg

    def close(self):
        """Close the connection."""
        self.s.close()

    def __del__(self):
        self.s.close()
