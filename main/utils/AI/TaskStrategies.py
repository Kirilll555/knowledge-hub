from abc import ABC, abstractmethod


class TaskTypeStrategy(ABC):
    @abstractmethod
    def get_user_prompt(self, user_input: str) -> str:
        pass

    @abstractmethod
    def get_task_name(self) -> str:
        pass


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
