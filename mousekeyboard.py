import socket
import struct
import logging
import pyautogui

pyautogui.FAILSAFE = False

# Configuration
MOUSE_SERVER_IP = '0.0.0.0'
MOUSE_SERVER_PORT = 2444
last_x, last_y = 0, 0

def setup_logging():
    logging.basicConfig(filename='mouse_positions.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def receive_mouse_positions():
    setup_logging()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((MOUSE_SERVER_IP, MOUSE_SERVER_PORT))
        sock.listen(1)
        print("Mouse server waiting for a connection...")
        conn, addr = sock.accept()
        print("Connected to", addr)

        try:
            global last_x, last_y
            while True:
                # Determine the length of the incoming data
                cursor_data = conn.recv(12)  # Read up to 12 bytes to handle both cases

                if not cursor_data:
                    print("No cursor data received, closing connection...")
                    break

                data_length = len(cursor_data)

                try:
                    if data_length == 8:
                        # Handle mouse position data
                        x, y = struct.unpack('!II', cursor_data)
                        if last_x != x or last_y != y:
                            last_x, last_y = x, y
                            # print(f"Cursor Position - X: {x}, Y: {y}")
                            # logging.info(f"Cursor Position - X: {x}, Y: {y}")
                            pyautogui.moveTo(x, y)
                    elif data_length == 12:
                        # Handle KVM behavior data
                        kvm_behaviour = struct.unpack('!III', cursor_data)
                        # print("KVM Behaviour:", kvm_behaviour)

                        # Handle mouse click
                        if kvm_behaviour[1] == 1:  # Assuming 1 represents a mouse event
                            if kvm_behaviour[2] == 1:
                                pyautogui.click(button='left')
                                # print('Left Click')
                            elif kvm_behaviour[2] == 3:
                                pyautogui.click(button='right')
                                # print('Right Click')

                                
                        # Handle keyboard events (if needed)
                        elif kvm_behaviour[1] == 2:  # Assuming 2 represents a keyboard event
                            # print(f"Keyboard Event: {kvm_behaviour[2]}")
                            try:
                               pyautogui.press(chr(kvm_behaviour[2]))
                            except Exception as pressException:#AddSupport for special keys like arrows 
                               print('Press Error', pressException)

                    else:
                        print(f"Unexpected data length: {data_length}")

                except struct.error as e:
                    print('Cannot unpack:', e)

        finally:
            conn.close()

if __name__ == "__main__":
    while True:
        try:
            receive_mouse_positions()
        except Exception as e:
            print('Error\n', e)

#https://pyautogui.readthedocs.io/en/latest/keyboard.html