""" Агент на основе ИИ, который отвечает на вопросы пользователей """
from base import BaseAI
from main.utils.AI.SubjectStrategies import *
from main.utils.AI.TaskStrategies import *


class Assistant(BaseAI):
    """ Удобная конструкция для реализации вышеупомянутой задачи """

    def __init__(self):
        super().__init__()

        self.subject_strategies = {
            "math": MathStrategy(),
            "physics": PhysicsStrategy(),
            "literature": LiteratureStrategy(),
            "programming": ProgrammingStrategy(),
            "history": HistoryStrategy(),
            "geography": GeographyStrategy(),
            "biology": BiologyStrategy(),
            "chemistry": ChemistryStrategy(),
            "social_study": SocialStudyStrategy(),
            "other": OtherStrategy(),
        }

        self.task_strategies = {
            "solve": SolveStrategy(),
            "explain": ExplainStrategy(),
            "verify": VerifyStrategy(),
            "generate": GenerateStrategy(),
            "analyze": AnalyzeStrategy(),
        }

        self.subject = 'other'
        self.task = 'analyze'

    def prepare(self, user_input: str) -> None:
        """ Обработка информации, необходимая для качественного ответа ИИ """

        subject_key, task_key = self.identifier.get_req_details(user_input)

        self.subject = self.subject_strategies.get(subject_key)
        self.task = self.task_strategies.get(task_key)

        system_prompt = self.subject.get_system_prompt()
        user_prompt = self.task.get_user_prompt(user_input)
        self.prompt = self.make_prompt(user_prompt, system_prompt)

    def ask(self, user_input: str) -> dict:
        self.prepare(user_input)
        self.generate()
        return self.return_answer()


a = Assistant()
print(a.ask("2+2=?"))