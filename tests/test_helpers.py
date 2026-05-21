from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponseForbidden
from unittest.mock import patch
from main.views_features.helpers import (
    get_menu,
    moderator_required,
    admin_required,
    check_ban
)
from django.http import HttpResponse


class HelpersTestCase(TestCase):
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

        # Создаем модератора
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='moderator123',
            is_staff=True
        )

        # Создаем администратора
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        # Создаем заблокированного пользователя
        self.banned_user = User.objects.create_user(
            username='banneduser',
            email='banned@example.com',
            password='banned123'
        )

    def create_request(self, user=None):
        """Вспомогательный метод для создания запроса с пользователем"""
        request = self.factory.get('/')
        if user:
            request.user = user
        else:
            request.user = AnonymousUser()
        return request

    @patch('main.views_features.helpers.check_moderator_access')
    def test_get_menu_anonymous_user(self, mock_check_moderator):
        """Тест 1: Проверка меню для неавторизованного пользователя"""
        request = self.create_request()

        menu = get_menu(request)

        # Проверяем структуру меню
        self.assertIsInstance(menu, list)
        self.assertGreater(len(menu), 0)

        # Проверяем наличие пунктов для неавторизованного пользователя
        menu_names = [item['name'] for item in menu]
        self.assertIn('Главная', menu_names)
        self.assertIn('Задать вопрос', menu_names)
        self.assertIn('Спросить ИИ', menu_names)
        self.assertIn('Войти', menu_names)
        self.assertIn('Регистрация', menu_names)

        # Проверяем, что нет пунктов для авторизованных
        self.assertNotIn('Выйти', menu_names)
        self.assertNotIn('Настройки', menu_names)
        self.assertNotIn('Модерация', menu_names)

        # Проверяем, что check_moderator_access не вызывался
        mock_check_moderator.assert_not_called()

    @patch('main.views_features.helpers.check_moderator_access')
    def test_get_menu_authenticated_user(self, mock_check_moderator):
        """Тест 2: Проверка меню для обычного авторизованного пользователя"""
        mock_check_moderator.return_value = False
        request = self.create_request(self.user)

        menu = get_menu(request)

        menu_names = [item['name'] for item in menu]

        # Проверяем наличие пунктов для авторизованного пользователя
        self.assertIn('Главная', menu_names)
        self.assertIn(self.user.username, menu_names)
        self.assertIn('Настройки', menu_names)
        self.assertIn('Выйти', menu_names)

        # Проверяем URL для профиля
        profile_item = next(item for item in menu if item['name'] == self.user.username)
        self.assertEqual(profile_item['url'], f'/profile/{self.user.username}/')

        # Проверяем, что нет пункта "Модерация"
        self.assertNotIn('Модерация', menu_names)

        # Проверяем, что нет пунктов для неавторизованных
        self.assertNotIn('Войти', menu_names)
        self.assertNotIn('Регистрация', menu_names)

    @patch('main.views_features.helpers.check_moderator_access')
    def test_get_menu_moderator_user(self, mock_check_moderator):
        """Тест 3: Проверка меню для модератора"""
        mock_check_moderator.return_value = True
        request = self.create_request(self.moderator)

        menu = get_menu(request)

        menu_names = [item['name'] for item in menu]

        # Проверяем, что у модератора есть пункт "Модерация"
        self.assertIn('Модерация', menu_names)

        # Проверяем URL для модерации
        moderation_item = next(item for item in menu if item['name'] == 'Модерация')
        self.assertEqual(moderation_item['url'], '/moderation/')

    @patch('main.views_features.helpers.check_moderator_access')
    def test_get_menu_admin_user(self, mock_check_moderator):
        """Тест 4: Проверка меню для администратора"""
        mock_check_moderator.return_value = True
        request = self.create_request(self.admin)

        menu = get_menu(request)

        menu_names = [item['name'] for item in menu]

        # Проверяем, что у админа тоже есть пункт "Модерация"
        self.assertIn('Модерация', menu_names)
        self.assertIn(self.admin.username, menu_names)
        self.assertIn('Выйти', menu_names)

    def test_get_menu_structure(self):
        """Тест 5: Проверка структуры каждого пункта меню"""
        request = self.create_request(self.user)

        with patch('main.views_features.helpers.check_moderator_access', return_value=False):
            menu = get_menu(request)

        # Проверяем, что каждый пункт меню имеет правильную структуру
        for item in menu:
            self.assertIsInstance(item, dict)
            self.assertIn('name', item)
            self.assertIn('url', item)
            self.assertIsInstance(item['name'], str)
            self.assertIsInstance(item['url'], str)
            self.assertTrue(len(item['name']) > 0)
            self.assertTrue(len(item['url']) > 0)

    @patch('main.views_features.helpers.check_moderator_access')
    def test_moderator_required_decorator_with_moderator(self, mock_check_moderator):
        """Тест 6: Проверка декоратора moderator_required с модератором"""
        mock_check_moderator.return_value = True

        @moderator_required
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request(self.moderator)
        response = test_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
        mock_check_moderator.assert_called_once_with(self.moderator)

    @patch('main.views_features.helpers.check_moderator_access')
    def test_moderator_required_decorator_with_regular_user(self, mock_check_moderator):
        """Тест 7: Проверка декоратора moderator_required с обычным пользователем"""
        mock_check_moderator.return_value = False

        @moderator_required
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request(self.user)
        response = test_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn('Доступ запрещён', response.content.decode())
        mock_check_moderator.assert_called_once_with(self.user)

    @patch('main.views_features.helpers.check_admin_access')
    def test_admin_required_decorator_with_admin(self, mock_check_admin):
        """Тест 8: Проверка декоратора admin_required с администратором"""
        mock_check_admin.return_value = True

        @admin_required
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request(self.admin)
        response = test_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
        mock_check_admin.assert_called_once_with(self.admin)

    @patch('main.views_features.helpers.check_admin_access')
    def test_admin_required_decorator_with_moderator(self, mock_check_admin):
        """Тест 9: Проверка декоратора admin_required с модератором"""
        mock_check_admin.return_value = False

        @admin_required
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request(self.moderator)
        response = test_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn('Доступ запрещён', response.content.decode())
        self.assertIn('администратора', response.content.decode())
        mock_check_admin.assert_called_once_with(self.moderator)

    @patch('main.views_features.helpers.check_user_access')
    def test_check_ban_decorator_with_active_user(self, mock_check_user):
        """Бонусный тест 1: Проверка декоратора check_ban с активным пользователем"""
        mock_check_user.return_value = True

        @check_ban
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request(self.user)
        response = test_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
        mock_check_user.assert_called_once_with(self.user)

    @patch('main.views_features.helpers.check_moderator_access')
    def test_moderator_required_decorator_preserves_function_metadata(self, mock_check_moderator):
        """Бонусный тест 2: Проверка сохранения метаданных функции декоратором"""
        mock_check_moderator.return_value = True

        @moderator_required
        def test_view(request):
            """Test docstring"""
            return HttpResponse('OK')

        # Проверяем, что декоратор сохраняет имя функции и документацию
        self.assertEqual(test_view.__name__, 'test_view')
        self.assertEqual(test_view.__doc__, 'Test docstring')

    @patch('main.views_features.helpers.check_admin_access')
    def test_admin_required_decorator_with_regular_user(self, mock_check_admin):
        """Бонусный тест 3: Проверка декоратора admin_required с обычным пользователем"""
        mock_check_admin.return_value = False

        @admin_required
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request(self.user)
        response = test_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)

    @patch('main.views_features.helpers.check_moderator_access')
    def test_moderator_required_decorator_with_anonymous_user(self, mock_check_moderator):
        """Бонусный тест 4: Проверка декоратора moderator_required с анонимным пользователем"""
        mock_check_moderator.return_value = False

        @moderator_required
        def test_view(request):
            return HttpResponse('OK')

        request = self.create_request()  # Анонимный пользователь
        response = test_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_get_menu_with_special_characters_in_username(self):
        """Бонусный тест 5: Проверка меню с специальными символами в имени пользователя"""
        special_user = User.objects.create_user(
            username='user@test.com',
            email='special@example.com',
            password='test123'
        )

        request = self.create_request(special_user)

        with patch('main.views_features.helpers.check_moderator_access', return_value=False):
            menu = get_menu(request)

        # Проверяем, что пользователь с спецсимволами корректно отображается
        self.assertIn('user@test.com', [item['name'] for item in menu])