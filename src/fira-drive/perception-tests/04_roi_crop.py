import struct
import cv2
import numpy as np
import zmq
from multiprocessing.shared_memory import SharedMemory

# Config (Must match Producer)
NUM_SLOTS, WIDTH, HEIGHT, CHANNELS = 4, 640, 480, 3
BUFFER_SIZE = WIDTH * HEIGHT * CHANNELS

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
            seq = struct.unpack('>I', parts[1])[0]
            if seq % 2 != 0: continue 

            idx = (seq // 2) % NUM_SLOTS
            start = idx * BUFFER_SIZE
            
            raw_data = np.frombuffer(buff[start : start + BUFFER_SIZE], dtype=np.uint8)
            frame = raw_data.reshape((HEIGHT, WIDTH, CHANNELS))

            # --- PRE-PROCESSING: ROI (CROP) ---
            
            # Define the region: [start_y:end_y, start_x:end_x]
            # We focus on the bottom half of the image where the road is.
            roi_start_row = int(HEIGHT * 0.5) # Start 60% down the image
            roi_end_row = HEIGHT             # Go to the bottom
            
            roi_frame = frame[roi_start_row:roi_end_row, 0:WIDTH]

            # --- OPTIONAL: MASKED ROI ---
            # Instead of a square crop, we can use a triangle/trapezoid mask
            mask = np.zeros_like(frame)
            polygon = np.array([[
                (0, HEIGHT), 
                (WIDTH, HEIGHT), 
                (int(WIDTH*0.8), int(HEIGHT*0.5)), 
                (int(WIDTH*0.2), int(HEIGHT*0.5))
            ]], np.int32)
            
            cv2.fillPoly(mask, polygon, (255, 255, 255))
            masked_image = cv2.bitwise_and(frame, mask)

            # Display
            cv2.imshow("1. Full Frame (Original)", frame)
            cv2.imshow("2. ROI Crop (Focus on Road)", roi_frame)
            cv2.imshow("3. Masked ROI (Trapezoid)", masked_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()