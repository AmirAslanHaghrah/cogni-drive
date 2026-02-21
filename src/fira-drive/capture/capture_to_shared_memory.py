import time
import struct
from multiprocessing.shared_memory import SharedMemory

import cv2
import zmq
import numpy as np


# Define the number of slots and maximum sequence number
NUM_SLOTS = 4
MAX_SEQUENCE = 10000  # Define the max sequence number before reset

# ZeroMQ setup (Publisher)
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")  # Bind to a port for PUB/SUB communication

def send_sequence_number(sequence_number):
    # 1. Define the topic (must be bytes)
    topic = b"cam0_metadata"
    
    # 2. Pack the sequence number
    sequence_bytes = struct.pack('>I', sequence_number)
    
    # 3. Send as a multipart message
    # send_multipart takes a list of bytes
    socket.send_multipart([topic, sequence_bytes])

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from the camera.")
        exit()

    # Calculate BUFFER_SIZE based on the grabbed image size
    BUFFER_SIZE = np.prod(frame.shape)

    # Create shared memory for camera frames only
    shared_memory_cam0 = SharedMemory(
        name='cam0',
        create=True,
        size=int(NUM_SLOTS * BUFFER_SIZE))

    buff_cam0 = shared_memory_cam0.buf
    sequence_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        # Sequence number logic: alternating odd/even
        sequence_number = (sequence_number + 1) % MAX_SEQUENCE
        
        # Write the buffer to shared memory (for frame data only)
        slot_index = (sequence_number // 2) % NUM_SLOTS
        buff_cam0[slot_index * BUFFER_SIZE : (slot_index + 1) * BUFFER_SIZE] = frame.flatten()

        # Sequence number logic: alternating odd/even
        sequence_number = (sequence_number + 1) % MAX_SEQUENCE

        # Send the sequence number via ZeroMQ
        send_sequence_number(sequence_number)

        # Optional: Control frame rate
        time.sleep(0.1)

    # Clean up
    shared_memory_cam0.close()
    shared_memory_cam0.unlink()

    cap.release()
    cv2.destroyAllWindows()
