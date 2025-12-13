from services.audioprocessor.CheckCommandService import CommandService
from services.audioprocessor.VoskServiceImpl import VoskServiceImpl
from services.chatbot.GeminiServiceImpl import GeminiServiceImpl
from services.intent.IntentRouterService import IntentFunction, IntentRouterService
from services.sshservice.SSHService import SSHService
import numpy as np
from collections import deque
import threading

print("Initialisiere Services...")
vosk_model_path = "models/vosk-model-small-de-0.15"
voskService = VoskServiceImpl(model_path=vosk_model_path, chunk_sec=0.25, sample_rate=16000)
print("VoskService bereit.")

geminiService = GeminiServiceImpl()
print("GeminiService bereit.")

# --- SSH zuerst ---
ssh_host = "HIER_IP_EINFUEGEN" #"143.93.211.53"
sshService = None
if ssh_host == "HIER_IP_EINFUEGEN":
    print("SSHService NICHT gestartet: keine IP hinterlegt und aktuell kein Zugriff auf das Gerät.")
else:
    sshService = SSHService(host=ssh_host, username="nao", password="nao", key_filename=None)
    sshService.connect()
    print(f"SSHService bereit für Host {ssh_host}.")


def speak_async(text: str) -> None:
    """Spricht den Text über SSH ohne den Haupt-Thread zu blockieren."""
    if sshService:
        threading.Thread(target=sshService.execute_talk, args=(text,), daemon=True).start()
    else:
        print(f"Pepper (lokal): {text}")

# CommandService mit SSHService verknüpfen
commandService = CommandService(ssh_service=sshService)
commandService.register_smalltalk_handler(lambda text: geminiService.generate_response(text))
print("CommandService bereit.")

intent_functions = {
    name: IntentFunction(
        description=meta["description"],
        handler=meta["handler"],
    )
    for name, meta in commandService.get_intent_functions().items()
}

qwen_model_path = "models/qwen2_5-0_5b_instruct"
intentRouter = IntentRouterService(
    model_path=qwen_model_path,
    functions=intent_functions,
    device="cpu",
)
print("IntentRouter bereit.")

print("System bereit. Kontinuierliche Aufnahme läuft (~10s Fenster). STRG+C zum Beenden.")
if sshService:
    # Confirm successful setup via Pepper's speech interface.
    sshService.execute_talk("Die Verbindung steht.")
else:
    print("Hinweis: Kein SSHService aktiv, daher keine Sprachbestätigung.")
buffer = deque()
target_samples = 10 * voskService.sample_rate
total_samples = 0
chunk_seconds = 0.5
recognizer = voskService.create_recognizer()
command_texts = deque(maxlen=8)
wake_window = deque(maxlen=4)
wake_phrase = "hey pepper"
listening_for_command = False

try:
    while True:
        chunk = voskService.record_chunk(seconds=chunk_seconds)
        buffer.append(chunk)
        total_samples += len(chunk)

        while total_samples > target_samples and buffer:
            removed = buffer.popleft()
            total_samples -= len(removed)

        pcm_chunk = voskService.audio_to_pcm(chunk)
        accepted = recognizer.AcceptWaveform(pcm_chunk)

        if accepted:
            final_text = voskService._decode_result(recognizer.Result())
            if final_text:
                final_text = final_text.strip()
                if not final_text:
                    continue

                if listening_for_command:
                    command_texts.append(final_text)
                    transcript_view = " ".join(command_texts).strip()
                else:
                    wake_window.append(final_text)
                    transcript_view = " ".join(wake_window).strip()

                print(f"[Transkript] {transcript_view}")

                if not listening_for_command:
                    window_lower = transcript_view.lower()
                    if wake_phrase in window_lower:
                        listening_for_command = True
                        command_texts.clear()
                        wake_window.clear()
                        after_idx = window_lower.rfind(wake_phrase) + len(wake_phrase)
                        remaining_text = transcript_view[after_idx:].strip()
                        if remaining_text:
                            command_texts.append(remaining_text)
                        print("Aktivierungsphrase 'hey pepper' erkannt. Befehl wird aufgenommen …")
                        speak_async("Wie kann ich helfen?")
                    else:
                        continue

                command_input = " ".join(command_texts).strip()
                if not command_input:
                    continue

                print("Intent wird bestimmt …")
                speak_async("Eine Sekunde, da muss ich kurz überlegen.")
                intent_name = intentRouter.predict_intent(command_input)
                if intent_name in ("dance", "sing"):
                    matched_command = commandService.check_command(command_input)
                    expected = "TANZEN" if intent_name == "dance" else "SINGEN"
                    if matched_command != expected:
                        print(
                            "Intent scheint unsicher (keine passende Sprachregel) – fallback zu Smalltalk."
                        )
                        intent_name = None
                intent_name = intent_name or "smalltalk"
                print(f"Intent erkannt: {intent_name}")
                response_text = intentRouter.execute(intent_name, command_input)

                if response_text:
                    print(f"Pepper sagt: {response_text}")
                    # Nur für Intents, die NICHT bereits im CommandService sprechen,
                    # den SSH-Talk hier ausführen.
                    if sshService and intent_name == "smalltalk":
                        sshService.execute_talk(response_text)
                else:
                    print("Intent hatte keine Antwort zurückgegeben.")
                buffer.clear()
                total_samples = 0
                command_texts.clear()
                wake_window.clear()
                listening_for_command = False
                recognizer = voskService.create_recognizer()
        else:
            partial_text = voskService._decode_partial(recognizer.PartialResult())
            if partial_text:
                print(f"[Partial] {partial_text}")
except KeyboardInterrupt:
    print("\nAufnahme beendet.")
