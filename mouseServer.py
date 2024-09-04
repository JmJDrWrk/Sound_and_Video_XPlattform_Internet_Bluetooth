#Ref SVPS-v4.0
#Release Notes:
# - Added support for mouse
# - Added support for keyboard
# - Mouse sends relative position
# - Unoptimized mouse sendings and extra callings inside mouseClient and clientVideo
# - New port in use localhost between mouseClient and clientVideo
# - ClientVideo and mouseClient requires to run together at least in this version
# - keyboard support some specific keys like delete and enter but not combinations and holdings

import socket
import json
import pyautogui
pyautogui.FAILSAFE = True
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
config = config['mouse_sharing']


# Dirección y puerto del servidor
SERVER_IP = '0.0.0.0'
SERVER_PORT = int(config['mouseport'])

# Crear un socket y enlazarlo a la dirección del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow quick reuse of the port
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(2)

print(f"listening on {SERVER_IP}:{SERVER_PORT}")

def handle_client(client_socket):
    try:
        while True:
            try:
                data = client_socket.recv(4096)  # Aumentamos el tamaño del buffer para manejar múltiples eventos
                if not data:
                    break

                events = json.loads(data.decode('utf-8'))
                
                for event in events:
                    # Process mouse events
                    print(event)
                    if event['type'] == 'move':
                        pyautogui.moveTo(event['x'], event['y'])
                        # print(f"pyautogui.moveTo(event['x'], event['y'])")
                    elif event['type'] == 'click':
                        button = pyautogui.LEFT if event['button'] == 'Button.left' else pyautogui.RIGHT
                        if event['pressed']:
                            pyautogui.mouseDown(button=button)
                            # print(f"pyautogui.mouseDown(button=button)")
                        else:
                            pyautogui.mouseUp(button=button)
                            # print(f"pyautogui.mouseUp(button=button)")
                    elif event['type'] == 'scroll':
                        pyautogui.scroll(event['dy'])
                        # print(f"pyautogui.scroll(event['dy'])")
            except socket.error as exec:
                print('Mouse Loop Exception', exec)
                if exec.errno in [10038, 10054]:  # WinError 10038 or 10054
                    print('Socket error detected, closing socket')
                    break
            except Exception as general_error:
                print('General Exception:', general_error)
                # break

    except Exception as e:
        print(f"Excepción: {e}")
    finally:
        print('Avoided close of the socket')
        exit()
    

# Aceptar conexiones de clientes
while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection acepted from {addr}")
    handle_client(client_socket)
