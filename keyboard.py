#Ref SVPS-v3.1
#Release Notes:
# -Finally using tcp version with optimization
# -Improve high fps up to 28 at least on this equipment
# -Improve latency down between 1.8s and 800ms
# -Added client-server features like delay and frames per second
# -Deprecated usage of mousekeyboard.py and its configurations in client and in server side
# -- 3.1
# -- Added keyboard server script and support directly to this file in server side
# -- Added keyboard client script into clien part manually managed
# -- Both keyboard side scripts supports and requires new versions of config.ini and rutine.ini


from pynput import keyboard
import socket

import configparser

config = configparser.ConfigParser()
config.read('config.ini')
config = config['keyboard_sharing']

KEYBOARDPORT = int(config['keyboardport'])
KEYBOARDIP = config['keyboardip']


# Global variables to track modifier keys
ctrl_pressed = False
shift_pressed = False

def on_press(key):
    global ctrl_pressed, shift_pressed
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressed = True
    elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        shift_pressed = True
    elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        send_command("KEYPRESS:ALT")
    else:
        key_name = getattr(key, 'char', str(key)).upper()
        if ctrl_pressed and key_name:
            send_command(f"KEYPRESS:CTRL+{key_name}")
        elif shift_pressed and key_name:
            send_command(f"KEYPRESS:SHIFT+{key_name}")
        else:
            send_command(f"KEYPRESS:{key_name}")

def on_release(key):
    global ctrl_pressed, shift_pressed
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressed = False
    elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        shift_pressed = False

def send_command(command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((KEYBOARDIP, KEYBOARDPORT))
    print(f'Connection stablished {KEYBOARDIP}:{KEYBOARDPORT}')
    client_socket.send(command.encode('utf-8'))
    client_socket.close()

def main():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
