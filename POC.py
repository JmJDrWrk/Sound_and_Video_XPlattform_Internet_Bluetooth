import cv2
import numpy as np
import socket
import pyautogui
import time
def send_screen(server_ip, server_port):
    # Define the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Define chunk size
    chunk_size = 65507  # Max size for UDP payload is 65,535 bytes, leaving some space for headers
    
    while True:
        # Same half screen behaviour
        #screen = ImageGrab.grab()
        #frame = np.array(screen)
        
        # Capture the screen
        screenshot = pyautogui.screenshot()
        
        
        frame = np.array(screenshot)
        
        # Convert to JPEG
        _, encoded_frame = cv2.imencode('.jpg', frame)
        data = encoded_frame.tobytes()
        counter = 0
        # Fragment and send data
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            if(len(chunk)<65507):
                print(len(chunk))
            # sock.sendto(chunk, (server_ip, server_port))
            sock.sendto(f'A{counter}'.encode(), (server_ip, server_port))
            counter += 1
        print('Frame?', counter)
        sock.sendto(f'{counter-1}'.encode(), (server_ip, server_port))
        # Optional: add a delay to control frame rate
        # cv2.waitKey(1)
        # time.sleep(1)
    # Close the socket
    sock.close()

# Example usage
send_screen('127.0.0.1', 12345)
