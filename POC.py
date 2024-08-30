import cv2
import numpy as np
import socket
import time
def receive_screen(port):
    # Define the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    counter = 0
    buffer = b''
    while True:
        # Receive data from the socket
        data, _ = sock.recvfrom(65507)  # Buffer size may need adjustment
        
        if not data:
            break

        if(len(data)==1):
            print(f'Frames received: {counter-1}')
            print(f'Frames sended: {data.decode()}')
            
            if(int(data.decode()) != (counter-1)):
                # print('Loss Detected')
                continue
            counter = 0
            
            #Si el buffer no se ha llenado, es la ultima parte del frame
            
            
            # Try to decode the buffer into a frame
            np_arr = np.frombuffer(buffer, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # If decoding is successful
            if frame is not None:
                cv2.imshow('Received Screen', frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
            
            # Clear buffer after processing frame
            buffer = b''
            
            # time.sleep(1)
            
        else:
            counter += 1
            print(data.decode())
            # Append received data to buffer
            buffer += data
        


    
    # Close the socket
    sock.close()
    cv2.destroyAllWindows()

# Example usage
receive_screen(12345)
