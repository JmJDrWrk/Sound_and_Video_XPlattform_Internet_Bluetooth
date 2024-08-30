# screen_share_client.py

import socketio
import base64
import cv2
import numpy as np

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on('screen_frame')
def on_screen_frame(data):
    # Decode the base64-encoded image
    jpg_original = base64.b64decode(data)
    
    # Convert it to a NumPy array
    np_arr = np.frombuffer(jpg_original, dtype=np.uint8)
    
    # Decode the image to display it
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    # Display the frame
    cv2.imshow('Screen Share', frame)
    if cv2.waitKey(1) == ord('q'):
        sio.disconnect()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # Connect to the server
    sio.connect('http://localhost:5000')

    # Keep the script running
    sio.wait()
