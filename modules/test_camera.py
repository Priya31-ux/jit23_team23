from modules.camera import start_camera, get_frame, stop_camera
import cv2

start_camera()

while True:

    frame = get_frame()

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord("q"):
        break

stop_camera()

cv2.destroyAllWindows()