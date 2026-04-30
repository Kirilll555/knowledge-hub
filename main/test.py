import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class AskQuestionViewTests(TestCase):
    fixtures = ['db.json']  # в db.json есть User с username='REF'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='REF')  # имя из db.json
        self.client.force_login(self.user)

    def test_get_returns_form(self):
        url = reverse('ask')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_empty_fields(self):
        url = reverse('ask')
        response = self.client.post(url, {'title': '', 'content': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заполните все поля')

    def test_post_valid_data(self):
        url = reverse('ask')
        response = self.client.post(url, {
            'title': 'Test title',
            'content': 'Test content',
        })
        self.assertEqual(response.status_code, 302)

    def test_post_redirects_to_question_detail(self):
        question_id = 2  # Укажи реальный ID, который ожидается
        # Или, если хочешь, чтобы тест принимал любой ID:

        url = reverse('ask')
        response = self.client.post(url, {
            'title': 'Test title',
            'content': 'Test content',
            'subject': 'general',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.url, r'^/question/\d+/$')

