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

    # --- TUNE THESE POINTS FOR YOUR TRACK ---
    # Pick 4 points on the raw image that form a TRAPEZOID on the road
    # Order: [top-left, top-right, bottom-right, bottom_left]
    src_pts = np.float32([
        [240, 300], [400, 300],  # Top of the road section
        [640, 450], [0, 450]     # Bottom of the road section
    ])
    
    # Map them to a perfect RECTANGLE in the output
    dst_pts = np.float32([
        [0, 0], [WIDTH, 0],
        [WIDTH, HEIGHT], [0, HEIGHT]
    ])

    # Calculate the transformation matrix once
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

    try:
        while True:
            parts = socket.recv_multipart()
            seq = struct.unpack('>I', parts[1])[0]
            if seq % 2 != 0: continue 

            idx = (seq // 2) % NUM_SLOTS
            frame = np.frombuffer(buff[idx*BUFFER_SIZE:(idx+1)*BUFFER_SIZE], dtype=np.uint8).reshape((HEIGHT, WIDTH, CHANNELS))

            # --- WARP THE IMAGE ---
            bev_frame = cv2.warpPerspective(frame, matrix, (WIDTH, HEIGHT))

            # Draw the source points on the original frame so you can see what you are warping
            debug_frame = frame.copy()
            for pt in src_pts:
                cv2.circle(debug_frame, tuple(pt.astype(int)), 10, (0, 255, 0), -1)

            cv2.imshow("1. Original with Source Points", debug_frame)
            cv2.imshow("2. Bird's Eye View", bev_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        shm.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()