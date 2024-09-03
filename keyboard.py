#Ref SVPS-v3.1

import socket
import pyautogui 
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
          
            pyautogui.press(key)
        else:
            print("Invalid command format")
    except Exception as e:
            print(f"An error occurred: {e}")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
