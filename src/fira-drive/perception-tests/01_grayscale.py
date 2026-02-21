import struct
import cv2
import numpy as np
import zmq
from multiprocessing.shared_memory import SharedMemory

# Configuration (Must match your Producer/Camera settings)
NUM_SLOTS = 4
WIDTH, HEIGHT, CHANNELS = 640, 480, 3 
BUFFER_SIZE = WIDTH * HEIGHT * CHANNELS 

# ZeroMQ Subscriber Setup
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"cam0_metadata")

def main():
    # Connect to the Shared Memory created by your Producer
    try:
        shm = SharedMemory(name='cam0', create=False)
        buff = shm.buf
        print("Connected to Shared Memory. Processing frames...")
    except FileNotFoundError:
        print("Error: Shared memory 'cam0' not found. Start the Producer first!")
        return

    try:
        while True:
            # 1. Wait for the sequence number from ZeroMQ
            parts = socket.recv_multipart()
            sequence_number = struct.unpack('>I', parts[1])[0]

            # 2. Safety Check: Only process "Ready" (Even) frames
            if sequence_number % 2 != 0:
                continue

            # 3. Calculate memory location
            slot_index = (sequence_number // 2) % NUM_SLOTS
            start = slot_index * BUFFER_SIZE
            end = start + BUFFER_SIZE

            # 4. Map the raw data to a NumPy array
            raw_data = np.frombuffer(buff[start:end], dtype=np.uint8)
            frame = raw_data.reshape((HEIGHT, WIDTH, CHANNELS))

            # --- PRE-PROCESSING STEP: GRAYSCALE ---
            # This converts (H, W, 3) to (H, W, 1)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 5. Display the result
            cv2.imshow("Perception Step 1: Grayscale", gray_frame)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()