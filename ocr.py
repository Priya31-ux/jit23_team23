from google import genai
from PIL import Image
from speech import speak
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

def read_text(image_path):
    image = Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            """
            Read all clearly visible text in the image.

            Rules:
            - Read only visible text.
            - Preserve the order as much as possible.
            - If no readable text is present, reply:
              'No readable text found.'
            """,
            image,
        ],
    )

    text = response.text.strip()
    print(text)
    speak(text)
    return text
