from dotenv import load_dotenv
from openai import OpenAI
from main.utils.AI.Ident import Identifier

load_dotenv()


class BaseAI:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        self.model = "arcee-ai/trinity-large-preview:free"
        self.identifier = Identifier(self.client, self.model)

    def generate(self, prompt: str, system_prompt: str) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7
            )

            answer = response.choices[0].message.content

            if self.identifier.check_answer(answer, f"{system_prompt}\n\n{prompt}"):
                return {
                    "success": True,
                    "answer": answer,
                }
            else:
                return {
                    "success": False,
                    "error": answer,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
