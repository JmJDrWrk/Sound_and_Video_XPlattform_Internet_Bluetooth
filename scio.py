# screen_share_server.py

import socketio
import base64
import cv2
import numpy as np
import pyautogui
import threading
import time

# Create a Socket.IO server
sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Function to capture the screen and send frames
def capture_and_send():
    while True:
        # Capture the screen using pyautogui
        screenshot = pyautogui.screenshot()

        # Convert the screenshot to a NumPy array
        frame = np.array(screenshot)

        # Convert the frame to a byte string
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the client
        sio.emit('screen_frame', jpg_as_text)

        # Wait for a short interval to reduce CPU usage
        time.sleep(0.1)

@sio.event
def connect(sid, environ):
    print(f"Client {sid} connected")

@sio.event
def disconnect(sid):
    print(f"Client {sid} disconnected")

if __name__ == '__main__':
    # Start a new thread to capture and send frames
    thread = threading.Thread(target=capture_and_send)
    thread.start()

    # Serve the app on localhost:5000
    from wsgiref import simple_server
    server = simple_server.make_server('0.0.0.0', 5000, app)
    print("Serving on http://0.0.0.0:5000")
    server.serve_forever()
