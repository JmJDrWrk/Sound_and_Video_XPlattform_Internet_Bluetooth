#Ref SVPS-v3
#Release Notes:
# -Finally using tcp version with optimization
# -Improve high fps up to 28 at least on this equipment
# -Improve latency down between 1.8s and 800ms
# -Added client-server features like delay and frames per second
# -Removed utility to remote control mouse and keyboard but keeping mouse png pasting feedback to see mouse from client
# -Deprecated usage of mousekeyboard.py and its configurations in client and in server side


import pygame
import socket
import struct
import io
from PIL import Image
import configparser
import time

config = configparser.ConfigParser()
config.read('config.ini')

config = config['screen_sharing']

print('Calling', config['videoServerIp'])

VIDEO_SERVER_IP = config['videoServerIp']
VIDEO_SERVER_PORT = int(config['videoServerPort'])

image_width, image_height = int(config['default_target_screen_width']), int(config['default_target_screen_height'])
screen_width, screen_height = int(config['default_window_width']), int(config['default_window_height'])

def receive_and_display():
    global image_width, image_height, screen_width, screen_height
    
    pygame.init()
    global screen
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption('Client Screen')

    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
    video_sock.connect((VIDEO_SERVER_IP, VIDEO_SERVER_PORT))

    clock = pygame.time.Clock()
    frame_count = 0
    start_time = time.time()

    try:
        while True:
            frame_start_time = time.time()

            received_data = video_sock.recv(12)  # 4 bytes for size + 8 bytes for timestamp
            if len(received_data) == 12:
                data_size = struct.unpack('!I', received_data[:4])[0]
                server_timestamp = struct.unpack('!Q', received_data[4:])[0]

                current_time = int(time.time() * 1_000_000)
                elapsed_time = current_time - server_timestamp
                if elapsed_time != 0 and elapsed_time < 2000:
                    print('ELAPSED_TIME', elapsed_time)
            else:
                print("Error: received data length is not correct.")

            # Receive the image data
            data = b''
            while len(data) < data_size:
                packet = video_sock.recv(data_size - len(data))
                if not packet:
                    print("Incomplete image data received, closing connection...")
                    break
                data += packet

            if data:
                try:
                    # Load image from bytes
                    image = Image.open(io.BytesIO(data))

                    # Check and print image mode for debugging
                    # print(f"Image mode: {image.mode}, Size: {image.size}")

                    # Convert image to pygame format
                    if image.mode == 'RGB':
                        mode = 'RGB'
                    elif image.mode == 'RGBA':
                        mode = 'RGBA'
                    else:
                        print(f"Unsupported image mode: {image.mode}")
                        continue
                    
                    image = pygame.image.fromstring(image.tobytes(), image.size, mode)

                    # Resize image to fit screen
                    window_size = screen.get_size()
                    screen_width, screen_height = window_size
                    resized_image = pygame.transform.scale(image, (screen_width, screen_height))

                    # Display the image
                    screen.blit(resized_image, (0, 0))
                    pygame.display.flip()
                except Exception as e:
                    print(f"Error loading image: {e}")
            # Process Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps = frame_count / elapsed_time
                print(f"FPS: {fps:.2f}")
                frame_count = 0
                start_time = time.time()

            clock.tick(60)  # Adjusted to 30 FPS

    except Exception as e:
        print('Error', e)
    finally:
        pygame.quit()
        video_sock.close()

if __name__ == "__main__":
    receive_and_display()
