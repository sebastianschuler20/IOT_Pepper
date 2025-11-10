import keyboard
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

import gemini_api

SAMPLE_RATE = 16000
CHUNK_SEC = 0.25

model = WhisperModel("small", device="cpu", compute_type="int8")

def record_chunk(seconds: float = CHUNK_SEC, samplerate: int = SAMPLE_RATE) -> np.ndarray:
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()

def transcribe(audio: np.ndarray, language: str = "de") -> str:
    segments, info = model.transcribe(audio, language=language, vad_filter=False)
    return "".join(seg.text for seg in segments).strip()

#--------------------------------------------------------------------------------------------------
# Aufnahme-Steuerung
#--------------------------------------------------------------------------------------------------
print("Halte STRG zum Aufnehmen…")
keyboard.wait("ctrl")

print("Aufnahme läuft…")
chunks = []
while keyboard.is_pressed("ctrl"):
    chunks.append(record_chunk())

print("Aufnahme beendet.")

if chunks:
    audio = np.concatenate(chunks).astype(np.float32)
else:
    audio = np.array([], dtype=np.float32) 

print(f"Länge aufgenommen: {audio.shape[0]/SAMPLE_RATE:.2f} s")

if audio.size == 0:
    print("Kein Audio aufgenommen.")
else:
    text = transcribe(audio)
    #print("\nTranskript:\n", text if text else "(leer)")

print(f"Gemini-Anwort: {gemini_api.generate_ai_content(text)}")
