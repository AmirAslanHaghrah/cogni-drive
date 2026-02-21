import struct
from multiprocessing.shared_memory import SharedMemory

import cv2
import numpy as np
import zmq

# Define the number of slots and frame resolution (must match Publisher exactly)
NUM_SLOTS = 4
WIDTH, HEIGHT, CHANNELS = 640, 480, 3 
BUFFER_SIZE = WIDTH * HEIGHT * CHANNELS 

# ZeroMQ setup (Subscriber)
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")

# --- UPDATE: Subscribe to a specific topic ---
TOPIC = b"cam0_metadata"
socket.setsockopt(zmq.SUBSCRIBE, TOPIC)

# Connect to the existing shared memory
try:
    shared_memory_cam0 = SharedMemory(name='cam0', create=False)
    buff_cam0 = shared_memory_cam0.buf
except FileNotFoundError:
    print("Error: Shared memory 'cam0' not found. Is the publisher running?")
    exit()

def receive_sequence_number_and_display():
    print(f"Listening for topic: {TOPIC.decode()}...")
    
    while True:
        # ZeroMQ strips the topic for you if you check frames, 
        # but recv_multipart returns the whole list.
        parts = socket.recv_multipart()
        
        if len(parts) < 2:
            continue

        topic_received = parts[0]
        sequence_bytes = parts[1]
        
        # Unpack the 4-byte integer
        sequence_number = struct.unpack('>I', sequence_bytes)[0]
        
        # Calculate the slot index (matching the publisher logic)
        slot_index = (sequence_number // 2) % NUM_SLOTS
        
        # Extract the frame from shared memory
        start = slot_index * BUFFER_SIZE
        end = start + BUFFER_SIZE
        
        # Create a non-copying view of the memory for performance
        frame_data = np.frombuffer(buff_cam0[start:end], dtype=np.uint8)
        frame = frame_data.reshape((HEIGHT, WIDTH, CHANNELS))

        # Display
        cv2.imshow("Video Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    shared_memory_cam0.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    receive_sequence_number_and_display()