import cv2
import numpy as np
import socket
import struct

def extract_rtp_payload(rtp_packet):
    header = rtp_packet[:12]  # RTP header is 12 bytes
    payload = rtp_packet[12:]
    return payload

def receive_screen(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))

    expected_seq_number = 0
    buffer = b''

    while True:
        data, _ = sock.recvfrom(65507)
        if not data:
            continue

        rtp_header = data[:12]
        payload = extract_rtp_payload(data)
        seq_number = struct.unpack('!H', rtp_header[2:4])[0]

        if seq_number == expected_seq_number:
            buffer += payload
            expected_seq_number += 1
        else:
            print(f"Packet loss detected. Expected {expected_seq_number}, got {seq_number}")
            expected_seq_number = seq_number + 1  # Resync on next packet

        try:
            np_arr = np.frombuffer(buffer, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imshow('Received Screen', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Error decoding frame: {e}")

        buffer = b''

    sock.close()
    cv2.destroyAllWindows()

# Example usage
receive_screen(12345)
