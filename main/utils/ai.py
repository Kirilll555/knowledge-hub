from openai import OpenAI
from abc import ABC, abstractmethod


class SubjectStrategy(ABC):
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def get_subject_name(self) -> str:
        pass


class TaskTypeStrategy(ABC):
    @abstractmethod
    def get_user_prompt(self, user_input: str) -> str:
        pass

    @abstractmethod
    def get_task_name(self) -> str:
        pass


class MathStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return ("Ты репетитор по математике. Если задача касается геометрии, то используй формат: Дано,Найти,Решение, "
                "а также не забывай указывать теорему/факт в скобках после утверждения, если это не совсем очевидно, "
                "либо это не подразумевается задачей. Не используй странные методы решения, если об этом не просят. "
                "ПО типу задач проанализируй, какие теоремы можно использовать, а какие - не стоит. Если же задача по "
                "алгебре, то не пропускай шаги решения, не заюывай указывать важные аспекты. При построении графиков "
                "не забудь упросить его, если нужно, напиать тип получившегося графика, а также точки. Если задают "
                "текстовые задачи, то не забывай объявлять переменные и объяснять, откуда берется уравнения. В обоих "
                "случаях стремись к тому, что это больше решение, нежели чем неструктурированное объяснение. Не "
                "забывай, что пропускать этапы решения нельзя, а также запрещено выдумывать что-либо")

    def get_subject_name(self) -> str:
        return "Математика"


class PhysicsStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return ("Ты учитель физики. Используй формат Дано,Найти,Решение, не забывай Записывать закон, по которому идет "
                "дальнейшее решение. Не бери формулы из воздуха, а также не пропускай шаги решения! Не забывай, "
                "что пропускать этапы решения нельзя, а также запрещено выдумывать что-либо. Стремись к тому, "
                "что это больше решение, нежели чем неструктурированное объяснение.")

    def get_subject_name(self) -> str:
        return "Физика"


class LiteratureStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return ("Ты репетитор по литературе. Не забывай про чувства и психологию героев, не опускай детали. "
                "ВЫДУМЫВАТЬ ПРОИЗВЕДЕНИЯ И ИХ СОДЕРЖАНИЯ И Т.Д. ИЗ ГОЛОВЫ ЗАПРЕЩАЕТСЯ!!! Если ты не знаешь содержание "
                "произведения, то ТАК И СКАЖИ!!!")

    def get_subject_name(self) -> str:
        return "Литература"


class ProgrammingStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return "Ты — программист. Объясняй код, рассказывай примеры, предупреждай об ошибках."

    def get_subject_name(self) -> str:
        return "Программирование"


class HistoryStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return "Ты — историк. Показывай связи событий, объясняй контекст."

    def get_subject_name(self) -> str:
        return "История"


class GeographyStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return "Ты учитель по географии."

    def get_subject_name(self) -> str:
        return "География"


class OtherSubjectStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return "Ты ИИ Ассистент, который помогает людям получить ответ на свой вопрос."

    def get_subject_name(self) -> str:
        return "Другое"


class SolveStrategy(TaskTypeStrategy):
    def get_user_prompt(self, user_input: str) -> str:
        return f"Реши задачу:\n{user_input}"

    def get_task_name(self) -> str:
        return "Решение"


class ExplainStrategy(TaskTypeStrategy):
    def get_user_prompt(self, user_input: str) -> str:
        return f"Объясни:\n{user_input}"

    def get_task_name(self) -> str:
        return "Объяснение"


class VerifyStrategy(TaskTypeStrategy):
    def get_user_prompt(self, user_input: str) -> str:
        return f"Проверь и найди ошибки:\n{user_input}"

    def get_task_name(self) -> str:
        return "Проверка"


class GenerateStrategy(TaskTypeStrategy):
    def get_user_prompt(self, user_input: str) -> str:
        return f"Создай/напиши:\n{user_input}"

    def get_task_name(self) -> str:
        return "Создание"


class AnalyzeStrategy(TaskTypeStrategy):
    def get_user_prompt(self, user_input: str) -> str:
        return (f"Проанализируй:\n{user_input}. Если не знаешь полного произведения, то скажи только известные факты, "
                f"а не выдумывай из головы!")

    def get_task_name(self) -> str:
        return "Анализ"


class SmartAssistant:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "arcee-ai/trinity-large-preview:free"

        self.subject_strategies = {
            'math': MathStrategy(),
            'physics': PhysicsStrategy(),
            'literature': LiteratureStrategy(),
            'programming': ProgrammingStrategy(),
            'history': HistoryStrategy(),
            'geography': GeographyStrategy(),
            'other': OtherSubjectStrategy(),
        }

        self.task_strategies = {
            'solve': SolveStrategy(),
            'explain': ExplainStrategy(),
            'verify': VerifyStrategy(),
            'generate': GenerateStrategy(),
            'analyze': AnalyzeStrategy(),
        }

    def detect(self, text: str) -> tuple[str, str]:
        prompt = f"""
        Из текста: "{text}"

        Определи:
        1. Предмет (одно слово): math, physics, literature, programming, history, geography, other
        2. Тип задачи (одно слово): solve, explain, verify, generate, analyze

        Ответь строго в формате: предмет|тип
        Пример: math|solve
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )

            result = response.choices[0].message.content.strip()
            subject, task_type = result.split('|')
            return subject.strip(), task_type.strip()

        except Exception:
            return 'other', 'explain'

    def check_answer(self, answer, question):
        prompt = f"""
            Из ответа ИИ-Агента: "{answer}" на вопрос {question}

            Определи: српавилась ли нейросеть с задачей, судя по ее ответу? На нужный ли вопрос она ответила?

            Ответь строго в формате: +/-, где + - все верно, а - - неверно
            Пример: +
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )

            result = response.choices[0].message.content.strip()
            return result

        except Exception:
            return "-"

    def ask(self, user_input: str) -> dict:
        try:
            subject_key, task_key = self.detect(user_input)

            subject = self.subject_strategies.get(subject_key)
            task = self.task_strategies.get(task_key)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": subject.get_system_prompt()},
                    {"role": "user", "content": task.get_user_prompt(user_input)}
                ],
                temperature=0.7
            )

            answer = response.choices[0].message.content

            if self.check_answer(answer, user_input) == "+":
                return {
                    'success': True,
                    'answer': answer,
                    'subject': subject.get_subject_name(),
                    'task': task.get_task_name()
                }
            else:
                return {
                    'success': False,
                    'error': answer
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class AssistantFactory:
    @staticmethod
    def create(api_key: str) -> SmartAssistant:
        return SmartAssistant(api_key)


def ask_ai(question):
    API_KEY = "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"
    assistant = AssistantFactory.create(API_KEY)

    result = assistant.ask(question)

    if result['success']:
        return {"success": True,
                "subject": result['subject'],
                "task": result['task'],
                "answer": result['answer'],
                }
    else:
        return {"success": False,
                "error": result['error'],
                }

print(ask_ai("Есть ли жизнь на Марсе?"))