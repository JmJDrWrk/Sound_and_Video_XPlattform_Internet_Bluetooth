import subprocess
#Este codigo no ha sido probado ni aporta nada a la ejecución RECOMIENDO lanzar los scripts de forma manual
scripts = [
    'python ClientAudio.py',
    'python ClientVideo.py'
]

processes = []


for script in scripts:
    process = subprocess.Popen(script, shell=True)
    processes.append(process)
    print(f'Started: {script}')
    
for process in processes:
    process.wait()

print('Scripts have ended!')