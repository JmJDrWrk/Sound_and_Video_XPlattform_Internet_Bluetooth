import pygame
import socket
import struct
import io
from PIL import Image
import configparser
import numpy as np
import cv2
import time
config = configparser.ConfigParser()
config.read('config.ini')

config = config['screen_sharing']

print('Calling', config['videoServerIp'])

# Configuration
VIDEO_SERVER_IP = config['videoServerIp']  # Change this to your video server IP
VIDEO_SERVER_PORT_TCP = int(config['videoServerPortTCP'])  # TCP port for registration
VIDEO_SERVER_PORT_UDP = int(config['videoServerPortUDP'])  # UDP port for video streaming
MOUSE_SERVER_IP = config['peripheralServerIp']  # Change this to your mouse server IP
MOUSE_SERVER_PORT = int(config['peripheralServerPort'])
VIDEO_SERVER_CLOCK_PORT = 3556

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

    # Connect to video server for registration
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((VIDEO_SERVER_IP, VIDEO_SERVER_PORT_TCP))

    # Register with the server
    tcp_sock.recv(1024)  # Assuming registration is done, and server sends a confirmation
    print(f"Connected to video server {VIDEO_SERVER_IP}:{VIDEO_SERVER_PORT_TCP}")

    # Connect to video server for receiving video data over UDP
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', VIDEO_SERVER_PORT_UDP))
    
    clock_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clock_sock.bind(('0.0.0.0', VIDEO_SERVER_CLOCK_PORT))
    
    # Connect to mouse/keyboard server
    input_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # input_sock.connect((MOUSE_SERVER_IP, MOUSE_SERVER_PORT))

    print(f"Connected to input server {MOUSE_SERVER_IP}:{MOUSE_SERVER_PORT}")

    try:
        data_buffer = b''
        image_received = False
        counter = 0
        while True:
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         pygame.quit()
            #         exit()
            
            packet, _ = udp_sock.recvfrom(65507)
            # print('Waiting clock')
            clock,_ = clock_sock.recvfrom(16)
            trigger = clock.decode()
            
            if not packet:
                break
            
            if('next ' in trigger):
                packet, _ = udp_sock.recvfrom(65507)
                data_buffer += packet
                counter += 1
                sended = (int(trigger.split(':')[1]))
                # if(sended!=counter):
                print(f'Sended: {sended} Received: {counter}')
                np_array = np.frombuffer(data_buffer, np.uint8)
                frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    image_height, image_width, n= frame.shape
                    # Convert the frame from BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert the frame to a Pygame surface
                    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
                    
                    # Resize the image to fit the screen
                    screen_width, screen_height = screen.get_size()
                    resized_image = pygame.transform.scale(frame_surface, (screen_width, screen_height))
                    
                    # Display the image
                    screen.blit(resized_image, (0, 0))
                    pygame.display.flip()
                counter = 0
                data_buffer = b''
            else:
                counter += 1
                data_buffer += packet
            

            #         if image_received:
            # try:
            #     # Try to open the image with the received data
            #     image = Image.open(io.BytesIO(data_buffer))
            #     image_width, image_height = image.size
            #     image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

            #     # Resize image to fit screen
            #     screen_width, screen_height = screen.get_size()
            #     resized_image = pygame.transform.scale(image, (screen_width, screen_height))

            #     # Display the image
            #     screen.blit(resized_image, (0, 0))
            #     pygame.display.flip()
                
            #     # Clear buffer after processing the image
            #     data_buffer = b''
            #     image_received = False
                
            # except Exception as e:
                # print(f"Error loading image: {e}")
                # except Exception as e:
                #     print(f"Error loading image: {e}")




            # send_cursor_position(input_sock)

            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         return
            #     elif event.type == pygame.MOUSEBUTTONDOWN:
            #         if event.button == 1:
            #             send_click_signal(input_sock, 1)
            #         elif event.button == 3:
            #             send_click_signal(input_sock, 3)
            #     elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            #         handle_key_event(event, input_sock)

    except Exception as e:
        print('Error!', e)
    finally:
        pygame.quit()
        tcp_sock.close()  # Close TCP socket for registration
        udp_sock.close()  # Close UDP socket for video data
        input_sock.close()

if __name__ == "__main__":
    receive_and_display()
