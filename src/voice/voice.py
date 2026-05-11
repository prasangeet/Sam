import queue
import sounddevice as sd
import vosk
import json
import pyttsx3
import os

# -------------------------------
# 🔊 TEXT TO SPEECH
# -------------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)


def speak(text: str):
    print(f"Sam: {text}")
    engine.say(text)
    engine.runAndWait()


# -------------------------------
# 🎤 SPEECH TO TEXT
# -------------------------------
q = queue.Queue()


def _callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


# resolve model path safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../../models/vosk-model-small-en-us-0.15")

model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)


def listen() -> str:
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=_callback,
    ):
        print("🎤 Listening...")

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()

                if text:
                    print(f"You: {text}")
                    return text
