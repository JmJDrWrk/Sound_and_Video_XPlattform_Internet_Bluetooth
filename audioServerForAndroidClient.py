import socket
import pyaudio
import configparser
import threading

p = pyaudio.PyAudio()

SERVER_IP = '0.0.0.0'
SERVER_REGISTRATION_PORT = 54424
CLIENT_PORT = 5005
FORMAT = pyaudio.paInt16


def handle_client_registration(reg_server_socket):
#    #Handles client registration and configuration file reception.
    print('\twaiting client registration')
    client_socket, client_address = reg_server_socket.accept()
    client_ip, client_port = client_address
    print(f"\tconnection from {client_ip}:{client_port}")
    
    # Send available audio devices to the client
    # message = "[Devices]\n{next}"
    # # for i in range(p.get_device_count()):
    # #     info = p.get_device_info_by_index(i)
    # #     message += f"Device {i}: {info['name']} : {info['maxInputChannels']}\n"
    # client_socket.sendall(message.encode())
    
    # client_socket.sendall(open('audio_streaming.log','rb').read()) Optional untested
    # configString = client_socket.recv(1024)
    print('This is the config string')
    # Receive the config file from the client
    TERMINATOR = b'\x00\x00\x00\x00'
    with open('config.ini', 'wb') as file:
        print("\treceiving configuration file...")
        while True:
            data = client_socket.recv(1024)
            # print('data', data)
            # if TERMINATOR in data:
            #     print('FOUND TERMINATOR EI VOLVER')
            #     # break
            if not data:
                break
            file.write((str((data.decode())).replace('{keyenter}','\n').replace('\x00\x00\x00\x00','')).encode())
        print("\tconfiguration file received successfully.")
    # with open('config.ini', 'w')
    # # client_socket.sendall('ALpha'.encode())

    # print('\thandshake: OK')
    # client_socket.sendall('listo'.encode())
    return client_ip


def load_config(filename='config.ini'):
#    #Loads audio configuration from the specified file.
    config = configparser.ConfigParser()
    config.read(filename)
    audio_config = config['audio_sharing']
    return {
        'audioServerIp': audio_config.get('audioServerIp'),
        'audioServerPort': int(audio_config.get('audioServerPort')),
        'channels': int(audio_config.get('channels')),
        'rate': int(audio_config.get('rate')),
        'chunk': int(audio_config.get('chunk')),
        'deviceIndex': int(audio_config.get('deviceIndex'))
    }

def start_audio_streaming():
    # print('\t handshake')

#    #Starts the audio streaming process.
    # Set up registration server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reg_server_socket:
        reg_server_socket.bind((SERVER_IP, SERVER_REGISTRATION_PORT))
        reg_server_socket.listen(1)
        client_ip = handle_client_registration(reg_server_socket)

    print('\tstarting Audio Stream')

    # Load audio settings from the config file
    config = load_config()
    
    # Set up the audio stream
    stream = p.open(
        format=FORMAT,
        channels=config['channels'],
        rate=config['rate'],
        input=True,
        input_device_index=config['deviceIndex'],
        frames_per_buffer=config['chunk']
    )
    # print("\a") Attempt to make a beep
    # Set up UDP socket for streaming

    CHUNK = config['chunk']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print(f"\tstreaming system audio to {client_ip}:{CLIENT_PORT}...")
        try:
            while True:
                data = stream.read(CHUNK)
                sock.sendto(data, (client_ip, CLIENT_PORT))
        except KeyboardInterrupt:
            print("\tstreaming stopped.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

start_audio_streaming()

