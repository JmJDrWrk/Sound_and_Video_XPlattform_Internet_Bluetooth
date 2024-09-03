import socket
import numpy as np
from PIL import ImageGrab, Image, ImageOps
import io
import struct
import pyautogui
import configparser
import time
from skimage.metrics import structural_similarity as ssim

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

def get_diff_image(prev_image, curr_image):
    # Convert images to numpy arrays
    prev_np = np.array(prev_image)
    curr_np = np.array(curr_image)
    
    # Ensure the images are in the same size
    if prev_np.shape != curr_np.shape:
        raise ValueError("The images must be of the same size.")
    
    # Set a reasonable window size
    win_size = min(prev_np.shape[:2]) // 8 * 2 + 1  # Ensure win_size is odd and not too large
    win_size = max(win_size, 7)  # Ensure win_size is at least 7

    # Compute the structural similarity index (SSIM)
    ssim_index, diff = ssim(prev_np, curr_np, full=True, channel_axis=-1, win_size=win_size)
    
    # Convert the difference image to uint8
    diff_image = (diff * 255).astype(np.uint8)
    
    return diff_image

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
    
    prev_image = ImageGrab.grab()
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
            
            # Get difference image
            diff_image = get_diff_image(prev_image, curr_image)
            
            # Save the diff image to a buffer and encode it
            with io.BytesIO() as buffer:
                diff_image_pil = Image.fromarray(diff_image)
                diff_image_pil.save(buffer, format='JPEG')
                data = buffer.getvalue()
            
            # Send the size of the data first
            data_size = struct.pack('!I', len(data))
            conn.sendall(data_size)
            
            # Send timestamp
            TIMESTAMP = struct.pack('!Q', int(time.time() * 1_000_000))
            conn.sendall(TIMESTAMP)
            
            # Send the data
            conn.sendall(data)
            
            # Update previous image
            prev_image = curr_image

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
