from picamera2 import Picamera2
import time

picam2 = None

def start_camera():
    global picam2

    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )

    picam2.configure(config)
    picam2.start()

    time.sleep(2)

def get_frame():
    return picam2.capture_array()

def stop_camera():
    picam2.stop()