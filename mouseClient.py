#Ref SVPS-v4.0

import socket
import json
import time
from pynput import mouse

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
config = config['mouse_sharing']

# Dirección del servidor
SERVER_IP = config['mouseip']
SERVER_PORT = int(config['mouseport'])
usePygameMouse = bool(config['usepygamemouseposition'])
PYGAME_IP = '127.0.0.1'
PYGAME_PORT = int(config['pygamemousepositionport'])

print('\n WARNING!! usePygameMouse value is ignored this version requires it to be true\n\n')

pygame_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pygame_socket.bind(('0.0.0.0', PYGAME_PORT))


# Crear una conexión de socket al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))


move_buffer = []
event_buffer = []
BUFFER_INTERVAL = 0.1  # Intervalo de tiempo para enviar eventos en segundos

def send_buffered_events():
    
    data, _ = pygame_socket.recvfrom(16)
    lastX, lastY, remain = data.decode().split(';')
    print('eventBuffer', event_buffer)
    # event_buffer.append(move_buffer[-1])
    event_buffer.append({'type': 'move', 'x': int(lastX), 'y': int(lastY)})
    # event_buffer.clear()
    if event_buffer or move_buffer:
        #This entire block requires optimization
        # on_move()
        # print(f'There was {len(move_buffer)} acumulated movements')
        # print('move buffer', move_buffer[0])
        # fromx, ffromy = (move_buffer[0]['x'], move_buffer[0]['y'])
        # tox, toy = (move_buffer[-1]['x'], move_buffer[-1]['y'])
        # print(f'{fromx},{ffromy}  moving to {tox},{toy}')
        # if(move_buffer):
        # print('Obteniendo posicion real del raton')

            # print('data', {'type': 'move', 'x': lastX, 'y': lastY})
        move_buffer.clear()
        client_socket.sendall(json.dumps(event_buffer).encode('utf-8'))
        # print('Sending', event_buffer)
        event_buffer.clear()

# lastX, lastY = 0, 0   
# tooTinyTrigger

def on_move(x, y):
    # if(x == lastX and y == lastY):
    #     print('This mouse position is too tiny')
    
    event = {'type': 'move', 'x': x, 'y': y}
    move_buffer.append(event)

def on_click(x, y, button, pressed):
    event = {
        'type': 'click',
        'x': x,
        'y': y,
        'button': str(button),
        'pressed': pressed
    }
    event_buffer.append(event)

def on_scroll(x, y, dx, dy):
    print('scrolling')
    event = {
        'type': 'scroll',
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy
    }
    event_buffer.append(event)

# Configurar el listener de ratón
with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
# with mouse.Listener( on_click=on_click, on_scroll=on_scroll) as listener:
    try:
        while True:
            try:
                time.sleep(BUFFER_INTERVAL)
                # print('Sending events...')
                send_buffered_events()
            except Exception as exce:
                print('Exception inside mouse loop', exce)
                pass
    except KeyboardInterrupt:
        print("Ending mouse client...")
    finally:
        client_socket.close()
