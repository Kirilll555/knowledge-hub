from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch


class ProfileViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()

        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Создаем другого пользователя
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='other123'
        )

        # URL-ы
        self.profile_url = reverse('profile', args=['testuser'])
        self.other_profile_url = reverse('profile', args=['otheruser'])
        self.settings_url = reverse('settings')

    def login_user(self):
        """Вход пользователя"""
        self.client.login(username='testuser', password='testpass123')

    @patch('main.views_features.auth_views.get_profile')
    def test_profile_view_own_profile(self, mock_get_profile):
        """Тест 1: Просмотр собственного профиля"""
        self.login_user()

        mock_get_profile.return_value = {
            'nickname': 'TestUser',
            'age': 25,
            'hobby': 'Programming',
            'main_subject': 'python',
            'role': 'user'
        }

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertIn('menu', response.context)
        self.assertIn('questions_count', response.context)
        self.assertIn('answers_count', response.context)

    @patch('main.views_features.auth_views.get_profile')
    def test_profile_view_other_user_profile(self, mock_get_profile):
        """Тест 2: Просмотр профиля другого пользователя"""
        self.login_user()

        mock_get_profile.return_value = {
            'nickname': 'OtherUser',
            'age': 30,
            'hobby': 'Reading',
            'main_subject': 'physics',
            'role': 'user'
        }

        response = self.client.get(self.other_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertEqual(response.context['profile_user'], self.other_user)
        self.assertEqual(response.context['questions_count'], 0)
        self.assertEqual(response.context['answers_count'], 0)

    def test_profile_view_anonymous(self):
        """Тест 4: Просмотр профиля без авторизации"""
        response = self.client.get(self.profile_url)

        # Профиль требует авторизации (декоратор @login_required)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    @patch('main.views_features.auth_views.get_user_settings')
    @patch('main.views_features.auth_views.get_profile')
    def test_settings_view_get(self, mock_get_profile, mock_get_settings):
        """Тест 5: GET-запрос страницы настроек"""
        self.login_user()

        mock_get_settings.return_value = {
            'notifications': True,
            'theme': 'light',
            'language': 'ru'
        }
        mock_get_profile.return_value = {
            'nickname': 'TestUser',
            'age': 25,
            'hobby': 'Programming',
            'main_subject': 'python',
            'role': 'user'
        }

        response = self.client.get(self.settings_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings.html')
        self.assertIn('settings', response.context)
        self.assertIn('profile', response.context)
        self.assertIn('menu', response.context)

    @patch('main.views_features.auth_views.update_user_settings')
    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.get_user_settings')
    @patch('main.views_features.auth_views.get_profile')
    def test_settings_view_post_success(self, mock_get_profile, mock_get_settings,
                                        mock_save_profile, mock_update_settings):
        """Тест 6: Успешное сохранение настроек"""
        self.login_user()

        mock_get_settings.return_value = {
            'notifications': True,
            'theme': 'dark',
            'language': 'en'
        }
        mock_get_profile.return_value = {
            'nickname': 'NewNickname',
            'age': 30,
            'hobby': 'Gaming',
            'main_subject': 'physics',
            'role': 'user'
        }

        post_data = {
            'nickname': 'NewNickname',
            'age': '30',
            'hobby': 'Gaming',
            'main_subject': 'physics',
            'theme': 'dark',
            'notifications': 'on',
            'language': 'en'
        }

        response = self.client.post(self.settings_url, post_data)

        # View рендерит страницу с saved=True, а не редиректит
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['saved'])

        # Проверяем, что save_profile вызван с правильными параметрами
        mock_save_profile.assert_called_once_with(
            self.user.id,
            self.user.username,
            {
                'nickname': 'NewNickname',
                'age': 30,
                'hobby': 'Gaming',
                'main_subject': 'physics',
            }
        )

        # Проверяем, что update_user_settings вызван
        mock_update_settings.assert_called_once_with(
            self.user.id,
            {
                'notifications': True,
                'theme': 'dark',
                'language': 'en',
            }
        )

    @patch('main.views_features.auth_views.get_user_settings')
    @patch('main.views_features.auth_views.get_profile')
    def test_settings_view_post_invalid_age(self, mock_get_profile, mock_get_settings):
        """Тест 7: Сохранение настроек с некорректным возрастом"""
        self.login_user()

        mock_get_settings.return_value = {'notifications': True, 'theme': 'light', 'language': 'ru'}
        mock_get_profile.return_value = {'nickname': 'TestUser', 'age': None, 'hobby': '', 'main_subject': 'general',
                                         'role': 'user'}

        post_data = {
            'nickname': 'TestUser',
            'age': '-5',
            'hobby': 'Gaming',
            'main_subject': 'physics',
            'theme': 'dark',
            'notifications': 'on',
            'language': 'en'
        }

        response = self.client.post(self.settings_url, post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        # Проверяем, что возраст стал None (некорректное значение)
        self.assertIsNone(response.context['profile']['age'])

    @patch('main.views_features.auth_views.update_user_settings')
    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.get_user_settings')
    @patch('main.views_features.auth_views.get_profile')
    def test_settings_view_post_without_notifications(self, mock_get_profile, mock_get_settings,
                                                      mock_save_profile, mock_update_settings):
        """Тест 8: Сохранение настроек без чекбокса уведомлений"""
        self.login_user()

        mock_get_settings.return_value = {'notifications': False, 'theme': 'light', 'language': 'ru'}
        mock_get_profile.return_value = {'nickname': 'TestUser', 'age': 25, 'hobby': 'Reading',
                                         'main_subject': 'general', 'role': 'user'}

        post_data = {
            'nickname': 'TestUser',
            'age': '25',
            'hobby': 'Reading',
            'main_subject': 'general',
            'theme': 'light',
            'language': 'ru'
            # Нет поля 'notifications'
        }

        response = self.client.post(self.settings_url, post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['saved'])

        # Проверяем, что notifications установлен в False
        mock_update_settings.assert_called_once_with(
            self.user.id,
            {
                'notifications': False,
                'theme': 'light',
                'language': 'ru',
            }
        )

    def test_settings_view_get_saved_param(self):
        """Тест 9: GET-запрос настроек с параметром saved"""
        self.login_user()

        # Мокаем функции, которые вызываются в settings view
        with patch('main.views_features.auth_views.get_user_settings') as mock_settings, \
                patch('main.views_features.auth_views.get_profile') as mock_profile:
            mock_settings.return_value = {'notifications': True, 'theme': 'light', 'language': 'ru'}
            mock_profile.return_value = {'nickname': 'TestUser', 'age': 25, 'hobby': 'Reading',
                                         'main_subject': 'general', 'role': 'user'}

            # GET-запрос без параметра saved
            response = self.client.get(self.settings_url)
            self.assertEqual(response.status_code, 200)
            # saved может быть None или отсутствовать
            self.assertFalse(response.context.get('saved'))

    @patch('main.views_features.auth_views.update_user_settings')
    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.get_user_settings')
    @patch('main.views_features.auth_views.get_profile')
    def test_settings_view_post_preserves_user_data(self, mock_get_profile, mock_get_settings,
                                                    mock_save_profile, mock_update_settings):
        """Тест 10: Сохранение настроек сохраняет существующие данные"""
        self.login_user()

        mock_get_settings.return_value = {'notifications': True, 'theme': 'dark', 'language': 'en'}
        mock_get_profile.return_value = {'nickname': 'TestUser', 'age': 25, 'hobby': 'Programming',
                                         'main_subject': 'python', 'role': 'user'}

        post_data = {
            'nickname': 'TestUser',
            'age': '25',
            'hobby': 'Programming',
            'main_subject': 'python',
            'theme': 'dark',
            'notifications': 'on',
            'language': 'en'
        }

        response = self.client.post(self.settings_url, post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['saved'])

        # Проверяем, что данные не изменились
        mock_save_profile.assert_called_once_with(
            self.user.id,
            self.user.username,
            {
                'nickname': 'TestUser',
                'age': 25,
                'hobby': 'Programming',
                'main_subject': 'python',
            }
        )