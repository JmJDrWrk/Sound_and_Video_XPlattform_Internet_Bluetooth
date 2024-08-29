# EXT = 'exe'

import subprocess
import signal
import time
import socket
import threading
import configparser

filename='rutine.ini'
rutine = configparser.ConfigParser()
rutine.read(filename)
rutine = rutine['runtimeConfiguration']

EXT = rutine['EXT']

controlPort = int(rutine['controlport']) # 9548
video = bool(rutine['allowVideoSharing'])
mouseandkeyboard= bool(rutine['allowMouseAndKeyboardBeingControlled'])
audio = bool(rutine['allowAudioSharing'])

CONTROL_PORT = controlPort


scripts = {

}

if(video): scripts['video_server'] = f'python videoServer.{EXT}'
if(audio): scripts['audio_server'] = f'python audioServer.{EXT}'
if(mouseandkeyboard): scripts['video_mouse_server'] = f'python mousekeyboard.{EXT}'

if(not video and not audio and not mouseandkeyboard):
    print('\nERROR!! At least one server must be set as true.')
    exit()


processes = {}

def start_server(server_name):
#    #Starts a server process.
    if server_name in scripts:
        print(f"{server_name}: UP")
        process = subprocess.Popen(scripts[server_name], shell=True)
        processes[server_name] = process
        print(f"\tstarted {server_name} with PID {process.pid}")

def stop_server(server_name):
#    #Stops a server process.
    process = processes.get(server_name)
    if process:
        print(f"[control] terminate {server_name} ")
        process.terminate()  # or process.kill() for immediate termination
        process.wait()  # Wait for process to terminate
        del processes[server_name]
        print(f"\n{server_name}: DOWN\n")
    else:
        print(f"No running process found for {server_name}")

def restart_server(server_name):
#    #Restarts a server process.
    stop_server(server_name)
    start_server(server_name)

def control_server():
#    #Thread function to handle incoming commands to control servers.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', CONTROL_PORT))  # Bind to localhost and port 9999

    print("control_server: UP\n")
    while True:
        data, addr = server_socket.recvfrom(1024)
        command = data.decode("utf-8")
        print('\n[control]', command, '\n')
        if command.startswith("restart"):
            _, server_name = command.split()
            restart_server(server_name)


# Start control server in a separate thread
control_thread = threading.Thread(target=control_server)
control_thread.daemon = True
control_thread.start()

# Start each server initially
for server_name in scripts:
    start_server(server_name)

# Keep the main thread running to keep control thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down all servers...")
    for server_name in list(processes.keys()):
        stop_server(server_name)
    print("All servers stopped.")