#Ref SVPS-v4.0

import socket
import pyautogui
pyautogui.FAILSAFE = True
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
config = config['keyboard_sharing']

old_print = print
def print(*argv):
    old_print('\t[Keyboard Server]', *argv)
    

KEYBOARDPORT = int(config['keyboardport'])
    

def execute_command(command):
    try:
        if command.startswith("KEYPRESS:"):
            key = command[len("KEYPRESS:"):].strip()  # Extract and strip any extra whitespace
            print(f"Received key: {key}")

            # Handle special keys
            special_keys = {
                "KEY.ENTER": "enter",
                "KEY.SPACE": "space",
                "KEY.TAB": "tab",
                "KEY.BACKSPACE": "backspace",
                "KEY.ESCAPE": "esc",
                "KEY.SHIFT": "shift",
                "KEY.CONTROL": "ctrl",
                "KEY.ALT": "alt",
                "KEY.DELETE": "delete",
                "KEY.UP": "up",
                "KEY.DOWN": "down",
                "KEY.LEFT": "left",
                "KEY.RIGHT": "right",
                "KEY.F1": "f1",
                "KEY.F2": "f2",
                # Add more special keys as needed
            }

            # Convert the key to lowercase and check if it's a special key
            key = key.upper()  # Convert to uppercase for comparison
            if key in special_keys:
                print('Pressing special key')
                pyautogui.press(special_keys[key])
            else:
                pyautogui.press(key.lower())  # Use lowercase for normal keys
        else:
            print("Invalid command format")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow quick reuse of the port
    server_socket.bind(('0.0.0.0', KEYBOARDPORT)) 
    server_socket.listen(1)
    print(f"Server listening on port {KEYBOARDPORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            command = data.decode('utf-8')
            execute_command(command)

        client_socket.close()

if __name__ == "__main__":
    main()
