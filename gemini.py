from picamera2 import Picamera2
from google import genai
from PIL import Image
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# Capture a fresh image
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.configure(config)

picam2.start()
time.sleep(2)

picam2.capture_file("images/current.jpg")
picam2.stop()

# Open the newly captured image
image = Image.open("images/current.jpg")

question = input("Ask SightSense: ")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        question,
        image,
    ],
)

print(response.text)
