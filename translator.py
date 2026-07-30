from deep_translator import GoogleTranslator

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Punjabi": "pa"
}


def translate_text(text, language):
    if language == "English":
        return text

    try:
        return GoogleTranslator(
            source="auto",
            target=LANGUAGES[language]
        ).translate(text)

    except Exception as e:
        print("Translation Error:", e)
        return text
