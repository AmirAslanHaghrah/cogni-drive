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

    try:
        while True:
            parts = socket.recv_multipart()
            seq = struct.unpack('>I', parts[1])[0]
            if seq % 2 != 0: continue 

            idx = (seq // 2) % NUM_SLOTS
            frame = np.frombuffer(buff[idx*BUFFER_SIZE:(idx+1)*BUFFER_SIZE], dtype=np.uint8).reshape((HEIGHT, WIDTH, CHANNELS))

            # --- PRE-PROCESSING PIPELINE ---
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blur, 50, 150)

            # --- STEP 9: HOUGH LINE DETECTION ---
            # Parameters:
            # 1: rho (distance resolution in pixels)
            # np.pi/180: theta (angle resolution in radians)
            # 50: threshold (min votes to be a 'line')
            # minLineLength: skip short lines
            # maxLineGap: join segments if they are close
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)

            # Create a copy to draw on
            line_image = frame.copy()

            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 3)

            cv2.imshow("Detected Hough Lines", line_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()