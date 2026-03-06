from main.utils.AI.SubjectStrategies import *
from main.utils.AI.TaskStrategies import *
from main.utils.AI.Ident import Identifier
from main.utils.AI.Base import BaseAI


class Assistant:
    def __init__(self):
        self.client = BaseAI()
        self.model = "arcee-ai/trinity-large-preview:free"

        self.subject_strategies = {
            'math': MathStrategy(),
            'physics': PhysicsStrategy(),
            'literature': LiteratureStrategy(),
            'programming': ProgrammingStrategy(),
            'history': HistoryStrategy(),
            'geography': GeographyStrategy(),
            'biology': ByologyStrategy(),
            'chemistry': ChemistryStrategy(),
            'other': OtherStrategy(),
        }

        self.task_strategies = {
            'solve': SolveStrategy(),
            'explain': ExplainStrategy(),
            'verify': VerifyStrategy(),
            'generate': GenerateStrategy(),
            'analyze': AnalyzeStrategy(),
        }

    def ask(self, user_input: str) -> dict:
        try:
            subject_key, task_key = self.client.identifier.detect(user_input)

            subject = self.subject_strategies.get(subject_key)
            task = self.task_strategies.get(task_key)

            return self.client.generate(task.get_user_prompt(user_input), subject.get_system_prompt())

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

print(Assistant().ask("jnvnjvnjinjifnvg"))