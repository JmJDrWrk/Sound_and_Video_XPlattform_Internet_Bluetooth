#Ref SVPS-v4.0
#Release Notes:
# - Added support for mouse
# - Added support for keyboard
# - Mouse sends relative position
# - Unoptimized mouse sendings and extra callings inside mouseClient and clientVideo
# - New port in use localhost between mouseClient and clientVideo
# - ClientVideo and mouseClient requires to run together at least in this version

import subprocess
import configparser
import time
import socket
import atexit

filename='rutine.ini'
rutine = configparser.ConfigParser()
rutine.read(filename)
rutine = rutine['runtimeConfiguration']

EXT = rutine['EXT']
CONTROL_PORT = int(rutine['controlport'])
CONTROL_IP = rutine['controlip']

video = bool(rutine['allowVideoSharing'])
keyboard = bool(rutine['allowkeyboard'])
audio = bool(rutine['allowAudioSharing'])
mouse = bool(rutine['allowMouse'])


scripts = {

}

if(video): scripts['video_client'] = f'python clientVideo.{EXT}'
if(audio): scripts['audio_client'] = f'python clientAudio.{EXT}'
if(keyboard): scripts['keyboard_client'] = f'python keyboard.{EXT}'
if(mouse): scripts['mouse_client'] = f'python mouseClient.{EXT}'

if(not video and not audio and not keyboard):
    print('\nERROR!! At least one service must be set as true.')
    exit()
    
    
    
    
# before connecting anything, tell server to restart all services for preventing bugs
control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SERVICES = ['video_server','keyboard_server','mouse_server']
# Temporal solution
for service in SERVICES:
    print(f'\t Restarting service: {service}')
    control_socket.sendto(f'restart {service}'.encode(), (CONTROL_IP, CONTROL_PORT))

    

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
    
    
# Start each server initially
for server_name in scripts:
    start_server(server_name)

def on_exit():
    print('Forced Exit')
    for server_name in list(processes.keys()):
        print(f'Stopping {server_name}')
        stop_server(server_name)    
    print("All clients stopped.")
    
atexit.register(on_exit)

# Keep the main thread running to keep control thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down all clients...")
    for server_name in SERVICES:#list(processes.keys()):
        stop_server(server_name)    
    print("All clients stopped.")