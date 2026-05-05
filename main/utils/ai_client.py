import urllib
import httpx
from django.conf import settings


class AIClient:
    def __init__(self):
        self.base_url = settings.AI_SERVER_URL
        self.api_key = settings.AI_API_KEY

    def generate(self, prompt: str) -> dict:
        """ Делает запрос на сервер с ИИ """
        try:
            print(123213123)
            encoded_prompt = urllib.parse.quote(prompt)
            response = httpx.post(
                f"{self.base_url}/generate?api_key={self.api_key}&prompt={encoded_prompt}",
                timeout=120.0
            )

            return response.json()
        except Exception as e:
            print("OI", e)
            return {"success": False, "error": str(e)}

    def regenerate(self, question: str, old_answer: str) -> dict:
        """ Регенерация ответа """
        prompt = f"Вопрос: {question}\n\nПредыдущий неудачный ответ: {old_answer}\n\nДай лучший ответ."
        return self.generate(prompt)
