#Ref SVPS-v3.1.1
#Release Notes:
# -Finally using tcp version with optimization
# -Improve high fps up to 28 at least on this equipment
# -Improve latency down between 1.8s and 800ms
# -Added client-server features like delay and frames per second
# -Deprecated usage of mousekeyboard.py and its configurations in client and in server side
# -- 3.1
# -- Added keyboard server script and support directly to this file in server side
# -- Added keyboard client script into clien part manually managed
# -- Both keyboard side scripts supports and requires new versions of config.ini and rutine.ini
# --- 3.1.1
# --- Added client launcher
# --- clientRun is capable of running and managing services, this makes rutine.ini mandatory

import subprocess
import configparser
import time

filename='rutine.ini'
rutine = configparser.ConfigParser()
rutine.read(filename)
rutine = rutine['runtimeConfiguration']

EXT = rutine['EXT']

video = bool(rutine['allowVideoSharing'])
keyboard = bool(rutine['allowkeyboard'])
audio = bool(rutine['allowAudioSharing'])


scripts = {

}

if(video): scripts['video_client'] = f'python clientVideo.{EXT}'
if(audio): scripts['audio_client'] = f'python audioServer.{EXT}'
if(keyboard): scripts['keyboard_client'] = f'python keyboard.{EXT}'

if(not video and not audio and not keyboard):
    print('\nERROR!! At least one service must be set as true.')
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
    
    
# Start each server initially
for server_name in scripts:
    start_server(server_name)

# Keep the main thread running to keep control thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down all clients...")
    for server_name in list(processes.keys()):
        stop_server(server_name)    
    print("All clients stopped.")