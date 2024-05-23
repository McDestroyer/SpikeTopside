import socket
import struct

length_packet_size = struct.calcsize("L")

BUFFER_SIZE = 8096

class PiConnection:
    """Interface for communicating with a Raspberry Pi."""

    TCP_IP = "172.17.254.121"
    TCP_PORT = 5005

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.TCP_IP, self.TCP_PORT))

    def send(self, message):
        """Send a message."""
        self.s.send(struct.pack("L", len(message)))
        while message:
            self.s.send(message[:BUFFER_SIZE])
            message = message[BUFFER_SIZE:]

    def recv(self):
        """Receive a message."""
        length_bytes = b""
        while len(length_bytes) < length_packet_size:
            length_bytes += self.s.recv(length_packet_size)
        length = struct.unpack("L", length_bytes)[0]
        msg = b""
        while len(msg) < length:
            msg += self.s.recv(length)
        return msg

    def close(self):
        """Close the connection."""
        self.s.close()

    def __del__(self):
        self.s.close()
