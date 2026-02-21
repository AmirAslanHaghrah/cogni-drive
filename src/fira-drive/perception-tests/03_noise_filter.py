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

            if seq % 2 != 0: continue # Skip if not ready

            idx = (seq // 2) % NUM_SLOTS
            start = idx * BUFFER_SIZE
            
            # Get raw frame
            raw_data = np.frombuffer(buff[start : start + BUFFER_SIZE], dtype=np.uint8)
            frame = raw_data.reshape((HEIGHT, WIDTH, CHANNELS))

            # --- PRE-PROCESSING: NOISE FILTERS ---
            
            # 1. Grayscale first (Commonly done before blurring)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 2. Gaussian Blur 
            # (5, 5) is the kernel size. Must be ODD numbers. 
            # Larger numbers = more blur = less noise = slower processing.
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 3. Median Blur (Excellent for 'salt and pepper' noise)
            # Good if you see random white/black dots.
            median = cv2.medianBlur(gray, 5)

            # Display comparisons
            cv2.imshow("1. Original Gray", gray)
            cv2.imshow("2. Gaussian Blur (Smoothed)", blurred)
            cv2.imshow("3. Median Blur (Noise Removed)", median)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()