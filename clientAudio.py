import socket
import pyaudio
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
configRoot = config
config = config['audio_sharing']

# Parameters
SERVER_PORT = int(config['audioServerPort'])  # The port number that the client will listen to (must match the server's CLIENT_PORT)
SERVER_IP = config['audioServerIp']
SERVER_REGISTRATION_PORT = 54424
CONTROL_PORT = 9548
# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
deviceAutoTarget = config['deviceAutoTarget']

# Restart Signal
# Restart Signal
commandSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

command = "restart audio_server"  # Make sure to specify which server to restart
commandSocket.sendto(command.encode(), (SERVER_IP, CONTROL_PORT))

# restarted = commandSocket.recv(1024)#Wait server to wake up again
# print('What',restarted.decode())
#Registration process

# Create a socket object
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.settimeout(3)
        
    try:
        # Connect to the server
        client_socket.connect((SERVER_IP, SERVER_REGISTRATION_PORT))
        
        # Receive a message from the server
        message = client_socket.recv(1024)  # Buffer size is 1024 bytes
        # print(f"Received message from server: {message.decode()}")
        
        # message = client_socket.recv(1024)  # Buffer size is 1024 bytes
        # print(f'Received logs from audioServer')
        # print(message)

        devices = str(message.decode())
        print(devices)
        if(deviceAutoTarget!='None'):
            # print('looking for', deviceAutoTarget)
            for device in devices.split('\n'):
                try:
                    deviceIndexName, deviceName = str(device).split(':')
                    # print(deviceIndexName, deviceName, deviceAutoTarget, str(deviceAutoTarget)in(str(deviceName)))
                    if(deviceName == deviceAutoTarget or deviceAutoTarget in deviceName):
                        print('WARNING!!!','Found Targeted Device',deviceIndexName, deviceName)
                        config['deviceIndex'] = str(int(deviceIndexName.replace('Device ','')))
                        with open('config.ini', 'w') as configfile:
                            configRoot.write(configfile)
                        break
                except Exception as excp2:
                    print('excp2','at',device, excp2)
                    continue
        
        file = open('config.ini','rb')
        
        # Send intended configuration
        client_socket.sendfile(file)
        
        file.tell()
        
        client_socket.recv(1024)
        

    except ConnectionError as e:
        print(f"Connection error at registration step: {e}")

    finally:
        # Close the client socket
        client_socket.close()
except:
    print('Probably you logged then shutdown the client and now restart it, the udp is running in remote machine, so registration is not allowed, we will try to connect you directly to stream!')
finally:
    print('Reconnecting...')



# Set up PyAudio
p = pyaudio.PyAudio()

# Open stream for playback
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

# Set up socket for receiving audio data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', SERVER_PORT))

print("Receiving system audio...")

try:
    while True:
        data, _ = sock.recvfrom(CHUNK * 2 * CHANNELS)
        stream.write(data)
except KeyboardInterrupt:
    print("Client stopped.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
