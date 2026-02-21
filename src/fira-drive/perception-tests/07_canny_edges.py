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
            frame = np.frombuffer(buff[idx*BUFFER_SIZE:(idx+1)*BUFFER_SIZE], dtype=np.uint8).reshape((HEIGHT, WIDTH, CHANNELS))

            # --- PRE-PROCESSING FOR CANNY ---
            # Canny works best on Grayscale and Blurred images
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # --- STEP 7: CANNY EDGE DETECTION ---
            # Syntax: cv2.Canny(image, low_threshold, high_threshold)
            # Low threshold: 50
            # High threshold: 150 (Usually 3x the low threshold)
            edges = cv2.Canny(blurred, 100, 300)

            cv2.imshow("1. Blurred Grayscale", blurred)
            cv2.imshow("2. Canny Edge Detection", edges)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()