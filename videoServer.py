import socket
import numpy as np
from PIL import ImageGrab, Image
import io
import struct
import pyautogui

# Configuration
SERVER_IP = '0.0.0.0'
SERVER_PORT = 12345
PNG_PATH = 'cursor12x17.png'  # Path to the PNG image
pyautogui.FAILSAFE = False
def send_screen_data():
    # Load the PNG image to overlay
    overlay_image = Image.open(PNG_PATH)
    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(1)

    print("Waiting for a connection...")
    conn, addr = sock.accept()
    print("Connected to", addr)

    try:
        while True:
            # Capture the screen
            screen = ImageGrab.grab()
            
            # Get the cursor position
            cursor_x, cursor_y = pyautogui.position()
            
            # Create an ImageDraw object to overlay the cursor image
            screen_with_cursor = screen.copy()
            screen_with_cursor.paste(overlay_image, (cursor_x, cursor_y), overlay_image)
            
            # Save the image to a buffer
            with io.BytesIO() as buffer:
                screen_with_cursor.save(buffer, format='PNG')
                data = buffer.getvalue()
            
            # Send the size of the data first
            data_size = struct.pack('!I', len(data))
            conn.sendall(data_size)
            
            # Send the data
            conn.sendall(data)
    finally:
        conn.close()
        sock.close()

if __name__ == "__main__":
    while True:
        try:
            send_screen_data()
        except Exception as e:
            print('Error\n', e)
            # a = input('Continue?')
            # if a.lower() == 'no':
            #     exit()

