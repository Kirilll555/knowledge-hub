import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock, PropertyMock
from main.models_features.question_feature import Question
from main.models_features.answer_rating_feature import Answer
from main.models_features.complaint_feature import Complaint


class ModerationViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()

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
            password='admin123'
        )

        # Создаем целевого пользователя для модерации
        self.target_user = User.objects.create_user(
            username='targetuser',
            email='target@example.com',
            password='target123'
        )

        # URL-ы (только те, что есть в urls.py)
        self.complaints_list_url = reverse('complaints_list')
        self.moderate_ban_url = reverse('moderate_ban_user', args=[self.target_user.id])
        self.moderate_unban_url = reverse('moderate_unban_user', args=[self.target_user.id])

    def login_as_admin(self):
        """Вход как администратор"""
        self.client.login(username='admin', password='admin123')

    def login_as_user(self):
        """Вход как обычный пользователь"""
        self.client.login(username='testuser', password='testpass123')

    @patch('main.views_features.moderation_views.get_all_complaints')
    def test_complaints_list_admin_access(self, mock_get_all):
        """Тест 1: Доступ к списку жалоб для администратора"""
        self.login_as_admin()

        mock_complaints = [
            MagicMock(id=1, reason='Spam'),
            MagicMock(id=2, reason='Harassment'),
        ]
        mock_get_all.return_value = mock_complaints

        response = self.client.get(self.complaints_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderation/complaints.html')
        self.assertEqual(len(response.context['complaints']), 2)

    def test_complaints_list_regular_user_access(self):
        """Тест 2: Доступ к списку жалоб для обычного пользователя"""
        self.login_as_user()

        response = self.client.get(self.complaints_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_complaints_list_anonymous_access(self):
        """Тест 3: Доступ к списку жалоб для анонимного пользователя"""
        response = self.client.get(self.complaints_list_url)

        # Ожидаем редирект на страницу логина
        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.moderation_views.update_complaint_status')
    def test_moderate_resolve_complaint_approve(self, mock_update_status):
        """Тест 4: Одобрение жалобы через moderate_resolve_complaint"""
        self.login_as_admin()

        complaint = Complaint.objects.create(
            user=self.user,
            target_type='question',
            complaint_type='spam',
            reason='Spam content',
            description='Test complaint'
        )

        data = json.dumps({'status': 'approved'})
        url = reverse('resolve_complaint', args=[complaint.id])

        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        mock_update_status.assert_called_once_with(complaint.id, 'approved')

    @patch('main.views_features.moderation_views.update_complaint_status')
    @patch('main.views_features.moderation_views.create_notification')
    @patch('main.views_features.moderation_views.delete_question')
    def test_resolve_complaint_approve_question(self, mock_delete_question,
                                                mock_notification, mock_update_status):
        """Тест 6: Одобрение жалобы на вопрос с удалением (resolve_complaint)"""
        self.login_as_admin()

        # Создаем вопрос для жалобы
        question = Question.objects.create(
            user=self.target_user,
            title='Bad Question',
            content='Bad content',
            is_deleted=False
        )

        # Создаем жалобу
        complaint = Complaint.objects.create(
            user=self.user,
            target_type='question',
            complaint_type='spam',
            reason='Spam',
            description='Bad question',
            question=question
        )

        url = reverse('resolve_complaint', args=[complaint.id])

        response = self.client.post(url, {'action': 'approve'})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        # Проверяем, что вопрос удален
        mock_delete_question.assert_called_once_with(question.id, self.admin.id)

        # Проверяем, что статус обновлен
        mock_update_status.assert_called_once_with(complaint.id, 'approved')

        # Проверяем, что уведомления отправлены (автору вопроса и автору жалобы)
        self.assertEqual(mock_notification.call_count, 2)

    @patch('main.views_features.moderation_views.update_complaint_status')
    @patch('main.views_features.moderation_views.create_notification')
    @patch('main.views_features.moderation_views.delete_answer')
    def test_resolve_complaint_approve_answer(self, mock_delete_answer,
                                              mock_notification, mock_update_status):
        """Тест 7: Одобрение жалобы на ответ с удалением (resolve_complaint)"""
        self.login_as_admin()

        # Создаем вопрос и ответ
        question = Question.objects.create(
            user=self.target_user,
            title='Test Question',
            content='Content',
            is_deleted=False
        )
        answer = Answer.objects.create(
            user=self.target_user,
            question=question,
            content='Bad answer',
            is_deleted=False
        )

        # Создаем жалобу
        complaint = Complaint.objects.create(
            user=self.user,
            target_type='answer',
            complaint_type='inappropriate',
            reason='Inappropriate',
            description='Bad answer',
            answer=answer
        )

        url = reverse('resolve_complaint', args=[complaint.id])

        response = self.client.post(url, {'action': 'approve'})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        mock_delete_answer.assert_called_once_with(answer.id, self.admin.id)
        mock_update_status.assert_called_once_with(complaint.id, 'approved')

    @patch('main.views_features.moderation_views.update_complaint_status')
    @patch('main.views_features.moderation_views.create_notification')
    def test_resolve_complaint_reject(self, mock_notification, mock_update_status):
        """Тест 8: Отклонение жалобы (resolve_complaint)"""
        self.login_as_admin()

        complaint = Complaint.objects.create(
            user=self.user,
            target_type='question',
            complaint_type='spam',
            reason='Spam',
            description='Test complaint'
        )

        url = reverse('resolve_complaint', args=[complaint.id])

        response = self.client.post(url, {'action': 'reject'})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('отклонена', response_data['message'])

        mock_update_status.assert_called_once_with(complaint.id, 'rejected')
        # Одно уведомление автору жалобы
        mock_notification.assert_called_once()

    def test_resolve_complaint_unauthorized(self):
        """Тест 9: Попытка решения жалобы обычным пользователем"""
        self.login_as_user()

        complaint = Complaint.objects.create(
            user=self.user,
            target_type='question',
            complaint_type='spam',
            reason='Spam'
        )

        url = reverse('resolve_complaint', args=[complaint.id])
        response = self.client.post(url, {'action': 'approve'})

        self.assertEqual(response.status_code, 403)

    @patch('subprocess.run')
    def test_moderate_ban_user_success(self, mock_subprocess):
        """Тест 10: Успешная блокировка пользователя"""
        self.login_as_admin()

        data = json.dumps({
            'reason': 'Spam',
            'days': 7
        })

        response = self.client.post(
            self.moderate_ban_url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        # Проверяем, что subprocess.run был вызван
        mock_subprocess.assert_called_once()

    @patch('main.views_features.moderation_views.unban_user')
    @patch('main.views_features.moderation_views.create_notification')
    def test_moderate_unban_user_success(self, mock_notification, mock_unban):
        """Тест 11: Успешная разблокировка пользователя"""
        self.login_as_admin()

        response = self.client.post(self.moderate_unban_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        mock_unban.assert_called_once_with(self.target_user.id, self.admin.id)
        mock_notification.assert_called_once()

    def test_moderate_ban_user_unauthorized(self):
        """Тест 12: Попытка бана обычным пользователем"""
        self.login_as_user()

        response = self.client.post(self.moderate_ban_url)

        self.assertEqual(response.status_code, 403)

    def test_moderate_ban_user_anonymous(self):
        """Тест 13: Попытка бана анонимным пользователем"""
        response = self.client.post(self.moderate_ban_url)

        self.assertEqual(response.status_code, 302)

    @patch('subprocess.run')
    def test_moderate_ban_user_with_exception(self, mock_subprocess):
        """Тест 14: Обработка ошибки при бане"""
        self.login_as_admin()

        mock_subprocess.side_effect = Exception('Script error')

        data = json.dumps({
            'reason': 'Spam',
            'days': 7
        })

        response = self.client.post(
            self.moderate_ban_url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)

    def test_resolve_complaint_invalid_method(self):
        """Тест 15: Неверный HTTP метод для решения жалобы"""
        self.login_as_admin()

        complaint = Complaint.objects.create(
            user=self.user,
            target_type='question',
            complaint_type='spam',
            reason='Spam'
        )

        url = reverse('resolve_complaint', args=[complaint.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    def test_resolve_complaint_anonymous(self):
        """Тест 16: Попытка решения жалобы анонимным пользователем"""
        complaint = Complaint.objects.create(
            user=self.user,
            target_type='question',
            complaint_type='spam',
            reason='Spam'
        )

        url = reverse('resolve_complaint', args=[complaint.id])
        response = self.client.post(url, {'action': 'approve'})

        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.moderation_views.create_notification')
    def test_moderate_unban_user_notification(self, mock_notification):
        """Тест 17: Проверка уведомления при разбане"""
        self.login_as_admin()

        # Мокаем unban_user
        with patch('main.views_features.moderation_views.unban_user'):
            response = self.client.post(self.moderate_unban_url)

        self.assertEqual(response.status_code, 200)

        # Проверяем, что уведомление отправлено с правильными параметрами
        mock_notification.assert_called_once_with(
            user_id=self.target_user.id,
            notification_type='system',
            title='🔓 Вы разблокированы',
            message='Ваш аккаунт разблокирован модератором',
            link='/'
        )

    def test_moderate_unban_user_unauthorized(self):
        """Тест 18: Попытка разбана обычным пользователем"""
        self.login_as_user()

        response = self.client.post(self.moderate_unban_url)

        self.assertEqual(response.status_code, 403)

    @patch('main.views_features.moderation_views.get_all_complaints')
    def test_complaints_list_with_data(self, mock_get_all):
        """Тест 19: Проверка данных в списке жалоб"""
        self.login_as_admin()

        mock_complaints = [
            MagicMock(
                id=1,
                reason='Spam',
                user=self.user,
                complaint_type='spam',
                description='Test 1',
                created_at='2024-01-01'
            ),
            MagicMock(
                id=2,
                reason='Harassment',
                user=self.target_user,
                complaint_type='harassment',
                description='Test 2',
                created_at='2024-01-02'
            ),
        ]
        mock_get_all.return_value = mock_complaints

        response = self.client.get(self.complaints_list_url)

        self.assertEqual(len(response.context['complaints']), 2)
        self.assertEqual(response.context['complaints'][0].reason, 'Spam')
        self.assertEqual(response.context['complaints'][1].reason, 'Harassment')

    @patch('subprocess.run')
    def test_moderate_ban_user_default_values(self, mock_subprocess):
        """Тест 20: Проверка значений по умолчанию при бане"""
        self.login_as_admin()

        # Отправляем пустые данные
        data = json.dumps({})

        response = self.client.post(
            self.moderate_ban_url,
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Проверяем, что subprocess.run вызван с правильными аргументами
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn('ban_user.py', call_args[1])
        self.assertEqual(call_args[2], str(self.target_user.id))
        self.assertEqual(call_args[3], 'Нарушение правил')
        self.assertEqual(call_args[4], '1')