import asyncio
import os
import subprocess
import edge_tts

VOICE_MAP = {
    "English": "en-IN-NeerjaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Kannada": "kn-IN-SapnaNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Telugu": "te-IN-ShrutiNeural",
    "Malayalam": "ml-IN-SobhanaNeural",
    "Marathi": "mr-IN-AarohiNeural",
    "Bengali": "bn-IN-TanishaaNeural",
    "Gujarati": "gu-IN-DhwaniNeural",
    "Punjabi": "pa-IN-OjasNeural"
}


async def generate_speech(text, voice):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save("speech.mp3")


def speak(text, language="English"):
    voice = VOICE_MAP.get(language, "en-IN-NeerjaNeural")

    asyncio.run(generate_speech(text, voice))

    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "speech.mp3"]
    )

    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")
