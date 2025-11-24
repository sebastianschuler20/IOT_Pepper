import numpy as np

from services.audioprocessor.AudioProcessorService import AudioProcessorService


class WhisperServiceImpl(AudioProcessorService):

    def __init__(self,model,chunk_sec: float, sample_rate: int):
        super().__init__(chunk_sec,sample_rate)
        self.model = model

    def transcribe(self, audio: np.ndarray, language: str = "de") -> str:
        context_prompt = "Gespräch mit dem Roboter Pepper. Pepper wird in den meisten Fällen am Anfang des Satzes gesagt"

        segments, info = self.model.transcribe(
            audio,
            language=language,
            vad_filter=False,
            initial_prompt=context_prompt
        )

        return "".join(seg.text for seg in segments).strip()
