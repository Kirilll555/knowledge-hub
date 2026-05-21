import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer, AnswerRating


class IndexViewTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()
        self.index_url = reverse('index')

        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Создаем другого пользователя для тестов
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='other123'
        )


    @patch('main.views_features.main_views.get_profile')
    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_user_with_questions(self, mock_get_recent, mock_get_profile):
        """Тест 3: Проверка счетчика вопросов пользователя"""
        self.client.login(username='testuser', password='testpass123')

        # Создаем несколько вопросов для пользователя
        for i in range(5):
            Question.objects.create(
                user=self.user,
                title=f'Test Question {i}',
                content=f'Content {i}',
                is_deleted=False
            )

        Question.objects.create(
            user=self.user,
            title='Deleted Question',
            content='Deleted',
            is_deleted=True
        )

        mock_get_recent.return_value = []
        mock_get_profile.return_value = {'nickname': 'TestUser'}

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_count'], 6)

    @patch('main.views_features.main_views.get_profile')
    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_user_with_answers(self, mock_get_recent, mock_get_profile):
        """Тест 4: Проверка счетчика ответов пользователя"""
        self.client.login(username='testuser', password='testpass123')

        # Создаем вопрос
        question = Question.objects.create(
            user=self.other_user,
            title='Test Question',
            content='Content',
            is_deleted=False
        )

        # Создаем ответы для пользователя
        for i in range(3):
            Answer.objects.create(
                user=self.user,
                question=question,
                content=f'Answer {i}',
                is_deleted=False
            )

        # Создаем удаленный ответ (не должен учитываться)
        Answer.objects.create(
            user=self.user,
            question=question,
            content='Deleted Answer',
            is_deleted=True
        )

        mock_get_recent.return_value = []
        mock_get_profile.return_value = {'nickname': 'TestUser'}

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['answers_count'], 4)


    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_page_title(self, mock_get_recent):
        """Тест 7: Проверка заголовка страницы"""
        mock_get_recent.return_value = []

        response = self.client.get(self.index_url)

        # Проверяем наличие заголовка в HTML
        self.assertContains(response, 'Knowledge Hub')

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_menu_in_context(self, mock_get_recent):
        """Тест 8: Проверка наличия меню в контексте"""
        mock_get_recent.return_value = []

        response = self.client.get(self.index_url)

        self.assertIn('menu', response.context)
        self.assertIsInstance(response.context['menu'], list)
        self.assertGreater(len(response.context['menu']), 0)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_with_no_questions(self, mock_get_recent):
        """Тест 9: Проверка главной страницы без вопросов"""
        mock_get_recent.return_value = []

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['questions']), 0)

    @patch('main.views_features.main_views.get_profile')
    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_user_with_no_activity(self, mock_get_recent, mock_get_profile):
        """Тест 12: Проверка пользователя без активности"""
        self.client.login(username='testuser', password='testpass123')

        mock_get_recent.return_value = []
        mock_get_profile.return_value = {
            'nickname': 'NewUser',
            'age': None,
            'hobby': '',
            'main_subject': 'general',
            'role': 'user'
        }

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['questions_count'], 0)
        self.assertEqual(response.context['answers_count'], 0)
        self.assertEqual(response.context['ratings_received'], 0)

    @patch('main.views_features.main_views.get_profile')
    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_template_used(self, mock_get_recent, mock_get_profile):
        """Тест 13: Проверка использования правильного шаблона"""
        self.client.login(username='testuser', password='testpass123')

        mock_get_recent.return_value = []
        mock_get_profile.return_value = {'nickname': 'TestUser'}

        response = self.client.get(self.index_url)

        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Knowledge Hub')

    @patch('main.views_features.main_views.get_profile')
    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_view_multiple_users_activity(self, mock_get_recent, mock_get_profile):
        """Тест 14: Проверка разделения активности разных пользователей"""
        # Создаем активность для первого пользователя
        for i in range(3):
            Question.objects.create(
                user=self.user,
                title=f'User Question {i}',
                content=f'Content {i}',
                is_deleted=False
            )

        # Создаем активность для другого пользователя
        for i in range(5):
            Question.objects.create(
                user=self.other_user,
                title=f'Other Question {i}',
                content=f'Content {i}',
                is_deleted=False
            )

        self.client.login(username='testuser', password='testpass123')

        mock_get_recent.return_value = []
        mock_get_profile.return_value = {'nickname': 'TestUser'}

        response = self.client.get(self.index_url)

        # Проверяем, что считаются только вопросы текущего пользователя
        self.assertEqual(response.context['questions_count'], 3)