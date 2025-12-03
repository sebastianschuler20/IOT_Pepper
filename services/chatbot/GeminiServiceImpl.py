from services.chatbot.ChatBotService import ChatbotService
import os
import time
from google import genai

class GeminiServiceImpl(ChatbotService):
    def __init__(self):
        self.client = genai.Client(api_key="AIzaSyCpT4JNgIPOGYat2Ajbg_GbXKn7wQS16_c")

    def generate_response(self, prompt: str):
        retries = 2
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                if attempt == retries:
                    raise
                time.sleep(2)
                return "Exception gefangen"
