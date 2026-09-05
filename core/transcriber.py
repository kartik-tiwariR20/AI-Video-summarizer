import whisper
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

_model = None


def load_model():
    global _model
    if _model is None:
        print("loading model")
        _model = whisper.load_model(WHISPER_MODEL)
        print("whisper model downloaded succesfully")
    return _model


def transcribe_chunk(chunk_path: str, task: str = "transcribe") -> str:
    model = load_model()
    result = model.transcribe(chunk_path, task=task)
    return result["text"]


def transcribe_all(chunks: list, language: str = "english") -> str:
    task = "transcribe"  # both english/hinglish just transcribe as-is, no forced translation

    full_transcript = ""
    for i, chunk in enumerate(chunks):
        print(f"Transcribing Chunks {i+1}")
        text = transcribe_chunk(chunk, task=task)
        full_transcript += text + " "

    print("Transcription Completed")
    return full_transcript.strip()
