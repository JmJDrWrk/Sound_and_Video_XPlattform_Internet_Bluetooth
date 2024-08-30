import cv2
import numpy as np
import socket
import pyautogui
import time
import struct

def create_rtp_packet(seq_number, timestamp, payload):
    version = 2
    padding = 0
    extension = 0
    csrc_count = 0
    marker = 0
    pt = 96  # Payload Type, 96 is dynamic for video
    ssrc = 12345  # A random SSRC

    rtp_header = struct.pack('!BBHII', 
        (version << 6) | (padding << 5) | (extension << 4) | csrc_count,
        (marker << 7) | pt,
        seq_number,
        timestamp,
        ssrc
    )

    return rtp_header + payload

def send_screen(server_ip, server_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chunk_size = 1400  # Smaller than typical MTU to avoid fragmentation

    seq_number = 0
    timestamp = 0
    fps = 30  # Set desired frames per second

    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        _, encoded_frame = cv2.imencode('.jpg', frame)
        data = encoded_frame.tobytes()

        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            rtp_packet = create_rtp_packet(seq_number, timestamp, chunk)
            sock.sendto(rtp_packet, (server_ip, server_port))
            seq_number += 1
        
        timestamp += int(90000 / fps)  # RTP timestamp increments
        time.sleep(1 / fps)

    sock.close()

# Example usage
send_screen('127.0.0.1', 12345)
