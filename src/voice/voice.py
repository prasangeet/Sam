import queue
import tempfile
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import sounddevice as sd
import scipy.io.wavfile as wav

import pyttsx3

from faster_whisper import (
    WhisperModel
)

from src.observability.bus import (
    event_bus
)


# -----------------------------------
# Text To Speech
# -----------------------------------
engine = pyttsx3.init()

engine.setProperty(
    "rate",
    170
)


def speak(
    text: str
):

    event_bus.emit(
        "tts_started",
        {
            "text": text
        }
    )

    print(f"Sam: {text}")

    engine.say(text)

    engine.runAndWait()

    event_bus.emit(
        "tts_completed",
        {}
    )


# -----------------------------------
# Whisper Model
# -----------------------------------
MODEL_SIZE = "small.en"

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

event_bus.emit(
    "stt_model_loaded",
    {
        "model": MODEL_SIZE
    }
)


# -----------------------------------
# Audio Config
# -----------------------------------
SAMPLE_RATE = 16000

CHANNELS = 1

DURATION = 5


# -----------------------------------
# Record Audio
# -----------------------------------
def record_audio():

    event_bus.emit(
        "audio_recording_started",
        {}
    )

    print("🎤 Listening...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    event_bus.emit(
        "audio_recording_completed",
        {}
    )

    return audio


# -----------------------------------
# Speech To Text
# -----------------------------------
def listen() -> str:

    try:

        audio = record_audio()

        with tempfile.NamedTemporaryFile(
            suffix=".wav"
        ) as temp_audio:

            wav.write(
                temp_audio.name,
                SAMPLE_RATE,
                audio
            )

            event_bus.emit(
                "transcription_started",
                {}
            )

            segments, info = model.transcribe(
                temp_audio.name,
                beam_size=5
            )

            text = " ".join(
                segment.text
                for segment in segments
            ).strip()

            event_bus.emit(
                "transcription_completed",
                {
                    "language": info.language,
                    "text": text
                }
            )

            if text:

                print(f"You: {text}")

            return text

    except Exception as e:

        event_bus.emit(
            "transcription_failed",
            {
                "error": str(e)
            }
        )

        print(
            f"[Voice Error] {e}"
        )

        return ""
