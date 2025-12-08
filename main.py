from services.audioprocessor.CheckCommandService import CommandService
from services.audioprocessor.VoskServiceImpl import VoskServiceImpl
from services.chatbot.GeminiServiceImpl import GeminiServiceImpl
from services.intent.IntentRouterService import IntentFunction, IntentRouterService
from services.sshservice.SSHService import SSHService
import numpy as np
from collections import deque

print("Initialisiere Services...")
vosk_model_path = "models/vosk-model-small-de-0.15"
voskService = VoskServiceImpl(model_path=vosk_model_path, chunk_sec=0.25, sample_rate=16000)
print("VoskService bereit.")

geminiService = GeminiServiceImpl()
print("GeminiService bereit.")

commandService = CommandService()
print("CommandService bereit.")

intent_functions = {
    name: IntentFunction(
        description=meta["description"],
        handler=meta["handler"],
    )
    for name, meta in commandService.get_intent_functions().items()
}
intent_functions["smalltalk"] = IntentFunction(
    description="Beantworte allgemeine Fragen oder führe Smalltalk.",
    handler=lambda text: geminiService.generate_response(text),
)

qwen_model_path = "models/qwen2_5-0_5b_instruct"
intentRouter = IntentRouterService(
    model_path=qwen_model_path,
    functions=intent_functions,
    device="cpu",
)
print("IntentRouter bereit.")

ssh_host = "HIER_IP_EINFUEGEN"
sshService = None
if ssh_host == "HIER_IP_EINFUEGEN":
    print("SSHService NICHT gestartet: keine IP hinterlegt und aktuell kein Zugriff auf das Gerät.")
else:
    sshService = SSHService(host=ssh_host, username="nao", password="nao", key_filename=None)
    sshService.connect()
    print(f"SSHService bereit für Host {ssh_host}.")

print("System bereit. Kontinuierliche Aufnahme läuft (~10s Fenster). STRG+C zum Beenden.")
buffer = deque()
target_samples = 10 * voskService.sample_rate
total_samples = 0
chunk_seconds = 0.5
recognizer = voskService.create_recognizer()
recent_texts = deque(maxlen=8)  # hält die letzten Result-Fragmente

try:
    while True:
        chunk = voskService.record_chunk(seconds=chunk_seconds)
        buffer.append(chunk)
        total_samples += len(chunk)

        # Älteste Audiodaten verwerfen, bis wir grob 10s behalten
        while total_samples > target_samples and buffer:
            removed = buffer.popleft()
            total_samples -= len(removed)

        # Streaming-Transkription Chunk für Chunk
        pcm_chunk = voskService.audio_to_pcm(chunk)
        accepted = recognizer.AcceptWaveform(pcm_chunk)

        if accepted:
            final_text = voskService._decode_result(recognizer.Result())
            if final_text:
                recent_texts.append(final_text)
                combined = " ".join(recent_texts).strip()
                print(f"[Transkript] {combined}")
                if "pepper" in combined.lower():
                    print("Keyword 'pepper' erkannt. Intent wird bestimmt …")
                    intent_name = intentRouter.predict_intent(combined)
                    if intent_name:
                        print(f"Intent erkannt: {intent_name}")
                        response_text = intentRouter.execute(intent_name, combined)
                        if response_text:
                            print(f"Pepper sagt: {response_text}")
                            sshService.execute_talk(response_text)
                        else:
                            print("Intent hatte keine Antwort zurückgegeben.")
                    else:
                        print("Kein Intent erkannt, fallback zu Gemini …")
                        response = geminiService.generate_response(combined)
                        print(response)
                        sshService.execute_talk(response)
                    # Reset für nächste Aktivierung
                    buffer.clear()
                    total_samples = 0
                    recent_texts.clear()
                    recognizer = voskService.create_recognizer()
        else:
            partial_text = voskService._decode_partial(recognizer.PartialResult())
            if partial_text:
                print(f"[Partial] {partial_text}")
except KeyboardInterrupt:
    print("\nAufnahme beendet.")
