from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from unittest.mock import MagicMock
from datetime import datetime
from main.views_features.ban_views import banned_page


class BanViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()
        self.factory = RequestFactory()

        # Создаем пользователя с замоканным профилем
        self.user = MagicMock(spec=User)
        self.user.is_authenticated = True

        # Создаем замоканный профиль с данными о бане
        self.mock_profile = MagicMock()
        self.mock_profile.ban_reason = 'Spam and inappropriate behavior'
        self.mock_profile.banned_at = datetime(2024, 1, 1, 12, 0, 0)
        self.mock_profile.banned_until = datetime(2024, 12, 31, 23, 59, 59)

        # Привязываем профиль к пользователю
        self.user.profile = self.mock_profile

    def test_banned_page_authenticated_user(self):
        """Тест 1: Проверка страницы бана для авторизованного пользователя"""
        request = self.factory.get('/banned/')
        request.user = self.user

        response = banned_page(request)

        self.assertEqual(response.status_code, 200)
        # Проверяем содержимое ответа
        content = response.content.decode('utf-8')
        self.assertIn('Spam and inappropriate behavior', content)
        self.assertIn('2024', content)  # Проверяем наличие даты в ответе

    def test_banned_page_anonymous_user(self):
        """Тест 2: Проверка редиректа для неавторизованного пользователя"""
        request = self.factory.get('/banned/')
        request.user = AnonymousUser()

        response = banned_page(request)

        # Ожидаем редирект на страницу логина
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_banned_page_different_ban_reasons(self):
        """Тест 3: Проверка различных причин бана"""
        ban_reasons = [
            'Spam',
            'Harassment',
            'Inappropriate content',
            'Multiple violations of terms of service',
            'Account under investigation'
        ]

        for reason in ban_reasons:
            self.mock_profile.ban_reason = reason

            request = self.factory.get('/banned/')
            request.user = self.user

            response = banned_page(request)
            content = response.content.decode('utf-8')
            self.assertIn(reason, content)

    def test_banned_page_permanent_ban(self):
        """Тест 4: Проверка страницы для перманентного бана"""
        self.mock_profile.ban_reason = 'Permanent ban for severe violations'
        self.mock_profile.banned_at = datetime(2024, 1, 1, 0, 0, 0)
        self.mock_profile.banned_until = datetime(2099, 12, 31, 23, 59, 59)

        request = self.factory.get('/banned/')
        request.user = self.user

        response = banned_page(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Permanent ban for severe violations', content)
        self.assertIn('2099', content)

    def test_banned_page_temporary_ban(self):
        """Тест 5: Проверка страницы для временного бана"""
        ban_start = datetime(2024, 6, 1, 10, 0, 0)
        ban_end = datetime(2024, 6, 8, 10, 0, 0)

        self.mock_profile.ban_reason = 'Temporary ban for 7 days'
        self.mock_profile.banned_at = ban_start
        self.mock_profile.banned_until = ban_end

        request = self.factory.get('/banned/')
        request.user = self.user

        response = banned_page(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Temporary ban for 7 days', content)