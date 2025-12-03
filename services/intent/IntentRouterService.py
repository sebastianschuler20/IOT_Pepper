import json
import os
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class IntentFunction:
    description: str
    handler: Callable[[str], str]


class IntentRouterService:
    """
    Routes user text to functions using a local Qwen2.5-0.5B-Instruct model.
    The model folder must exist inside the workspace; downloads are not attempted.
    """

    def __init__(
        self,
        model_path: str,
        functions: Dict[str, IntentFunction],
        device: str = "cpu",
        max_new_tokens: int = 32,
    ):
        if not os.path.isdir(model_path):
            raise FileNotFoundError(
                f"Qwen model not found at {model_path}. "
                "Place the model weights in the workspace and update the path."
            )

        self.functions = functions
        self.device = device
        self.max_new_tokens = max_new_tokens

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            torch_dtype=torch.float32 if device == "cpu" else torch.float16,
        ).to(device)

    def _build_messages(self, user_text: str) -> list:
        function_lines = [
            f"- {name}: {meta.description}" for name, meta in self.functions.items()
        ]
        functions_block = "\n".join(function_lines)

        system_prompt = (
            "Du bist ein Intent-Router. "
            "Wähle die passende Funktion aus der Liste. "
            "Antwortformat: Gib nur ein JSON-Objekt wie "
            '{"function": "<funktionsname>"} zurück. '
            "Verwende ausschließlich Funktionsnamen aus der Liste. "
            "Wenn nichts passt, nutze \"none\"."
            "\n\nVerfügbare Funktionen:\n"
            f"{functions_block}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]

    def predict_intent(self, text: str) -> Optional[str]:
        """
        Returns the chosen function name or None.
        """
        if not text:
            return None

        messages = self._build_messages(text)
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True,
        ).to(self.device)

        output_ids = self.model.generate(
            input_ids,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated_ids = output_ids[0][input_ids.shape[-1]:]
        raw_output = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        ).strip()

        # Try strict JSON parsing first.
        func_name = self._extract_function_name(raw_output)
        if func_name and func_name in self.functions:
            return func_name

        return None

    def _extract_function_name(self, raw_output: str) -> Optional[str]:
        try:
            data = json.loads(raw_output)
            if isinstance(data, dict):
                name = data.get("function")
                if isinstance(name, str):
                    return name.strip()
        except json.JSONDecodeError:
            start = raw_output.find("{")
            end = raw_output.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    data = json.loads(raw_output[start : end + 1])
                    if isinstance(data, dict):
                        name = data.get("function")
                        if isinstance(name, str):
                            return name.strip()
                except json.JSONDecodeError:
                    pass

        return None

    def execute(self, function_name: Optional[str], text: str) -> Optional[str]:
        """
        Executes the mapped handler and returns its result text (if any).
        """
        if not function_name or function_name not in self.functions:
            return None

        handler = self.functions[function_name].handler
        return handler(text)
