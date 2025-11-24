from faster_whisper import WhisperModel

from services.audioprocessor.CheckCommandService import CommandService
from services.audioprocessor.WhisperServiceImpl import WhisperServiceImpl
from services.chatbot.GeminiServiceImpl import GeminiServiceImpl

whisperService = WhisperServiceImpl(WhisperModel("medium", device="cpu", compute_type="int8"),0.25,16000)
geminiService = GeminiServiceImpl()
commandService = CommandService()

prompt = whisperService.start_recording()
# 2. Check: Ist es ein Befehl?
command_type = commandService.check_command(prompt)

if command_type:
    # JA: Führe Roboter-Aktion aus (Kein Gemini Aufruf)
    print(f"Befehl erkannt: {command_type}")
    response_text = commandService.execute_command(command_type)
    print(f"Pepper sagt: {response_text}")

else:
    # NEIN: Es ist Smalltalk -> Ab zu Gemini
    print("Kein Befehl erkannt, frage Gemini...")
    response = geminiService.generate_response(prompt)
    print(response)

