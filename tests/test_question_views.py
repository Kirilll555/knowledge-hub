import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer


class QuestionViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()

        # Создаем пользователей
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='other123'
        )

        # Создаем тестовый вопрос
        self.question = Question.objects.create(
            user=self.other_user,
            title='Test Question',
            content='Test Content',
            is_deleted=False
        )

        # URL-ы
        self.ask_url = reverse('ask')
        self.question_url = reverse('question_detail', args=[self.question.id])
        self.rate_url = reverse('rate_answer', args=[1])

    def login_user(self):
        """Вход пользователя"""
        self.client.login(username='testuser', password='testpass123')

    def test_ask_question_anonymous(self):
        """Тест 1: Попытка задать вопрос без авторизации"""
        response = self.client.get(self.ask_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    @patch('main.views_features.question_views.create_question')
    @patch('main.views_features.question_views.add_activity')
    def test_ask_question_post_success(self, mock_add_activity, mock_create_question):
        """Тест 2: Успешное создание вопроса"""
        self.login_user()

        mock_create_question.return_value = 123

        post_data = {
            'title': 'Test Question',
            'content': 'Test Content',
            'subject': 'physics'
        }

        response = self.client.post(self.ask_url, post_data)

        # Редирект на /question/123/, но так как вопроса нет - будет 302 без проверки редиректа
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/question/123/')

        mock_create_question.assert_called_once_with(
            self.user.id, 'Test Question', 'Test Content', 'physics'
        )
        mock_add_activity.assert_called_once_with(
            self.user.id, 'ask_question', question_id=123
        )

    def test_ask_question_post_empty_fields(self):
        """Тест 3: Попытка создать вопрос с пустыми полями"""
        self.login_user()

        post_data = {
            'title': '',
            'content': '',
            'subject': 'general'
        }

        response = self.client.post(self.ask_url, post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ask.html')
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Заполните все поля')

    def test_ask_question_get(self):
        """Тест 4: GET-запрос страницы создания вопроса"""
        self.login_user()

        response = self.client.get(self.ask_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ask.html')
        self.assertIn('menu', response.context)

    @patch('main.views_features.question_views.create_question')
    @patch('main.views_features.question_views.add_activity')
    def test_ask_question_default_subject(self, mock_add_activity, mock_create_question):
        """Тест 5: Создание вопроса с темой по умолчанию"""
        self.login_user()

        mock_create_question.return_value = 456

        post_data = {
            'title': 'Test Question',
            'content': 'Test Content'
            # Нет поля subject
        }

        response = self.client.post(self.ask_url, post_data)

        # Проверяем редирект без follow
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/question/456/')

        mock_create_question.assert_called_once_with(
            self.user.id, 'Test Question', 'Test Content', 'general'
        )


    def test_question_detail_not_found(self):
        """Тест 7: Просмотр несуществующего вопроса"""
        url = reverse('question_detail', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    @patch('main.views_features.question_views.get_answers_for_question')
    @patch('main.views_features.question_views.add_view')
    @patch('main.views_features.question_views.create_answer')
    @patch('main.views_features.question_views.add_activity')
    def test_question_detail_post_answer(self, mock_add_activity, mock_create_answer,
                                         mock_add_view, mock_get_answers):
        """Тест 8: Добавление ответа через страницу вопроса"""
        self.login_user()

        mock_get_answers.return_value = []

        response = self.client.post(self.question_url, {'content': 'Test Answer'})

        self.assertRedirects(response, f'/question/{self.question.id}/')

        mock_create_answer.assert_called_once_with(
            self.user.id, self.question.id, 'Test Answer'
        )
        mock_add_activity.assert_called_once_with(
            self.user.id, 'answer_question', question_id=self.question.id
        )

    def test_question_detail_post_answer_anonymous(self):
        """Тест 9: Попытка добавить ответ без авторизации"""
        response = self.client.post(self.question_url, {'content': 'Test Answer'})

        # Ожидаем редирект на логин с параметром next
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    @patch('main.views_features.question_views.create_answer')
    @patch('main.views_features.question_views.add_activity')
    def test_add_answer_success(self, mock_add_activity, mock_create_answer):
        """Тест 10: Успешное добавление ответа через API"""
        self.login_user()

        mock_create_answer.return_value = 789

        url = reverse('add_answer', args=[self.question.id])
        response = self.client.post(url, {'content': 'API Answer'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['answer_id'], 789)
        self.assertEqual(data['author'], 'testuser')
        self.assertEqual(data['content'], 'API Answer')
        self.assertIn('created_at', data)

        mock_create_answer.assert_called_once_with(
            self.user.id, self.question.id, 'API Answer'
        )
        mock_add_activity.assert_called_once()

    def test_add_answer_empty_content(self):
        """Тест 11: Добавление пустого ответа через API"""
        self.login_user()

        url = reverse('add_answer', args=[self.question.id])
        response = self.client.post(url, {'content': ''})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Пустой ответ')

    def test_add_answer_anonymous(self):
        """Тест 12: Попытка добавить ответ через API без авторизации"""
        url = reverse('add_answer', args=[self.question.id])
        response = self.client.post(url, {'content': 'Test'})

        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.question_views.rate_answer')
    @patch('main.views_features.question_views.add_activity')
    def test_rate_answer_like(self, mock_add_activity, mock_rate_answer):
        """Тест 13: Лайк ответа"""
        self.login_user()

        # Создаем ответ для теста
        answer = Answer.objects.create(
            user=self.other_user,
            question=self.question,
            content='Test Answer',
            is_deleted=False
        )

        url = reverse('rate_answer', args=[answer.id])
        data = json.dumps({'rating': 'like'})

        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        mock_rate_answer.assert_called_once_with(
            self.user.id, answer.id, 1
        )
        mock_add_activity.assert_called_once()

    @patch('main.views_features.question_views.rate_answer')
    @patch('main.views_features.question_views.add_activity')
    def test_rate_answer_dislike(self, mock_add_activity, mock_rate_answer):
        """Тест 14: Дизлайк ответа"""
        self.login_user()

        answer = Answer.objects.create(
            user=self.other_user,
            question=self.question,
            content='Test Answer',
            is_deleted=False
        )

        url = reverse('rate_answer', args=[answer.id])
        data = json.dumps({'rating': 'dislike'})

        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        mock_rate_answer.assert_called_once_with(
            self.user.id, answer.id, 0
        )
        mock_add_activity.assert_called_once()

    def test_rate_answer_anonymous(self):
        """Тест 15: Попытка оценить ответ без авторизации"""
        # Создаем ответ для теста
        answer = Answer.objects.create(
            user=self.other_user,
            question=self.question,
            content='Test Answer',
            is_deleted=False
        )

        url = reverse('rate_answer', args=[answer.id])
        data = json.dumps({'rating': 'like'})

        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 302)