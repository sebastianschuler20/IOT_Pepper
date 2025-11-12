from abc import ABC, abstractmethod
import numpy as np
import sounddevice as sd
import keyboard



class AudioProcessorService(ABC):
    """
    Abstract base class for an Audio Processor Service.

    This class defines the interface for processing audio files, including features extraction.

    """

    def __init__(self,chunk_sec: float, sample_rate: int):
        self.chunk_sec = chunk_sec
        self.sample_rate = sample_rate

    def record_chunk(self, seconds: float = None, samplerate: int = None) -> np.ndarray:
        # Wenn None, benutze die Instanzwerte
        if seconds is None:
            seconds = self.chunk_sec
        if samplerate is None:
            samplerate = self.sample_rate

        audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="float32")
        sd.wait()
        return audio.flatten()

    def start_recording(self) -> str:
        print("Halte STRG zum Aufnehmen…")
        keyboard.wait("ctrl")

        print("Aufnahme läuft…")
        chunks = []
        while keyboard.is_pressed("ctrl"):
            chunks.append(self.record_chunk())

        print("Aufnahme beendet.")

        if chunks:
            audio = np.concatenate(chunks).astype(np.float32)
        else:
            audio = np.array([], dtype=np.float32)

        print(f"Länge aufgenommen: {audio.shape[0] / self.sample_rate:.2f} s")

        if audio.size == 0:
            print("Kein Audio aufgenommen.")
            return "Habe ich nicht verstanden"
        else:
            prompt = self.transcribe(audio)
            print("\nTranskript:\n", prompt if prompt else "(leer)")
            return prompt

    @abstractmethod
    def transcribe(self, audio: np.ndarray, language: str = "de") -> str:
        """
        Jede Subklasse muss diese Methode implementieren.
        """
        pass