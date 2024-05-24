import struct
import socket
import time

length_packet_size = struct.calcsize("L")
BUFFER_SIZE = 1024

RECV_TIMEOUT = 3


class PcConnect:
    TCP_IP = "0.0.0.0"
    TCP_PORT = 5005

    def __init__(self):
        self.connect()

    def close(self):
        self.conn.close()

    def connect(self):
        print("Waiting for connection...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((PcConnect.TCP_IP, PcConnect.TCP_PORT))
        self.sock.listen(1)

        self.conn, self.addr = self.sock.accept()
        self.conn.settimeout(5)
        print("Connection address:", self.addr)

    def send(self, data):
        self.conn.send(struct.pack("L", len(data)))
        # seems like data sometimes gets curropted if we send more than 2000ish bytes
        # at a time? idk why yet.
        while data:
            self.conn.send(data[:BUFFER_SIZE])
            data = data[BUFFER_SIZE:]

    def recv(self):
        #  Receive packet length
        start = time.time()
        length_bytes = self.conn.recv(length_packet_size)

        # If failed, force a reconnect
        if len(length_bytes) < length_packet_size:
            self.reconnect()
            return self.recv()

        # Convert to int
        length = struct.unpack("L", length_bytes)[0]
        data = b""

        # Read packet
        start = time.time()
        while len(data) < length:
            # If we time out, force a reconnect
            if time.time() - start > RECV_TIMEOUT:
                self.reconnect()
                return self.recv()

            data += self.conn.recv(length - len(data))

        return data

    def reconnect(self):
        self.close()
        self.connect()
