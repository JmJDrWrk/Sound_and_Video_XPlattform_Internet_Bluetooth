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
    old_print('\t[Video Server]',*argv)
    

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
    # Separate the alpha channel
    alpha = overlay_image.split()[-1]
    # Convert to grayscale to prepare for coloring
    overlay_image = ImageOps.grayscale(overlay_image)
    # Convert to white
    overlay_image = ImageOps.colorize(overlay_image, black="white", white="white")
    # Put the alpha channel back
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
            screen = ImageGrab.grab()

            # Get the cursor position
            cursor_x, cursor_y = pyautogui.position()

            # Convert screen to RGBA to support transparency
            screen_with_cursor = screen.convert("RGBA")

            # Paste the overlay image with its alpha channel as the mask
            # overlay_image should be loaded earlier in your actual code
            screen_with_cursor.paste(overlay_image, (cursor_x, cursor_y), overlay_image)
            screen_with_cursor = screen_with_cursor.convert("RGB")
            # Save the image to a buffer and encode it
            with io.BytesIO() as buffer:
                screen_with_cursor.save(buffer, format='JPEG')  # Use JPEG for lower latency
                data = buffer.getvalue()

            # Send the size of the data first
            data_size = struct.pack('!I', len(data))
            conn.sendall(data_size)

            # Send timestamp
            TIMESTAMP = struct.pack('!Q', int(time.time() * 1_000_000))
            conn.sendall(TIMESTAMP)

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
