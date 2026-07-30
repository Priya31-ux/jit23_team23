from picamera2 import Picamera2
from PIL import Image
import pytesseract
import time

# Initialize camera
picam2 = Picamera2()

config = picam2.create_still_configuration(
    main={"size": (1920, 1080)}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

print("Capturing document...")

picam2.capture_file("document.jpg")

picam2.stop()

image = Image.open("document.jpg")

text = pytesseract.image_to_string(image, lang="eng+kan")

print("\nDetected Text:\n")
print(text)
