""" Основная работа (запросы и т.д.) ИИ """
from pathlib import Path
from llama_cpp import Llama
from main.utils.AI.identifier import Identifier


class BaseAI:
    """ Удобная конструкция для выполнения поставленной выше задачи """
    def __init__(self):
        models_dir = Path(__file__).parent / "models"
        gguf_files = list(models_dir.rglob("*.gguf"))

        if not gguf_files:
            raise FileNotFoundError("GGUF файл не найден. Запустите setup.py")

        model_path = str(gguf_files[0])

        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )

        self.identifier = Identifier()
        self.prompt = ""
        self.response = {}

    def make_prompt(self, prompt: str, system_prompt: str = "") -> str:
        """ Создает промпт в формате Qwen """

        if system_prompt:
            text = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        else:
            text = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        self.prompt = text
        return text

    def generate(self) -> None:
        """ Генерирует ответ """

        try:
            response = self.llm(
                self.prompt,
                max_tokens=512,
                temperature=0.7,
                echo=False
            )

            answer = response["choices"][0]["text"].strip()

            self.response = {
                "success": True,
                "answer": answer
            }

        except Exception as e:
            self.response = {
                "success": False,
                "error": f"Произошла ошибка при генерации ответа: {str(e)}"
            }

    def return_answer(self) -> dict:
        """ Возвращает итоговый ответ в виде словаря """

        if not self.response.get("success"):
            return {
                "success": False,
                "error": self.response.get("error", "Неизвестная ошибка")
            }

        if self.identifier.check_answer(self.response['answer']):
            return {
                "success": True,
                "answer": self.response['answer']
            }

        return {
            "success": False,
            "error": "Ответ не прошел проверку качества"
        }

    def run(self, prompt: str, system_prompt: str = "") -> dict:
        """ Главный метод для внешнего вызова """

        self.make_prompt(prompt, system_prompt)
        self.generate()
        return self.return_answer()
