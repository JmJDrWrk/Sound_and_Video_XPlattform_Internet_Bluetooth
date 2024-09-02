import cv2
import numpy as np
import socket
import pyautogui
import pickle
import struct

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)

# Parámetros de captura de pantalla
screen_size = (1920, 1080)  # Ajusta según tu resolución de pantalla
MAX_UDP_SIZE = 64000  # Tamaño máximo de datagrama UDP

def send_in_chunks(data, address):
    # Envía primero el tamaño del mensaje
    sock.sendto(struct.pack("L", len(data)), address)
    # Divide el mensaje en fragmentos
    for i in range(0, len(data), MAX_UDP_SIZE):
        chunk = data[i:i + MAX_UDP_SIZE]
        sock.sendto(chunk, address)

while True:
    # Captura de pantalla
    img = pyautogui.screenshot()
    frame = np.array(img)

    # Convertir a RGB (OpenCV usa BGR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Codificar el marco como JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    data = pickle.dumps(buffer)
    
    # Enviar datos en fragmentos
    send_in_chunks(data, server_address)
