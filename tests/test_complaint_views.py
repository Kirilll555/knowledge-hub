import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock


class ComplaintViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()
        self.factory = RequestFactory()

        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Создаем администратора
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Создаем целевого пользователя для жалоб
        self.target_user = User.objects.create_user(
            username='baduser',
            email='bad@example.com',
            password='badpass123'
        )

        # URL для API
        self.complaint_url = reverse('create_complaint')

    def login_user(self):
        """Вспомогательный метод для входа пользователя"""
        self.client.login(username='testuser', password='testpass123')

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_question_success(self, mock_notification, mock_create_complaint):
        """Тест 1: Успешное создание жалобы на вопрос"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 1
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': 'This is spam content'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['complaint_id'], 1)

        # Проверяем, что create_complaint вызван с правильными параметрами
        mock_create_complaint.assert_called_once_with(
            user_id=self.user.id,
            target_type='question',
            complaint_type='spam',
            reason='spam',
            description='This is spam content',
            question_id=123
        )

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_answer_success(self, mock_notification, mock_create_complaint):
        """Тест 2: Успешное создание жалобы на ответ"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 2
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'answer',
            'target_id': 456,
            'complaint_type': 'inappropriate',
            'description': 'Inappropriate content in answer'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['complaint_id'], 2)

        mock_create_complaint.assert_called_once_with(
            user_id=self.user.id,
            target_type='answer',
            complaint_type='inappropriate',
            reason='inappropriate',
            description='Inappropriate content in answer',
            answer_id=456
        )

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_user_success(self, mock_notification, mock_create_complaint):
        """Тест 3: Успешное создание жалобы на пользователя"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 3
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'user',
            'target_id': self.target_user.id,
            'complaint_type': 'harassment',
            'description': 'User is harassing others'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        mock_create_complaint.assert_called_once_with(
            user_id=self.user.id,
            target_type='user',
            complaint_type='harassment',
            reason='harassment',
            description='User is harassing others',
            target_user_id=self.target_user.id
        )

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_with_reason(self, mock_notification, mock_create_complaint):
        """Тест 4: Создание жалобы с отдельным полем reason"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 4
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'question',
            'target_id': 789,
            'complaint_type': 'other',
            'reason': 'Custom reason for complaint',
            'description': 'Some description'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        mock_create_complaint.assert_called_once_with(
            user_id=self.user.id,
            target_type='question',
            complaint_type='other',
            reason='Custom reason for complaint',
            description='Some description',
            question_id=789
        )

    def test_create_complaint_anonymous_user(self):
        """Тест 5: Попытка создания жалобы неавторизованным пользователем"""
        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': 'Test complaint'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        # Ожидаем редирект на страницу логина
        self.assertEqual(response.status_code, 302)

    def test_create_complaint_get_request(self):
        """Тест 6: Попытка создания жалобы через GET-запрос"""
        self.login_user()

        response = self.client.get(self.complaint_url)

        # Ожидаем ошибку метода (405 Method Not Allowed)
        self.assertEqual(response.status_code, 405)

    def test_create_complaint_invalid_json(self):
        """Тест 7: Отправка некорректного JSON"""
        self.login_user()

        response = self.client.post(
            self.complaint_url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)

    def test_create_complaint_missing_required_fields(self):
        """Тест 8: Отправка без обязательных полей"""
        self.login_user()

        data = {
            'description': 'Missing required fields'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_empty_description(self, mock_notification, mock_create_complaint):
        """Тест 9: Создание жалобы с пустым описанием"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 5
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': ''
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_notifications_sent_to_admins(self, mock_notification, mock_create_complaint):
        """Тест 10: Проверка отправки уведомлений администраторам"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 6
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': 'Test notification'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Проверяем, что уведомление было отправлено админу
        mock_notification.assert_called_once()
        call_kwargs = mock_notification.call_args[1]
        self.assertEqual(call_kwargs['user_id'], self.admin.id)
        self.assertEqual(call_kwargs['notification_type'], 'system')
        self.assertIn('🚩 Новая жалоба', call_kwargs['title'])
        self.assertIn('testuser', call_kwargs['title'])

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_long_description_truncated(self, mock_notification, mock_create_complaint):
        """Тест 11: Проверка обрезания длинного описания в уведомлении"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 7
        mock_create_complaint.return_value = mock_complaint

        long_description = 'A' * 200  # Описание длиннее 100 символов

        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': long_description
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Проверяем, что описание обрезано до 100 символов
        notification_message = mock_notification.call_args[1]['message']
        description_in_message = notification_message.split('Описание: ')[1]
        self.assertLessEqual(len(description_in_message), 100)

    def test_create_complaint_all_complaint_types(self):
        """Тест 12: Проверка всех типов жалоб"""
        self.login_user()

        complaint_types = ['spam', 'inappropriate', 'harassment', 'other', 'violence']

        for complaint_type in complaint_types:
            with patch('main.views_features.complaint_views.create_complaint') as mock_create, \
                    patch('main.views_features.complaint_views.create_notification'):
                mock_complaint = MagicMock()
                mock_complaint.id = 8
                mock_create.return_value = mock_complaint

                data = {
                    'target_type': 'question',
                    'target_id': 123,
                    'complaint_type': complaint_type,
                    'description': f'Test {complaint_type} complaint'
                }

                response = self.client.post(
                    self.complaint_url,
                    data=json.dumps(data),
                    content_type='application/json'
                )

                self.assertEqual(response.status_code, 200)
                response_data = json.loads(response.content)
                self.assertTrue(response_data['success'])

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_exception_handling(self, mock_notification, mock_create_complaint):
        """Тест 13: Проверка обработки исключений"""
        self.login_user()

        # Настраиваем create_complaint для выброса исключения
        mock_create_complaint.side_effect = Exception('Database error')

        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': 'Test error handling'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Database error')

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_multiple_admins_notification(self, mock_notification, mock_create_complaint):
        """Тест 14: Проверка уведомлений для нескольких администраторов"""
        # Создаем дополнительных админов
        admin2 = User.objects.create_superuser(
            username='admin2',
            email='admin2@example.com',
            password='admin2pass123'
        )
        admin3 = User.objects.create_superuser(
            username='admin3',
            email='admin3@example.com',
            password='admin3pass123'
        )

        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 9
        mock_create_complaint.return_value = mock_complaint

        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam',
            'description': 'Test multiple admins'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Проверяем, что уведомления отправлены всем админам (3 вызова)
        self.assertEqual(mock_notification.call_count, 3)

        # Проверяем ID админов, которым отправлены уведомления
        notified_admin_ids = [
            call.kwargs['user_id'] for call in mock_notification.call_args_list
        ]
        self.assertIn(self.admin.id, notified_admin_ids)
        self.assertIn(admin2.id, notified_admin_ids)
        self.assertIn(admin3.id, notified_admin_ids)

    @patch('main.views_features.complaint_views.create_complaint')
    @patch('main.views_features.complaint_views.create_notification')
    def test_create_complaint_without_description_field(self, mock_notification, mock_create_complaint):
        """Тест 15: Создание жалобы без поля description"""
        self.login_user()

        mock_complaint = MagicMock()
        mock_complaint.id = 10
        mock_create_complaint.return_value = mock_complaint

        # Отправляем данные без поля description
        data = {
            'target_type': 'question',
            'target_id': 123,
            'complaint_type': 'spam'
        }

        response = self.client.post(
            self.complaint_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Проверяем, что description установлен как пустая строка
        mock_create_complaint.assert_called_once()
        call_kwargs = mock_create_complaint.call_args[1]
        self.assertEqual(call_kwargs['description'], '')