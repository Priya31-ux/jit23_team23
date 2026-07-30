from picamera2 import Picamera2
from google import genai
from PIL import Image
from speech import speak
from translator import translate_text
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# ==============================
# Select Language
# ==============================

SELECTED_LANGUAGE = "Hindi"

# Available:
# English
# Hindi
# Kannada
# Tamil
# Telugu
# Malayalam
# Marathi
# Bengali
# Gujarati
# Punjabi

# ==============================
# Camera
# ==============================

picam2 = Picamera2()

config = picam2.create_still_configuration(
    main={"size": (1920, 1080)}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

os.makedirs("images", exist_ok=True)

print("=" * 50)
print("SightSense Started")
print("Selected Language:", SELECTED_LANGUAGE)
print("=" * 50)

previous_response = ""

prompt = """
You are SightSense, an AI assistant for visually impaired users.

Describe the surroundings naturally.

Rules:
1. Mention nearby obstacles first.
2. Mention people and their actions.
3. Mention important objects.
4. Mention doors or pathways.
5. Mention chairs and tables.
6. Read important visible text.
7. Keep the response under 40 words.
8. Never guess.
9. Speak directly to the user.
"""

MAX_RETRIES = 5

try:

    while True:

        print("\nCapturing image...")

        picam2.capture_file("images/current.jpg")

        image = Image.open("images/current.jpg")

        response = None

        for attempt in range(MAX_RETRIES):

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, image]
                )

                break

            except Exception as e:

                print(f"\nGemini Error ({attempt+1}/{MAX_RETRIES})")
                print(e)

                if attempt < MAX_RETRIES - 1:
                    print("Retrying in 5 seconds...\n")
                    time.sleep(5)
                else:
                    print("Skipping this frame...\n")

        if response is None:
            continue

        answer = response.text.strip()

        if not answer:
            continue

        if answer != previous_response:

            print("\nEnglish:")
            print(answer)

            translated_answer = translate_text(
                answer,
                SELECTED_LANGUAGE
            )

            print(f"\n{SELECTED_LANGUAGE}:")
            print(translated_answer)

            speak(
                translated_answer,
                SELECTED_LANGUAGE
            )

            previous_response = answer

        else:

            print("No significant scene change.")

        time.sleep(5)

except KeyboardInterrupt:

    print("\nStopping SightSense...")

finally:

    picam2.stop()
