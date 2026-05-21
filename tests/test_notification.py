import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from datetime import datetime


class NotificationViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()

        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # URL-ы
        self.notifications_url = reverse('get_notifications')
        self.mark_read_url = reverse('mark_read', args=[1])
        self.mark_all_read_url = reverse('mark_all_read')

    def login_user(self):
        """Вход пользователя"""
        self.client.login(username='testuser', password='testpass123')

    @patch('main.views_features.notification_views.get_user_notifications')
    @patch('main.views_features.notification_views.get_unread_count')
    def test_get_notifications_success(self, mock_unread_count, mock_get_notifications):
        """Тест 1: Успешное получение уведомлений"""
        self.login_user()

        # Создаем мок-уведомления
        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.notification_type = 'system'
        mock_notification.title = 'Test Notification'
        mock_notification.message = 'Test message'
        mock_notification.link = '/test/'
        mock_notification.is_read = False
        mock_notification.created_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_get_notifications.return_value = [mock_notification]
        mock_unread_count.return_value = 1

        response = self.client.get(self.notifications_url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['unread_count'], 1)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['id'], 1)
        self.assertEqual(data['notifications'][0]['type'], 'system')
        self.assertEqual(data['notifications'][0]['title'], 'Test Notification')
        self.assertEqual(data['notifications'][0]['is_read'], False)
        self.assertEqual(data['notifications'][0]['created_at'], '01.01.2024 12:00')

        # Проверяем, что функции вызваны с правильными параметрами
        mock_get_notifications.assert_called_once_with(self.user.id, limit=20)
        mock_unread_count.assert_called_once_with(self.user.id)

    @patch('main.views_features.notification_views.get_user_notifications')
    @patch('main.views_features.notification_views.get_unread_count')
    def test_get_notifications_empty_list(self, mock_unread_count, mock_get_notifications):
        """Тест 2: Получение пустого списка уведомлений"""
        self.login_user()

        mock_get_notifications.return_value = []
        mock_unread_count.return_value = 0

        response = self.client.get(self.notifications_url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['unread_count'], 0)
        self.assertEqual(len(data['notifications']), 0)

    def test_get_notifications_unauthorized(self):
        """Тест 3: Попытка получения уведомлений без авторизации"""
        response = self.client.get(self.notifications_url)

        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.notification_views.get_user_notifications')
    @patch('main.views_features.notification_views.get_unread_count')
    def test_get_notifications_multiple_notifications(self, mock_unread_count, mock_get_notifications):
        """Тест 4: Получение нескольких уведомлений"""
        self.login_user()

        # Создаем несколько мок-уведомлений
        mock_notifications = []
        for i in range(5):
            mock_notification = MagicMock()
            mock_notification.id = i + 1
            mock_notification.notification_type = 'system'
            mock_notification.title = f'Notification {i + 1}'
            mock_notification.message = f'Message {i + 1}'
            mock_notification.link = f'/test/{i + 1}'
            mock_notification.is_read = i % 2 == 0  # Четные прочитаны
            mock_notification.created_at = datetime(2024, 1, 1, i, 0, 0)
            mock_notifications.append(mock_notification)

        mock_get_notifications.return_value = mock_notifications
        mock_unread_count.return_value = 2

        response = self.client.get(self.notifications_url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['unread_count'], 2)
        self.assertEqual(len(data['notifications']), 5)

        # Проверяем статусы прочтения
        read_statuses = [n['is_read'] for n in data['notifications']]
        self.assertEqual(read_statuses, [True, False, True, False, True])

    @patch('main.views_features.notification_views.get_user_notifications')
    @patch('main.views_features.notification_views.get_unread_count')
    def test_get_notifications_with_different_types(self, mock_unread_count, mock_get_notifications):
        """Тест 5: Получение уведомлений разных типов"""
        self.login_user()

        mock_notifications = []
        types = ['system', 'answer', 'rating', 'complaint']

        for i, ntype in enumerate(types):
            mock_notification = MagicMock()
            mock_notification.id = i + 1
            mock_notification.notification_type = ntype
            mock_notification.title = f'{ntype} Notification'
            mock_notification.message = f'{ntype} message'
            mock_notification.link = '/'
            mock_notification.is_read = False
            mock_notification.created_at = datetime.now()
            mock_notifications.append(mock_notification)

        mock_get_notifications.return_value = mock_notifications
        mock_unread_count.return_value = 4

        response = self.client.get(self.notifications_url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(len(data['notifications']), 4)

        # Проверяем типы уведомлений
        notification_types = [n['type'] for n in data['notifications']]
        self.assertEqual(notification_types, types)

    @patch('main.views_features.notification_views.mark_notification_as_read')
    def test_mark_read_success(self, mock_mark_read):
        """Тест 6: Успешная отметка уведомления как прочитанного"""
        self.login_user()

        response = self.client.post(self.mark_read_url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data['success'])

        mock_mark_read.assert_called_once_with(1)

    def test_mark_read_unauthorized(self):
        """Тест 7: Попытка отметки уведомления без авторизации"""
        response = self.client.post(self.mark_read_url)

        self.assertEqual(response.status_code, 302)

    def test_mark_read_invalid_method(self):
        """Тест 8: Неверный HTTP метод для отметки уведомления"""
        self.login_user()

        response = self.client.get(self.mark_read_url)

        self.assertEqual(response.status_code, 405)

        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Method not allowed')

    @patch('main.views_features.notification_views.mark_all_notifications_as_read')
    def test_mark_all_read_success(self, mock_mark_all):
        """Тест 9: Успешная отметка всех уведомлений как прочитанных"""
        self.login_user()

        response = self.client.post(self.mark_all_read_url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data['success'])

        mock_mark_all.assert_called_once_with(self.user.id)

    def test_mark_all_read_unauthorized(self):
        """Тест 10: Попытка отметки всех уведомлений без авторизации"""
        response = self.client.post(self.mark_all_read_url)

        self.assertEqual(response.status_code, 302)