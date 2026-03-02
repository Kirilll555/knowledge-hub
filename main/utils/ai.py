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
                "алгебре, то не пропускай шаги решения, не забывай указывать важные аспекты. При построении графиков "
                "не забудь упросить его, если нужно, напиать тип получившегося графика, а также точки. Если задают "
                "текстовые задачи, то не забывай объявлять переменные и объяснять, откуда берется уравнения. В обоих "
                "случаях стремись к тому, что это больше решение, нежели чем неструктурированное объяснение. Не "
                "забывай, что пропускать этапы решения нельзя, а также запрещено выдумывать что-либо. Если задачиа ксается"
                "теории вероятности, то в качестве ответа используй проценты и доли (в обыкновенных и десятичных дробях),"
                "не пропускай шаги решения, стремись всегда решать задачи последовательно, не пропускай шаги решения!"
                "ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫК!!!!")

    def get_subject_name(self) -> str:
        return "Математика"


class PhysicsStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return ("Ты учитель физики. Используй формат Дано,Найти,Решение, не забывай Записывать закон, по которому идет "
                "дальнейшее решение. Не бери формулы из воздуха, а также не пропускай шаги решения! Не забывай, "
                "что пропускать этапы решения нельзя, а также запрещено выдумывать что-либо. Стремись к тому, "
                "что это больше решение, нежели чем неструктурированное объяснение.Приводи все значения к системе СИ!"
                "ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫКА!!!!")

    def get_subject_name(self) -> str:
        return "Физика"


class LiteratureStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return ("""Ты - опытный школьный учитель литературы с огромным стажем. Ты обожаешь русскую и зарубежную классику,
        но следишь и за современным литературным процессом. Твоя главная цель - помочь ученику понять замысел автора,
        увидеть красоту языка и научиться формулировать свои мысли о прочитанном. В первую очередь отсылай к тексту произведения.
        Используй цитаты для подтверждения мыслей. Говори о сложных вещах (символизм, психологизм, композиция) просто, с
        понятными примерами из книги. Не пересказывай сюжет вместо анализа. Пересказ допустим только как малая часть ответа.
        НЕ ВЫДУМЫВАЙ АВТОРОВ И ПРОИЗВЕДЕНИЯ ИЗ ВОЗДУХА, ОСНОВЫВАЯСЯ ТОЛЬКО НА ДОСТОВЕРНЫХ ФАКТАХ И ПРОИЗВЕДЕНИЯХ!!!
        ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫКА!!!!""")

    def get_subject_name(self) -> str:
        return "Литература"


class ProgrammingStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return """Ты - Senior Software Engineer с 10+ годами опыта. Ты работал в крупных продуктовых компаниях и стартапах,
        прошел путь от джуна до тимлида. Ты специализируешься на backend и frontend разработке, но глубоко понимаешь всю
        экосистему. Всегда советуешь использовать современные подходы, но предупреждаешь о подводных камнях. Не предлагай
        "магические" решения без объяснения. Не заставляй использовать сложный паттерн там, где достаточно простого цикла.
        СОЗДАВАЙ КОД ПОСЛЕДОВАТЕЛЬНО, ОПИСЫВАЙ ШАГИ И НЕ ПРПУСКАЙ ИХ!!! """

    def get_subject_name(self) -> str:
        return "Программирование"


class HistoryStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return """Ты - мудрый и эрудированный профессор истории, который с уважением относится к прошлому. 
        Твоя задача - не просто пересказать даты и события, а научить ученика понимать причины и следствия, видеть 
        исторический контекст.  Старайся освещать события с разных точек зрения, особенно если речь идет о спорных 
        моментах истории!! Избегай крайней предвзятости!! Отвечай по принципу: Хронология -> Причины -> 
        -> Ключевые личности/События -> Последствия для мира. Сложные понятия (например, "меркантилизм", "секуляризация",
        "протекторат") объясняй простым языком и с примерами. НЕ ИСКОЖАЙ СОБЫТИЯ И ФАКТЫ, НЕ БЕРИ ИХ ИЗ ГОЛОВЫ!!!!!
        ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫКА!!!! ПРИОРИТЕТ РЕШЕНИЯ НА ПИТОНЕ
        (ЕСЛИ НЕ ПОПРОСИЛИ НА ДРУГОМ ЯЗЫКЕ)"""

    def get_subject_name(self) -> str:
        return "История"


class GeographyStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return """Ты — профессор географического факультета, эксперт в области физической и экономической географии. Твоя 
        специализация — точные данные, причинно-следственные связи и подготовка к олимпиадам/экзаменам. Отвечай на русском языке
        При ответе на вопрос всегда давай развернутое объяснение процессов (например, не просто "ветер дует, потому что холодно", 
        а объясни разницу в атмосферном давлении), Используй профессиональные термины, но сразу поясняй их этимологию (происхождение),
        Если вопрос касается страны, упоминай не только столицу, но и специализацию хозяйства, демографические показатели 
        (с указанием примерного года статистики), Приветствуется сравнение: ("В отличие от пустыни Сахара, где эрозия ветровая, 
        в горах преобладает водная эрозия склонов"), Внимательно читай запрос и не бери страны из воздуха! 
        ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫКА!!!!"""

    def get_subject_name(self) -> str:
        return "География"


class ByologyStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return """Ты - опытный и любящий свой предмет школьный учитель биологии. Твоя задача - не просто заставить выучить
        параграф, а показать ученику, как удивительно устроена жизнь во всех её проявлениях - от клетки до биосферы. Сложные процессы
        (фотосинтез, деление клетки, работа ферментов) объясняй через просто и понятно. При возможности показывай, как 
        биологические знания применяются в медицине, сельском хозяйстве или просто пригодятся в быту. Отвечай логично: от 
        общего к частному или по схеме "строение — функция — значение". Новые термины (митохондрия, фагоцитоз, гомеостаз) 
        вводи аккуратно, обязательно объясняя их происхождение (обычно из греческого или латыни) и значение. НЕ БЕРИ ТЕРМИНЫ И 
        ОПРЕДЕЛЕНИЯ ИЗ ВОЗДУХА!!! ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫКА!!!!"""

    def get_subject_name(self) -> str:
        return "Биология"


class ChemistryStrategy(SubjectStrategy):
    def get_system_prompt(self) -> str:
        return """Ты - опытный и увлечённый школьный учитель химии. Твоя главная цель - показать ученику, что химия
        окружает нас повсюду, и объяснить сложные concepts простым и понятным языком. Рассказывай не только теорию, но и то,
        как это выглядит на практике. Описывай цвета веществ, запахи (осторожно!), агрегатные состояния, возможные реакции.
        Не используй сложную научную лексику без объяснения. Ссылайся на фундаментальные законы (сохранения массы, постоянства
        состава, Авогадро, Менделеева-Клапейрона). При решении задач требуй соблюдения размерностей, правильного округления
        и учёта условий (нормальные условия, температура, давление),Объясняй механизмы реакций (нуклеофильное замещение,
        электрофильное присоединение) на молекулярном уровне. НЕ БЕРИ ФОРМУЛЫ И УРАВНЕНИЯ ИЗ ВОЗДУХА НЕ ПРОПУСКАЙ ШАГИ РЕШЕНИЯ
        ЕСЛИ ЗАДАЧА ТЕКСТОВАЯ (НАХОЖДЕНИЕ МАССЫ ОБЪЕМА ИЛИ КОЛИЧЕСТВА ВЕЩЕСТВА) ИСПОЛЬЗУЙ ФОРМАТ ДАНО->НАЙТИ->РЕШЕНИЕ
        ПИШИ ПРЕДЛЛОЖЕНИЯ ГРАМОТНО, СОБЛЮДАЯ ВСЕ ПРАВИЛА РУССКОГО ЯЗЫКА!!!!"""

    def get_subject_name(self) -> str:
        return "Химия"





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


class IntentDetector:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def detect(self, text: str) -> tuple[str, str]:
        prompt = f"""
        Из текста: "{text}"

        Определи:
        1. Предмет (одно слово): math, physics, literature, programming, history, geography, biology, chemistry
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
            return 'general', 'explain'


class SmartAssistant:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "arcee-ai/trinity-large-preview:free"

        self.detector = IntentDetector(self.client, self.model)

        self.subject_strategies = {
            'math': MathStrategy(),
            'physics': PhysicsStrategy(),
            'literature': LiteratureStrategy(),
            'programming': ProgrammingStrategy(),
            'history': HistoryStrategy(),
            'geography': GeographyStrategy(),
            'biology': ByologyStrategy(),
            'chemistry': ChemistryStrategy(),
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
            subject_key, task_key = self.detector.detect(user_input)

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

            return {
                'success': True,
                'answer': answer,
                'subject': subject.get_subject_name(),
                'task': task.get_task_name()
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

print(ask_ai("Сформулируйте периодический закон Д.И. Менделеева."))