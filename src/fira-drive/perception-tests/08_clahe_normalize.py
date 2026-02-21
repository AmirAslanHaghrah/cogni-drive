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
        return

    # Create CLAHE object (Arguments: clipLimit=contrast threshold, tileGridSize=section size)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    while True:
        parts = socket.recv_multipart()
        seq = struct.unpack('>I', parts[1])[0]
        if seq % 2 != 0: continue 

        idx = (seq // 2) % NUM_SLOTS
        frame = np.frombuffer(buff[idx*BUFFER_SIZE:(idx+1)*BUFFER_SIZE], dtype=np.uint8).reshape((HEIGHT, WIDTH, CHANNELS))

        # 1. Convert to YUV (Luminance + Chrominance)
        # We only want to equalize the 'Y' (Brightness) channel to avoid weird color shifts
        img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

        # 2. Apply CLAHE to the Y channel
        img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])

        # 3. Convert back to BGR
        normalized_frame = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

        cv2.imshow("1. Original Frame (Shadows/Glaring)", frame)
        cv2.imshow("2. CLAHE Normalized (Balanced Contrast)", normalized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    shm.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()