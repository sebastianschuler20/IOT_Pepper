import json
import os

import numpy as np
from vosk import KaldiRecognizer, Model

from services.audioprocessor.AudioProcessorService import AudioProcessorService


class VoskServiceImpl(AudioProcessorService):
    """
    Transcription service using a local Vosk model.
    Expect `model_path` to point to an unpacked Vosk model directory inside the workspace.
    """

    def __init__(self, model_path: str, chunk_sec: float, sample_rate: int):
        super().__init__(chunk_sec, sample_rate)

        if not os.path.isdir(model_path):
            raise FileNotFoundError(
                f"Vosk model not found at {model_path}. "
                "Place the unpacked model folder in the workspace and update the path."
            )

        self.model_path = model_path
        self.model = Model(model_path)

    def _decode_result(self, result: str) -> str:
        """
        Vosk returns JSON with a `text` field. Parse and return it safely.
        """
        try:
            payload = json.loads(result)
            return payload.get("text", "").strip()
        except json.JSONDecodeError:
            return ""

    def _decode_partial(self, result: str) -> str:
        """
        Parses partial results (key `partial`).
        """
        try:
            payload = json.loads(result)
            return payload.get("partial", "").strip()
        except json.JSONDecodeError:
            return ""

    def create_recognizer(self) -> KaldiRecognizer:
        """
        Returns a fresh recognizer for streaming use.
        """
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        recognizer.SetWords(True)
        return recognizer

    def audio_to_pcm(self, audio: np.ndarray) -> bytes:
        """
        Convert float32 audio to int16 PCM bytes for Vosk.
        """
        return (audio * 32767).astype(np.int16).tobytes()

    def transcribe(self, audio: np.ndarray, language: str = "de") -> str:
        """
        Convert float32 audio to int16 PCM and run through Vosk recognizer.
        """
        if audio.size == 0:
            return ""

        # Vosk expects int16 PCM. AudioProcessorService records float32 in [-1, 1].
        pcm_audio = self.audio_to_pcm(audio)
        recognizer = self.create_recognizer()
        recognizer.AcceptWaveform(pcm_audio)

        text = self._decode_result(recognizer.FinalResult())
        return text
