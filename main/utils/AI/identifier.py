""" Классификация по ключевым словам текста, позволяющее уточнять ответ ИИ """
from keywords import subject_keywords, task_keywords, error_keywords


class Identifier:
    """ Удобная структура для решения поставленной выше задачи """
    def __init__(self):
        self.subject_keywords = subject_keywords
        self.task_keywords = task_keywords
        self.error_keywords = error_keywords

    def detect_subject(self, text: str) -> str:
        """ Определяет, к какому разделу относится вопрос по ключевым словам """

        subject = "other"

        max_matches = 0
        for subj, keywords in self.subject_keywords.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > max_matches:
                max_matches = count
                subject = subj

        return subject

    def detect_task(self, text: str) -> str:
        """ Определяет тип задачи по ключевым словам """

        task = "explain"

        max_matches_task = 0
        for t, keywords in self.task_keywords.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > max_matches_task:
                max_matches_task = count
                task = t

        return task

    def get_req_details(self, text: str) -> tuple:
        """ Возвращает требуемый ответ """

        text = text.lower()
        return self.detect_subject(text), self.detect_task(text)

    def check_answer(self, answer: str) -> bool:
        """ Проверяет, справилась ли ИИ с задачей """

        if not answer or len(answer.strip()) < 5:
            return False

        answer = answer.lower()
        if any(kw in answer for kw in self.error_keywords):
            return False

        return True
