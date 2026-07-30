from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import time

print("Loading YOLO model...")
model = YOLO("yolov8n.pt")
print("YOLO model loaded!")

# Initialize Raspberry Pi Camera
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

print("Camera started. Press 'q' to quit.")

try:
    while True:
        # Capture frame from Pi Camera
        frame = picam2.capture_array()

        # Run YOLO
        results = model(frame)

        # Draw detections
        annotated_frame = results[0].plot()

        # Print detected objects
        detections = []

        for box in results[0].boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            detections.append(label)

        if detections:
            print("Detected:", ", ".join(sorted(set(detections))))

        # Display window
        cv2.imshow("SightSense - YOLO Detection", annotated_frame)

        # Quit on q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
