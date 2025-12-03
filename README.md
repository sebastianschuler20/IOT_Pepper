IOT: Pepper-Projekt

## Modelle lokal bereitstellen

- **Vosk (Speech-to-Text)**: Lade ein passendes Vosk-Sprachmodell (z. B. `vosk-model-small-de-0.15`), entpacke es und lege den Ordner unter `models/vosk` ab.
- **Qwen2.5-0.5B-Instruct (Intent-Routing)**: Lade das Modell von Hugging Face herunter, entpacke es und platziere es unter `models/qwen2_5-0_5b_instruct`. Die Dateien `config.json`, `tokenizer.json`, `model.safetensors` usw. müssen dort liegen.

Beide Modelle werden nur lokal geladen (`local_files_only=True`); es erfolgt kein Download zur Laufzeit.
