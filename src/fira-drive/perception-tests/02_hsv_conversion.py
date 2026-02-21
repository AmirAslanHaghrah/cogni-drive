import struct
import cv2
import numpy as np
import zmq
from multiprocessing.shared_memory import SharedMemory

# Configuration (Must match your Producer)
NUM_SLOTS = 4
WIDTH, HEIGHT, CHANNELS = 640, 480, 3 
BUFFER_SIZE = WIDTH * HEIGHT * CHANNELS 

# ZeroMQ Setup
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"cam0_metadata")

def main():
    try:
        shm = SharedMemory(name='cam0', create=False)
        buff = shm.buf
    except FileNotFoundError:
        print("Start the Producer first!")
        return

    try:
        while True:
            parts = socket.recv_multipart()
            sequence_number = struct.unpack('>I', parts[1])[0]

            if sequence_number % 2 != 0:
                continue

            slot_index = (sequence_number // 2) % NUM_SLOTS
            start = slot_index * BUFFER_SIZE
            
            # 1. Get raw BGR frame
            raw_data = np.frombuffer(buff[start : start + BUFFER_SIZE], dtype=np.uint8)
            frame = raw_data.reshape((HEIGHT, WIDTH, CHANNELS))

            # 2. Convert to HSV
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 3. Extract individual channels for visualization
            # H = Hue (Color), S = Saturation (Intensity), V = Value (Brightness)
            h, s, v = cv2.split(hsv_frame)

            # Displaying the Hue channel is best for finding specific colors
            cv2.imshow("Original BGR", frame)
            cv2.imshow("HSV - Hue Channel (Colors)", h)
            cv2.imshow("HSV - Saturation Channel", s)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()