import cv2
import numpy as np
import socket
import pickle
import struct

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 12345))

def receive_in_chunks(sock, expected_size):
    data = b''
    while len(data) < expected_size:
        packet, _ = sock.recvfrom(65535)
        data += packet
    return data

while True:
    try:
        # Recibir tamaño del marco (debe ser enviado antes en el servidor)
        frame_size_data, _ = sock.recvfrom(8)
        frame_size = struct.unpack("L", frame_size_data)[0]
        
        # Recibir los datos del marco en fragmentos
        frame_data = receive_in_chunks(sock, frame_size)

        # print('\n\n\nFrame Data:', frame_data)
        
        # Decodificar los datos del marco
        frame = pickle.loads(frame_data)
        frame = cv2.imdecode(frame, 1)
        
        # Redimensionar el marco
        if frame is not None:
            height, width = frame.shape[:2]
            # Ajustar el tamaño según tus necesidades
            new_width = 800
            new_height = int((new_width / width) * height)
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Mostrar el marco redimensionado
            cv2.imshow('Screen Stream', resized_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Error->: {e}")

# Liberar recursos
cv2.destroyAllWindows()
sock.close()
