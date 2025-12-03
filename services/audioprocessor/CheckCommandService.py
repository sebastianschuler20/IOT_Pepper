import re
from typing import Callable, Dict


class CommandService:
    def __init__(self):
        # \b bedeutet Wortgrenze (damit "Stanzmaschine" nicht als "tanz" erkannt wird)
        # r"^..." bedeutet: Der Match MUSS am Anfang des Strings beginnen.
        # (?:...)? ist eine "non-capturing group" (optional), wir gruppieren damit Wörter.

        self.commands = {
            "TANZEN": [
                # Passt auf: "tanz", "tanzen"
                # Passt auf: "pepper tanz", "pepper tanzen"
                # Passt auf: "pepper kannst du tanzen"
                # IGNORIERT: "Erzähl mir von einem Tanz" (weil "Tanz" nicht am Anfang/nach Pepper steht)
                r"^(?:pepper\s+)?(?:kannst du\s+)?tan(z|zen|zt|ze)\b"
            ],

            "SINGEN": [
                # Passt auf: "sing", "singen", "sing mal"
                # Passt auf: "pepper sing ein lied"
                r"^(?:pepper\s+)?(?:kannst du\s+)?sing(en|t|e)?\b",
                r"^(?:pepper\s+)?lied\b"  # Falls jemand nur "Lied" oder "Pepper Lied" sagt
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

    def get_intent_functions(self) -> Dict[str, Dict[str, Callable[[str], str]]]:
        """
        Returns the available intent functions with descriptions and handlers.
        """
        return self.intent_functions

    def check_command(self, text: str):
        if not text:
            return None

        text_lower = text.lower()
        # 1. String Cleaning: Sicherstellen, dass "pepper" immer ein Leerzeichen hat
        #    und ganz am Anfang keine unnötigen Leerzeichen sind (.strip())
        text_lower = text_lower.replace("pepper", "pepper ").strip()

        # WICHTIG: Doppelte Leerzeichen entfernen, sonst greift der Regex manchmal nicht
        text_lower = re.sub(r'\s+', ' ', text_lower)

        for command_type, patterns in self.commands.items():
            for pattern in patterns:
                # Wir nutzen hier re.search, aber durch das "^" im Pattern
                # verhält es sich wie ein "Beginnt mit..."-Check.
                if re.search(pattern, text_lower):
                    return command_type

        return None

    def execute_command(self, command_type: str):
        """
        Führt die eigentliche Roboter-Logik aus.
        """
        if command_type == "TANZEN":
            return self.dance_action()

        elif command_type == "SINGEN":
            return self.sing_action()

        return None

    def dance_action(self) -> str:
        """
        Placeholder for dance action logic.
        """
        print("🤖 ROBOTER AKTION: Ich tanze jetzt! 💃")
        return "Ich tanze jetzt! 💃"

    def sing_action(self) -> str:
        """
        Placeholder for singing logic.
        """
        print("🤖 ROBOTER AKTION: La la laaaa! 🎵")
        return "La la laaaa! 🎵"
