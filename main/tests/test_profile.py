from unittest.mock import patch

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from main.models_features import Profile

User = get_user_model()


class RegisterViewTests(TestCase):
    fixtures = ['db.json']

    def setUp(self):
        self.client = Client()

    def test_register_get_status_ok(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_get_template(self):
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'register.html')

    def test_register_authenticated_redirects_home(self):
        user = User.objects.get(username='REF')
        self.client.force_login(user)
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.auth_views.log_auth')
    def test_register_post_missing_username(self, mock_log_auth):
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'a@b.com',
            'password': '12345',
            'password2': '12345',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заполните все обязательные поля')
        mock_log_auth.assert_called_once()

    @patch('main.views_features.auth_views.log_auth')
    def test_register_post_missing_password(self, mock_log_auth):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'a@b.com',
            'password': '',
            'password2': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заполните все обязательные поля')
        mock_log_auth.assert_called_once()

    @patch('main.views_features.auth_views.log_auth')
    def test_register_post_passwords_not_match(self, mock_log_auth):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'a@b.com',
            'password': '12345',
            'password2': '54321',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пароли не совпадают')
        mock_log_auth.assert_called_once()

    @patch('main.views_features.auth_views.log_auth')
    def test_register_post_existing_username(self, mock_log_auth):
        response = self.client.post(reverse('register'), {
            'username': 'REF',
            'email': 'same@mail.com',
            'password': '12345',
            'password2': '12345',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь с таким именем уже существует')
        mock_log_auth.assert_called_once()

    @patch('main.views_features.auth_views.auth_login')
    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.log_auth')
    def test_register_post_valid_redirects_home(self, mock_log_auth, mock_save_profile, mock_auth_login):
        response = self.client.post(reverse('register'), {
            'username': 'newuser1',
            'email': 'new@user.com',
            'password': '12345678',
            'password2': '12345678',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        mock_save_profile.assert_called_once()
        mock_auth_login.assert_called_once()
        mock_log_auth.assert_called()

    @patch('main.views_features.auth_views.auth_login')
    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.log_auth')
    def test_register_creates_user_in_db(self, mock_log_auth, mock_save_profile, mock_auth_login):
        before = User.objects.count()
        self.client.post(reverse('register'), {
            'username': 'brandnew',
            'email': 'brandnew@mail.com',
            'password': '12345678',
            'password2': '12345678',
        })
        self.assertEqual(User.objects.count(), before + 1)

    @patch('main.views_features.auth_views.auth_login')
    @patch('main.views_features.auth_views.save_profile')
    @patch('main.views_features.auth_views.log_auth')
    def test_register_calls_save_profile(self, mock_log_auth, mock_save_profile, mock_auth_login):
        self.client.post(reverse('register'), {
            'username': 'userprofiletest',
            'email': 'u@mail.com',
            'password': '12345678',
            'password2': '12345678',
        })
        mock_save_profile.assert_called_once()

    @patch('main.views_features.auth_views.auth_login')
    @patch('main.views_features.auth_views.log_auth')
    def test_register_creates_profile_in_db(self, mock_log_auth, mock_auth_login):
        self.client.post(reverse('register'), {
            'username': 'userprofiletest2',
            'email': 'u2@mail.com',
            'password': '12345678',
            'password2': '12345678',
        })
        self.assertTrue(Profile.objects.filter(user__username='userprofiletest2').exists())


class LoginViewTests(TestCase):
    fixtures = ['db.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='REF')

    def test_login_get_status_ok(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_get_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')

    def test_login_authenticated_redirects_home(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.auth_views.authenticate')
    @patch('main.views_features.auth_views.auth_login')
    @patch('main.views_features.auth_views.log_auth')
    def test_login_post_success_redirects_home(self, mock_log_auth, mock_auth_login, mock_authenticate):
        mock_authenticate.return_value = self.user
        response = self.client.post(reverse('login'), {
            'username': 'REF',
            'password': 'anything',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        mock_authenticate.assert_called_once()

    @patch('main.views_features.auth_views.authenticate')
    @patch('main.views_features.auth_views.auth_login')
    @patch('main.views_features.auth_views.log_auth')
    def test_login_post_success_redirects_next(self, mock_log_auth, mock_auth_login, mock_authenticate):
        mock_authenticate.return_value = self.user
        response = self.client.post(reverse('login') + '?next=/profile/REF/', {
            'username': 'REF',
            'password': 'anything',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/REF/')

    @patch('main.views_features.auth_views.authenticate')
    @patch('main.views_features.auth_views.log_auth')
    def test_login_post_invalid_shows_error(self, mock_log_auth, mock_authenticate):
        mock_authenticate.return_value = None
        response = self.client.post(reverse('login'), {
            'username': 'REF',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Неверное имя пользователя или пароль')

    @patch('main.views_features.auth_views.authenticate')
    @patch('main.views_features.auth_views.log_auth')
    def test_login_post_invalid_logs_auth(self, mock_log_auth, mock_authenticate):
        mock_authenticate.return_value = None
        self.client.post(reverse('login'), {
            'username': 'REF',
            'password': 'wrong',
        })
        mock_log_auth.assert_called_once()


class LogoutViewTests(TestCase):
    fixtures = ['db.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='REF')

    def test_logout_get_redirects_home(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_logout_post_redirects_home(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    @patch('main.views_features.auth_views.log_auth')
    def test_logout_authenticated_logs_event(self, mock_log_auth):
        self.client.force_login(self.user)
        self.client.get(reverse('logout'))
        mock_log_auth.assert_called_once()

    @patch('main.views_features.auth_views.log_auth')
    def test_logout_logs_out_user(self, mock_log_auth):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        mock_log_auth.assert_called_once()
