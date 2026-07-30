import sounddevice as sd
import soundfile as sf
import whisper

model = whisper.load_model("base")

def listen():

    print("Listening... Speak now.")

    samplerate = 16000
    duration = 5

    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='float32'
    )

    sd.wait()

    sf.write("voice.wav", recording, samplerate)

    result = model.transcribe("voice.wav")

    text = result["text"]

    print("You said:", text)

    return text
