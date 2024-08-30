import socket
import numpy as np
from PIL import ImageGrab, Image, ImageOps
import io
import struct
import pyautogui
import configparser
import cv2 
import numpy
import time
config = configparser.ConfigParser()
config.read('config.ini')
config = config['screen_sharing']

cursorWidth = int(config['cursorWidth'])
cursorHeight = int(config['cursorHeight'])

# Configuration
SERVER_IP = '0.0.0.0'
SERVER_PORT_TCP = 2555
SERVER_PORT_UDP = 3555
VIDEO_SERVER_CLOCK_PORT = 3556
PNG_PATH = 'cursor12x17.png'  # Path to the PNG image
pyautogui.FAILSAFE = False


MAX_UDP_PACKET_SIZE = 65507#65000  # Maximum UDP packet size

def handle_client_registration():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((SERVER_IP, SERVER_PORT_TCP))
    tcp_sock.listen(1)
    
    print("TCP server listening on port", SERVER_PORT_TCP)
    
    conn, addr = tcp_sock.accept()
    print("Client connected:", addr)
    
    conn.sendall(b"Registration successful")
    
    client_ip = addr[0]
    conn.close()
    tcp_sock.close()
    return client_ip

def send_screen_data(client_ip):
    overlay_image = Image.open(PNG_PATH).convert("RGBA")
    cursor_size = (cursorWidth, cursorHeight)
    overlay_image = overlay_image.resize(cursor_size)
    alpha = overlay_image.split()[-1]
    overlay_image = ImageOps.grayscale(overlay_image)
    overlay_image = ImageOps.colorize(overlay_image, black="white", white="white")
    overlay_image.putalpha(alpha)
    
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clock_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        while True:
            screen = ImageGrab.grab()
            cursor_x, cursor_y = pyautogui.position()
            screen_with_cursor = screen.convert("RGBA")
            screen_with_cursor.paste(overlay_image, (cursor_x, cursor_y), overlay_image)
            
            #This works exactly as bad
            # screenshot = pyautogui.screenshot()
            # frame = np.array(screenshot)
            
            
            # with io.BytesIO() as buffer:
            #     screen_with_cursor.save(buffer, format='PNG')
            #     data = buffer.getvalue()
            
            # Convert frame
            frame = np.array(screen_with_cursor)
            _, encoded_frame = cv2.imencode('.jpg', frame)
            data = encoded_frame.tobytes()
            
            counter = 0
            # Send data in chunks
            for i in range(0, len(data), MAX_UDP_PACKET_SIZE):
                # print('i', i)
                counter += 1
                chunk = data[i:i + MAX_UDP_PACKET_SIZE]
                udp_sock.sendto(chunk, (client_ip, SERVER_PORT_UDP))
                if(i+MAX_UDP_PACKET_SIZE>len(data)):
                    clock_sock.sendto(f'next sended:{counter}'.encode(), (client_ip, VIDEO_SERVER_CLOCK_PORT))
                else:
                    clock_sock.sendto('wait'.encode(), (client_ip, VIDEO_SERVER_CLOCK_PORT))
            # Send delimiter to mark end of the image data
            # udp_sock.sendto('k'.encode(), (client_ip, SERVER_PORT_UDP))
            # clock_sock.sendto('next'.encode(), (client_ip, VIDEO_SERVER_CLOCK_PORT))
            # print('Sending frame cut signal')
            # time.sleep(1)
            # udp_sock.sendto(b'END_OF_IMAGE', (client_ip, SERVER_PORT_UDP))
            # print('FRAMED')
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        udp_sock.close()

if __name__ == "__main__":
    client_ip = handle_client_registration()
    send_screen_data(client_ip)