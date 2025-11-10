import os
import time
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
# response=client.models.list(config={'page_size': 5})
# print(response.page)

def generate_ai_content(prompt: str):
    retries = 2
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt == retries:
                raise
            time.sleep(2)

