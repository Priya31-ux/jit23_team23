
import os
import re
import time
from io import BytesIO

from dotenv import load_dotenv
from google import genai
from picamera2 import Picamera2
from PIL import Image
from speech import speak

# ---------------- SETTINGS ----------------

MODEL = "gemini-flash-lite-latest"
OUTPUT_LANGUAGE = "Kannada"

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

VOICEOVER_PAUSE = 5
JPEG_QUALITY = 75

# ------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=api_key)


def analyze_scene(frame):
    """Return an English description and simple Kannada translation."""

    image = Image.fromarray(frame)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY)
    image_bytes = buffer.getvalue()

    prompt = """
You are SightSense, an assistive vision system for a blind person.

Look carefully at the supplied camera image.

Return exactly these two lines:
ENGLISH: <short English description>
KANNADA: <simple everyday Kannada description>

ENGLISH:
- Use clear, short sentences.
- Mention important nearby objects and where they are.
- Prioritize obstacles, steps, doors, people and possible hazards.
- Do not invent objects or claim a path is safe without evidence.
- Keep it concise, ideally under 25 words.
- Mention uncertainty if the image is unclear.

KANNADA:
- Use natural, simple Kannada spoken in everyday life.
- Use words ordinary Kannada speakers understand easily.
- Avoid formal, literary, textbook or complicated words.
- Avoid unnecessarily long sentences.
- Speak like a helpful person guiding someone who is blind.
- Clearly mention important objects, their positions and visible hazards.
- Translate naturally, not word-for-word.
- Do not add information that is not visible.
- Use Kannada script.
- Keep it short enough to understand when heard once.

Return only the two requested lines. No markdown or extra explanation.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            prompt,
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_bytes,
                }
            },
        ],
        config={
            "temperature": 0.2,
            "max_output_tokens": 150,
        },
    )

    result = (response.text or "").strip()

    english_match = re.search(
        r"ENGLISH:\s*(.*?)(?=\n\s*KANNADA:|$)",
        result,
        re.IGNORECASE | re.DOTALL,
    )

    kannada_match = re.search(
        r"KANNADA:\s*(.*)",
        result,
        re.IGNORECASE | re.DOTALL,
    )

    if not english_match or not kannada_match:
        print("Could not read Gemini response format:")
        print(result)
        return None, None

    english = english_match.group(1).strip().strip('"\'` ')
    kannada = kannada_match.group(1).strip().strip('"\'` ')

    if not english or not kannada:
        return None, None

    return english, kannada


def main():
    camera = Picamera2()

    camera_config = camera.create_video_configuration(
        main={
            "size": (CAMERA_WIDTH, CAMERA_HEIGHT),
            "format": "RGB888",
        },
        buffer_count=2,
    )

    camera.configure(camera_config)
    camera.start()

    # Allow the camera sensor to settle before the first capture.
    time.sleep(1)

    print("=" * 45)
    print("SightSense running")
    print("Description: English")
    print("Output language:", OUTPUT_LANGUAGE)
    print("Voiceover pause:", VOICEOVER_PAUSE, "seconds")
    print("Press Ctrl+C to stop.")
    print("=" * 45)

    previous_kannada = None

    try:
        while True:
            print("\nCapturing scene...", flush=True)

            # Picamera2 capture; no OpenCV VideoCapture required.
            frame = camera.capture_array()

            if frame is None or frame.size == 0:
                print("Camera frame unavailable. Retrying...")
                time.sleep(0.2)
                continue

            try:
                english, kannada = analyze_scene(frame)

                if not english or not kannada:
                    print("No usable description. Trying again.")
                    time.sleep(0.5)
                    continue

                print("\nEnglish:")
                print(english)

                print("\nSimple Kannada:")
                print(kannada)

                normalized = " ".join(kannada.split()).strip()

                # Do not repeat the same description continuously.
                if normalized == previous_kannada:
                    print("Same description; skipping voiceover.")
                    time.sleep(0.5)
                    continue

                print("\nSpeaking Kannada...", flush=True)

                # Assumes speak() waits until audio playback completes.
                speak(kannada, OUTPUT_LANGUAGE)

                previous_kannada = normalized

                print(
                    f"\nVoiceover complete. Pausing "
                    f"{VOICEOVER_PAUSE} seconds...",
                    flush=True,
                )

                # Five-second pause AFTER the voiceover finishes.
                time.sleep(VOICEOVER_PAUSE)

            except KeyboardInterrupt:
                raise
            except Exception as error:
                print(f"Scene processing error: {error}")
                time.sleep(1)

    finally:
        camera.stop()
        camera.close()
        print("\nSightSense stopped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping SightSense...")
