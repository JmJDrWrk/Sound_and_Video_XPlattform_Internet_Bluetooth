import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.1', 12345))  # Use the IP address assigned to Computer 1 and an available port
server_socket.listen(1)
print("Server is listening...")

conn, addr = server_socket.accept()
print(f"Connection established with {addr}")