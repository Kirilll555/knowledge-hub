import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock


class AuthViewsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных перед каждым тестом"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

    def test_index_view_anonymous_user(self):
        """Тест 1: Проверка главной страницы для неавторизованного пользователя"""
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('questions', response.context)
        self.assertIn('menu', response.context)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertIsNone(response.context['profile'])

    def test_index_view_authenticated_user(self):
        """Тест 2: Проверка главной страницы для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['questions_count'], 0)
        self.assertEqual(response.context['answers_count'], 0)

    def test_register_view_get(self):
        """Тест 4: Проверка GET-запроса на страницу регистрации"""
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('menu', response.context)

    def test_register_view_post_success(self):
        """Тест 5: Проверка успешной регистрации нового пользователя"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }

        response = self.client.post(reverse('register'), user_data)

        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Проверяем, что пользователь авторизован после регистрации
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_register_view_post_password_mismatch(self):
        """Тест 6: Проверка регистрации с несовпадающими паролями"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'differentpass'
        }

        response = self.client.post(reverse('register'), user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertContains(response, 'Пароли не совпадают')
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_view_post_existing_user(self):
        """Тест 7: Проверка регистрации существующего пользователя"""
        user_data = {
            'username': 'testuser',  # уже существует
            'email': 'another@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }

        response = self.client.post(reverse('register'), user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertContains(response, 'Пользователь уже существует')

    def test_login_view_get(self):
        """Тест 8: Проверка GET-запроса на страницу входа"""
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('menu', response.context)

    def test_login_view_post_success(self):
        """Тест 9: Проверка успешного входа пользователя"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(reverse('login'), login_data)

        self.assertRedirects(response, '/')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_view_post_failure(self):
        """Тест 10: Проверка неудачного входа с неправильными данными"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }

        response = self.client.post(reverse('login'), login_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Неверное имя пользователя или пароль')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_view(self):
        """Бонусный тест: Проверка выхода пользователя"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, '/')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_profile_view(self):
        """Бонусный тест: Проверка страницы профиля"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(
            reverse('profile', kwargs={'username': 'otheruser'})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertEqual(response.context['profile_user'], self.other_user)
        self.assertEqual(response.context['questions_count'], 0)
        self.assertEqual(response.context['answers_count'], 0)

    @patch('main.views_features.auth_views.get_profile')
    @patch('main.views_features.auth_views.get_user_settings')
    def test_settings_view_get(self, mock_settings, mock_profile):
        """Бонусный тест: Проверка GET-запроса страницы настроек"""
        mock_profile.return_value = {'nickname': 'TestUser', 'age': 25}
        mock_settings.return_value = {'theme': 'light', 'language': 'ru'}

        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('settings'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings.html')
        mock_profile.assert_called_once_with(self.user.id)
        mock_settings.assert_called_once_with(self.user.id)

    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.update_user_settings')
    def test_settings_view_post(self, mock_update_settings, mock_save_profile):
        """11 тест: Проверка POST-запроса настроек"""
        self.client.login(username='testuser', password='testpass123')

        post_data = {
            'nickname': 'NewNickname',
            'age': '30',
            'hobby': 'Programming',
            'main_subject': 'python',
            'notifications': 'on',
            'theme': 'dark',
            'language': 'en'
        }

        response = self.client.post(reverse('settings'), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings.html')
        self.assertTrue(response.context['saved'])

        # Проверяем, что функции сохранения вызваны с правильными аргументами
        mock_save_profile.assert_called_once()
        mock_update_settings.assert_called_once()