from faster_whisper import WhisperModel

from services.audioprocessor.CheckCommandService import CommandService
from services.audioprocessor.WhisperServiceImpl import WhisperServiceImpl
from services.chatbot.GeminiServiceImpl import GeminiServiceImpl
from services.sshservice.SSHService import SSHService

print("Initialisiere Services...")
whisperService = WhisperServiceImpl(WhisperModel("small", device="cpu", compute_type="int8"), 0.25, 16000)
print("WhisperService bereit.")

geminiService = GeminiServiceImpl()
print("GeminiService bereit.")

commandService = CommandService()
print("CommandService bereit.")

ssh_host = "HIER_IP_EINFUEGEN"
sshService = None
if ssh_host == "HIER_IP_EINFUEGEN":
    print("SSHService NICHT gestartet: keine IP hinterlegt und aktuell kein Zugriff auf das Gerät.")
else:
    sshService = SSHService(host=ssh_host, username="nao", password="nao", key_filename=None)
    print(f"SSHService bereit für Host {ssh_host}.")

print("System bereit. Aufnahme startet, wenn STRG gehalten wird...")
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
