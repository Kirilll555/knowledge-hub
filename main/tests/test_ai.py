import json

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

class AiSessionActionsTests(TestCase):
    fixtures = ['db.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='REF')
        self.client.force_login(self.user)

    def test_create_ai_session_post(self):
        response = self.client.post(reverse('create_ai_session'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_create_ai_session_get_fails(self):
        response = self.client.get(reverse('create_ai_session'))
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_delete_ai_session_post(self):
        response = self.client.post(reverse('delete_ai_session', kwargs={'session_id': 1}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_delete_ai_session_get_fails(self):
        response = self.client.get(reverse('delete_ai_session', kwargs={'session_id': 1}))
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_rename_ai_session_post_success(self):
        response = self.client.post(
            reverse('rename_ai_session', kwargs={'session_id': 1}),
            data=json.dumps({'title': 'New title'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_rename_ai_session_post_empty_title(self):
        response = self.client.post(
            reverse('rename_ai_session', kwargs={'session_id': 1}),
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_rename_ai_session_get_fails(self):
        response = self.client.get(reverse('rename_ai_session', kwargs={'session_id': 1}))
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_rename_ai_session_invalid_json(self):
        response = self.client.post(
            reverse('rename_ai_session', kwargs={'session_id': 1}),
            data='not-json',
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])