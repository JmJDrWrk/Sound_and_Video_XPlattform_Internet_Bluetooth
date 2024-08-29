import pygame
import socket
import struct
import io
from PIL import Image
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

config = config['screen_sharing']

print('Calling', config['videoServerIp'] )

# Configuration
VIDEO_SERVER_IP = config['videoServerIp']  # Change this to your video server IP
VIDEO_SERVER_PORT = int(config['videoServerPort'])
MOUSE_SERVER_IP = config['peripheralServerIp']  # Change this to your mouse server IP
MOUSE_SERVER_PORT = int(config['peripheralServerPort'])

# Modifier keys state
modifier_state = {
    'ctrl': False,
    'alt': False,
    'shift': False
}

last_x, last_y = 0, 0

# Initialize these to avoid NameErrors
image_width, image_height = int(config['default_target_screen_width']), int(config['default_target_screen_height'])
screen_width, screen_height = int(config['default_window_width']), int(config['default_window_height'])

def send_cursor_position(sock):
    global last_x, last_y
    x, y = pygame.mouse.get_pos()
    
    # Calculate scaling factors based on the current image dimensions
    scale_x = image_width / screen_width
    scale_y = image_height / screen_height
    
    # Adjust mouse position based on scaling
    adjusted_x = int(x * scale_x)
    adjusted_y = int(y * scale_y)
    
    if (adjusted_x != last_x or adjusted_y != last_y):
        last_x, last_y = adjusted_x, adjusted_y
        data = struct.pack('!II', adjusted_x, adjusted_y)
        sock.sendall(data)

def send_click_signal(sock, button):
    data = struct.pack('!III', 0, 1, button)
    sock.sendall(data)

def send_key_signal(sock, key, is_down):
    # Determine the modifier state
    mod_state = 0
    if modifier_state['ctrl']:
        mod_state |= pygame.KMOD_CTRL
    if modifier_state['alt']:
        mod_state |= pygame.KMOD_ALT
    if modifier_state['shift']:
        mod_state |= pygame.KMOD_SHIFT
    
    # Send key signal with modifier state
    data = struct.pack('!IIII', 0, 2, key, mod_state if is_down else 0)  # 2 indicates keyboard event
    sock.sendall(data)

def handle_key_event(event, sock):
    global modifier_state
    if event.key in [pygame.K_LCTRL, pygame.K_RCTRL]:
        modifier_state['ctrl'] = (event.type == pygame.KEYDOWN)
    elif event.key in [pygame.K_LALT, pygame.K_RALT]:
        modifier_state['alt'] = (event.type == pygame.KEYDOWN)
    elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
        modifier_state['shift'] = (event.type == pygame.KEYDOWN)
    
    # Send the key event to the server
    send_key_signal(sock, event.key, event.type == pygame.KEYDOWN)

def receive_and_display():
    global image_width, image_height, screen_width, screen_height
    
    pygame.init()
    global screen
    screen = pygame.display.set_mode(( int(config['default_window_width']), int(config['default_window_height'])), pygame.RESIZABLE)
    pygame.display.set_caption('Client Screen')

    # Connect to video server
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.connect((VIDEO_SERVER_IP, VIDEO_SERVER_PORT))
    
    # Connect to mouse/keyboard server
    input_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    input_sock.connect((MOUSE_SERVER_IP, MOUSE_SERVER_PORT))
    
    print(f"Connected to video server {VIDEO_SERVER_IP}:{VIDEO_SERVER_PORT}")
    print(f"Connected to input server {MOUSE_SERVER_IP}:{MOUSE_SERVER_PORT}")

    try:
        while True:
            # Receive the size of the image data
            data_size = video_sock.recv(4)
            if not data_size:
                print("No data size received, closing connection...")
                break
            
            data_size = struct.unpack('!I', data_size)[0]
            
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
                    # Load image from bytes and display
                    image = Image.open(io.BytesIO(data))
                    image_width, image_height = image.size
                    image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

                    # Additional image processing steps
                    window_size = screen.get_size()
                    screen_width, screen_height = window_size
                    # Resize the image to fit the screen
                    resized_image = pygame.transform.scale(image, (screen_width, screen_height))

                    screen.blit(resized_image, (0, 0))
                    pygame.display.flip()
                except Exception as e:
                    print(f"Error loading image: {e}")

            # Send cursor position
            send_cursor_position(input_sock)

            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        send_click_signal(input_sock, 1)
                    elif event.button == 3:  # Right click
                        send_click_signal(input_sock, 3)
                elif event.type == pygame.KEYDOWN:
                    # Handle key down and key up events
                    handle_key_event(event, input_sock)

    except Exception as e:
        print('Error', e)
    finally:
        pygame.quit()
        video_sock.close()
        input_sock.close()

if __name__ == "__main__":
    receive_and_display()
