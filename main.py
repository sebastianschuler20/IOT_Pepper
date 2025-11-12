from faster_whisper import WhisperModel
from services.audioprocessor.WhisperServiceImpl import WhisperServiceImpl
from services.chatbot.GeminiServiceImpl import GeminiServiceImpl

whisperService = WhisperServiceImpl(WhisperModel("medium", device="cpu", compute_type="int8"),0.25,16000)
geminiService = GeminiServiceImpl()

prompt = whisperService.start_recording()
print(geminiService.generate_response(prompt))

