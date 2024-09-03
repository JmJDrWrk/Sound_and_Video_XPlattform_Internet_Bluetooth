import socket
import json
import pyautogui

# Dirección y puerto del servidor
SERVER_IP = '0.0.0.0'
SERVER_PORT = 12341

# Crear un socket y enlazarlo a la dirección del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()

print(f"listening on {SERVER_IP}:{SERVER_PORT}")

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(4096)  # Aumentamos el tamaño del buffer para manejar múltiples eventos
            if not data:
                break

            events = json.loads(data.decode('utf-8'))
            
            for event in events:
                # Process mouse events
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

    except Exception as e:
        print(f"Excepción: {e}")
    finally:
        client_socket.close()

# Aceptar conexiones de clientes
while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection acepted from {addr}")
    handle_client(client_socket)
