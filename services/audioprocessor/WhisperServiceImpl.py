import numpy as np

from services.audioprocessor.AudioProcessorService import AudioProcessorService


class WhisperServiceImpl(AudioProcessorService):

    def __init__(self,model,chunk_sec: float, sample_rate: int):
        super().__init__(chunk_sec,sample_rate)
        self.model = model

    def transcribe(self, audio: np.ndarray, language: str = "de") -> str:
        context_prompt = "Das folgende ist ein Gespräch mit dem humanoiden Roboter namens Pepper. Es wird entweder Smalltalk mit ihm geführt oder ihm wird befohlen zu tanzen oder zu singen. Beispiele für Befehle sind 'Pepper tanz' oder 'Pepper sing'. Beispiele für Smalltalk sind 'Pepper Wie wird das Wetter morgen', 'Pepper Erzähl mir etwas über Angela Merkel', 'Pepper Gib mir Kochrezepte,  Als Anrede wird am Anfang Pepper gesagt"

        segments, info = self.model.transcribe(
            audio,
            language=language,
            vad_filter=False,
            initial_prompt=context_prompt
        )

        return "".join(seg.text for seg in segments).strip()
