import json
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User

from main.models_features.chat_feature import ChatSession, ChatMessage
from main.views_features.ai_views import (
    search_question,
    ask_ai,
    create_ai_session,
    delete_ai_session,
    rename_ai_session,
    regenerate_answer,
)


class AITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.login(username="testuser", password="testpass123")


class SearchQuestionTests(AITestCase):

    @patch("main.utils.ai_client.AIClient.generate")
    def test_search_question_post_with_session(self, mock_generate):
        """Тест POST-запроса с существующей сессией"""
        mock_generate.return_value = {"success": True, "answer": "Тестовый ответ"}

        session = ChatSession.objects.create(
            user_id=self.user.id, title="Тестовая сессия"
        )

        request = self.factory.post(
            "/search/",
            data=json.dumps({"question": "Тестовый вопрос", "session_id": session.id}),
            content_type="application/json",
        )
        request.user = self.user

        response = search_question(request)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["answer"], "Тестовый ответ")
        self.assertTrue(
            ChatMessage.objects.filter(
                session_id=session.id, role="assistant", content="Тестовый ответ"
            ).exists()
        )

    def test_search_question_get_authenticated(self):
        """Тест GET-запроса авторизованного пользователя с вопросом"""
        request = self.factory.get("/search/?q=Тестовый вопрос")
        request.user = self.user

        response = search_question(request)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context"):
            self.assertIn("question", response.context)
            self.assertEqual(response.context["question"], "Тестовый вопрос")
        else:
            content = response.content.decode("utf-8")
            self.assertIn("Тестовый вопрос", content)
        session = ChatSession.objects.filter(
            user_id=self.user.id, title="Тестовый вопрос"
        ).first()
        self.assertIsNotNone(session)
        self.assertTrue(
            ChatMessage.objects.filter(
                session_id=session.id, role="user", content="Тестовый вопрос"
            ).exists()
        )

    def test_search_question_get_unauthenticated(self):
        """Тест GET-запроса неавторизованного пользователя"""
        request = self.factory.get("/search/?q=Тестовый вопрос")
        request.user = AnonymousUser()
        self.assertFalse(request.user.is_authenticated)
        response = search_question(request)
        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context"):
            self.assertEqual(response.context["question"], "Тестовый вопрос")
            self.assertIsNone(response.context["session_id"])
        else:
            content = response.content.decode("utf-8")
            self.assertIn("Тестовый вопрос", content)
        self.assertEqual(ChatSession.objects.count(), 0)


class AskAITests(AITestCase):

    def setUp(self):
        super().setUp()
        self.session = ChatSession.objects.create(
            user_id=self.user.id, title="Тестовая сессия"
        )
        ChatMessage.objects.create(
            session_id=self.session.id, role="user", content="Предыдущий вопрос"
        )
        ChatMessage.objects.create(
            session_id=self.session.id, role="assistant", content="Предыдущий ответ"
        )

    @patch("main.utils.ai_client.AIClient.generate")
    def test_ask_ai_post_with_ajax_success(self, mock_generate):
        """Тест успешного AJAX POST-запроса"""
        mock_generate.return_value = {"success": True, "answer": "Новый ответ"}

        request = self.factory.post(
            f"/ask-ai/{self.session.id}/",
            data={"question": "Новый вопрос"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        request.user = self.user

        response = ask_ai(request, session_id=self.session.id)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["answer"], "Новый ответ")
        self.assertEqual(ChatMessage.objects.count(), 4)  # 2 старых + 2 новых


class SessionManagementTests(AITestCase):

    def setUp(self):
        super().setUp()
        self.session = ChatSession.objects.create(
            user_id=self.user.id, title="Тестовая сессия"
        )

    def test_create_ai_session(self):
        """Тест создания новой сессии"""
        request = self.factory.post("/create-session/")
        request.user = self.user

        response = create_ai_session(request)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertIsNotNone(response_data["session_id"])

        session = ChatSession.objects.get(id=response_data["session_id"])
        self.assertEqual(session.user_id, self.user.id)
        self.assertEqual(session.title, "Новый диалог")

    def test_delete_ai_session(self):
        """Тест удаления сессии"""
        session_to_delete = ChatSession.objects.create(
            user_id=self.user.id, title="Сессия для удаления"
        )

        request = self.factory.post(f"/delete-session/{session_to_delete.id}/")
        request.user = self.user

        response = delete_ai_session(request, session_to_delete.id)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertFalse(ChatSession.objects.filter(id=session_to_delete.id).exists())

    def test_delete_ai_session_wrong_user(self):
        """Тест попытки удаления чужой сессии"""
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        other_session = ChatSession.objects.create(
            user_id=other_user.id, title="Чужая сессия"
        )

        request = self.factory.post(f"/delete-session/{other_session.id}/")
        request.user = self.user

        response = delete_ai_session(request, other_session.id)
        response_data = json.loads(response.content)

        self.assertTrue(
            response_data["success"]
        )  # delete_session не выбрасывает ошибку
        self.assertTrue(ChatSession.objects.filter(id=other_session.id).exists())

    def test_rename_ai_session(self):
        """Тест переименования сессии"""
        request = self.factory.post(
            f"/rename-session/{self.session.id}/",
            data=json.dumps({"title": "Новое название"}),
            content_type="application/json",
        )
        request.user = self.user

        response = rename_ai_session(request, self.session.id)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])

        self.session.refresh_from_db()
        self.assertEqual(self.session.title, "Новое название")


class RegenerateAnswerTests(AITestCase):

    @patch("main.utils.ai_client.AIClient.regenerate")
    def test_regenerate_answer_success(self, mock_regenerate):
        """Тест успешной регенерации ответа"""
        mock_regenerate.return_value = {
            "success": True,
            "answer": "Перегенерированный ответ",
        }

        session = ChatSession.objects.create(
            user_id=self.user.id, title="Тестовая сессия"
        )
        ChatMessage.objects.create(
            session_id=session.id, role="assistant", content="Старый ответ"
        )

        request = self.factory.post(
            "/regenerate/",
            data=json.dumps(
                {
                    "question": "Тестовый вопрос",
                    "session_id": session.id,
                    "old_answer": "Старый ответ",
                }
            ),
            content_type="application/json",
        )

        response = regenerate_answer(request)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["answer"], "Перегенерированный ответ")
        self.assertFalse(
            ChatMessage.objects.filter(
                session_id=session.id, content="Старый ответ"
            ).exists()
        )
        self.assertTrue(
            ChatMessage.objects.filter(
                session_id=session.id, content="Перегенерированный ответ"
            ).exists()
        )