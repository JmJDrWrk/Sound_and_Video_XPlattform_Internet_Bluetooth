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
import pickle
from mss import mss
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


MAX_UDP_PACKET_SIZE = 64000#65000  # Maximum UDP packet size

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
        address = (client_ip, SERVER_PORT_UDP)
        MAX_UDP_SIZE = 64000 
        
        def send_in_chunks(data):
            # Envía primero el tamaño del mensaje
            udp_sock.sendto(struct.pack("L", len(data)), address)
            # Divide el mensaje en fragmentos
            for i in range(0, len(data), MAX_UDP_SIZE):
                chunk = data[i:i + MAX_UDP_SIZE]
                udp_sock.sendto(chunk, address)
                # print(len(chunk))
                
        def alternativeCaptureMethod():
             # Capture entire screen
            with mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                # Convert to PIL/Pillow Image
                return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')


        while True:
            ## Old data version
            # screen = ImageGrab.grab()
            # cursor_x, cursor_y = pyautogui.position()
            # screen_with_cursor = screen.convert("RGBA")
            # screen_with_cursor.paste(overlay_image, (cursor_x, cursor_y), overlay_image)
            # img = alternativeCaptureMethod()
            frame = np.array(pyautogui.screenshot())
            # frame = np.array(img)
            _, encoded_frame = cv2.imencode('.jpg', frame)
            # data = encoded_frame.tobytes()
            data = pickle.dumps(encoded_frame)
            
            # Enviar datos en fragmentos
            
            #New Data Version
            # img = pyautogui.screenshot()
            # frame = np.array(img)

            # # Convertir a RGB (OpenCV usa BGR)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # # Codificar el marco como JPEG
            # _, buffer = cv2.imencode('.jpg', frame)
            # data = pickle.dumps(buffer)
            
            send_in_chunks(data)
            # time.sleep(0.001)

    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        udp_sock.close()

if __name__ == "__main__":
    client_ip = handle_client_registration()
    send_screen_data(client_ip)