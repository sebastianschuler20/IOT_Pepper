import re
from typing import Callable, Dict, Optional

from services.sshservice.SSHService import SSHService  # <--- neu


class CommandService:
    def __init__(self, ssh_service: Optional[SSHService] = None):
        # Referenz auf SSHService (kann None sein, z.B. für lokale Tests)
        self.ssh_service = ssh_service

        self.commands = {
            "TANZEN": [
                r"^(?:pepper\s+)?(?:kannst du\s+)?tan(z|zen|zt|ze)\b"
            ],
            "SINGEN": [
                r"^(?:pepper\s+)?(?:kannst du\s+)?sing(en|t|e)?\b",
                r"^(?:pepper\s+)?lied\b"
            ],
        }

        self.intent_functions: Dict[str, Dict[str, Callable[[str], str]]] = {
            "dance": {
                "description": "Lässt Pepper tanzen.",
                "handler": lambda _: self.dance_action(),
            },
            "sing": {
                "description": "Lässt Pepper ein Lied singen.",
                "handler": lambda _: self.sing_action(),
            },
        }

    def set_ssh_service(self, ssh_service: SSHService) -> None:
        """
        Kann aufgerufen werden, nachdem der SSHService aufgebaut wurde.
        """
        self.ssh_service = ssh_service

    def get_intent_functions(self) -> Dict[str, Dict[str, Callable[[str], str]]]:
        return self.intent_functions

    def check_command(self, text: str):
        if not text:
            return None

        text_lower = text.lower()
        text_lower = text_lower.replace("pepper", "pepper ").strip()
        text_lower = re.sub(r'\s+', ' ', text_lower)

        for command_type, patterns in self.commands.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return command_type

        return None

    def execute_command(self, command_type: str):
        if command_type == "TANZEN":
            return self.dance_action()
        elif command_type == "SINGEN":
            return self.sing_action()
        return None

    def dance_action(self) -> str:
        """
        Lässt Pepper tanzen (über SSHService.execute_wave) und optional sprechen.
        """
        text = "Ich tanze jetzt!"
        print("🤖 ROBOTER AKTION: Ich tanze jetzt! 💃")

        if self.ssh_service:
            # optional: gleichzeitig sprechen
            self.ssh_service.execute_talk(text)
            # Bewegung
            self.ssh_service.execute_wave()
        else:
            print("[WARNUNG] Kein SSHService konfiguriert – Tanzen nur lokal geloggt.")

        # Text wird weitergegeben (für Logging o.Ä.)
        return text

    def sing_action(self) -> str:
        """
        Lässt Pepper ein Lied singen (über SSHService.execute_talk).
        """
        text = "La la laaaa!"
        print("🤖 ROBOTER AKTION: La la laaaa! 🎵")

        if self.ssh_service:
            self.ssh_service.execute_talk(text)
        else:
            print("[WARNUNG] Kein SSHService konfiguriert – Singen nur lokal geloggt.")

        return text
