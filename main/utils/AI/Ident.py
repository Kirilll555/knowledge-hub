class Identifier:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def detect(self, text: str) -> tuple[str, str]:
        prompt = f"""
        Из текста: "{text}"

        Определи:
        1. Предмет (одно слово): math, physics, literature, programming, history, geography, biology, chemistry, other
        2. Тип задачи (одно слово): solve, explain, verify, generate, analyze

        Ответь строго в формате: предмет|тип
        Пример: math|solve
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20,
            )

            result = response.choices[0].message.content.strip()
            subject, task_type = result.split("|")
            return subject.strip(), task_type.strip()

        except Exception:
            return "other", "explain"

    def check_answer(self, answer: str, question: str) -> bool:
        prompt = f"""
            Определи, справился ли ИИ-агент с вопросом: {question}, ответив {answer}"


            Ответь строго в формате: + (если справился); - (если не справился)
            Пример: +
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20,
            )

            result = response.choices[0].message.content.strip()
            return True if result == "+" else False

        except Exception:
            return False
