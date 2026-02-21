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

    # Define a Kernel (The "brush" used to clean the image)
    # A 5x5 kernel is usually strong enough for FIRA tracks.
    kernel = np.ones((5, 5), np.uint8)

    try:
        while True:
            parts = socket.recv_multipart()
            seq = struct.unpack('>I', parts[1])[0]
            if seq % 2 != 0: continue 

            idx = (seq // 2) % NUM_SLOTS
            frame = np.frombuffer(buff[idx*BUFFER_SIZE:(idx+1)*BUFFER_SIZE], dtype=np.uint8).reshape((HEIGHT, WIDTH, CHANNELS))

            # --- PRE-PROCESSING STEPS BEFORE MORPHOLOGY ---
            # 1. Grayscale & Blur
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 2. Thresholding (Create a binary Black & White image)
            # This makes the "lanes" white and the road black.
            _, binary_mask = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

            # --- STEP 6: MORPHOLOGICAL TRANSFORMATIONS ---
            
            # OPENING (Erosion followed by Dilation) - Removes small white noise
            opening = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
            
            # CLOSING (Dilation followed by Erosion) - Fills holes in the lane
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

            cv2.imshow("1. Raw Binary Mask (Noisy)", binary_mask)
            cv2.imshow("2. After Opening (Noise Removed)", opening)
            cv2.imshow("3. After Closing (Gaps Filled)", closing)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()