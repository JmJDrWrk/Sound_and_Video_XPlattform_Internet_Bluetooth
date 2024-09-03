import socket
import numpy as np
from PIL import ImageGrab, Image, ImageOps
import io
import struct
import pyautogui
import configparser
import time

old_print = print
def print(*argv):
    old_print('\t[Video Server]', *argv)

config = configparser.ConfigParser()
config.read('config.ini')
config = config['screen_sharing']

cursorWidth = int(config['cursorWidth'])
cursorHeight = int(config['cursorHeight'])

# Configuration
SERVER_IP = '0.0.0.0'
SERVER_PORT = 12345
PNG_PATH = 'cursor12x17.png'  # Path to the PNG image
pyautogui.FAILSAFE = False

def send_screen_data():
    # Load the PNG image to overlay and convert to RGBA
    overlay_image = Image.open(PNG_PATH).convert("RGBA")
    
    # Resize the cursor image
    cursor_size = (cursorWidth, cursorHeight)  # New cursor size (width, height)
    overlay_image = overlay_image.resize(cursor_size)
    
    # Convert the cursor image to white while preserving transparency
    alpha = overlay_image.split()[-1]
    overlay_image = ImageOps.grayscale(overlay_image)
    overlay_image = ImageOps.colorize(overlay_image, black="white", white="white")
    overlay_image.putalpha(alpha)
    
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
            curr_image = ImageGrab.grab()
            
            # Get the cursor position
            cursor_x, cursor_y = pyautogui.position()
            
            # Convert screen to RGBA to support transparency
            screen_with_cursor = curr_image.convert("RGBA")
            screen_with_cursor.paste(overlay_image, (cursor_x, cursor_y), overlay_image)
            screen_with_cursor = screen_with_cursor.convert("RGB")
            
            # Save the image to a buffer and encode it
            with io.BytesIO() as buffer:
                screen_with_cursor.save(buffer, format='JPEG')
                data = buffer.getvalue()
            
            # Prepare the data size and timestamp
            data_size = len(data)
            timestamp = int(time.time() * 1_000_000)

            # Pack both data size and timestamp into a single byte sequence
            data_size_bytes = struct.pack('!I', data_size)
            timestamp_bytes = struct.pack('!Q', timestamp)
            combined_data = data_size_bytes + timestamp_bytes

            # Send the combined data
            conn.sendall(combined_data)
            
            # Send the data
            conn.sendall(data)

    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        conn.close()
        sock.close()

if __name__ == "__main__":
    while True:
        try:
            send_screen_data()
        except Exception as e:
            print('Error\n', e)
