from unittest.mock import patch

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class IndexViewTests(TestCase):
    fixtures = ['db.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='REF')

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_status_ok(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_template(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_has_today_date(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertIn('today_date', response.context)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_has_page_title(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['page_title'], 'Knowledge Hub - Главная')

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_has_questions_list(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertIn('questions', response.context)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_passes_limit_to_recent_questions(self, mock_recent):
        mock_recent.return_value = []
        self.client.get(reverse('index'))
        mock_recent.assert_called_once_with(limit=10)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_profile_is_none(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertIsNone(response.context['profile'])

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_questions_count_zero(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['questions_count'], 0)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_answers_count_zero(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['answers_count'], 0)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_ratings_count_zero(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['ratings_received'], 0)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_user_in_context(self, mock_recent):
        mock_recent.return_value = []
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['user'].is_authenticated, False)

    @patch('main.views_features.main_views.get_recent_questions')
    def test_index_anonymous_recent_questions_from_mock(self, mock_recent):
        mock_recent.return_value = [{'id': 1, 'title': 'Q'}]
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['questions'], [{'id': 1, 'title': 'Q'}])

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_status_ok(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_template(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_calls_get_profile(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        self.client.get(reverse('index'))
        mock_profile.assert_called_once_with(self.user.id)

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_has_profile(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['profile'], {'nickname': 'REF'})

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_questions_count(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['questions_count'], 1)

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_answers_count(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['answers_count'], 1)

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_ratings_received(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertGreaterEqual(response.context['ratings_received'], 0)

    @patch('main.views_features.main_views.get_recent_questions')
    @patch('main.views_features.main_views.get_profile')
    def test_index_authenticated_user_in_context(self, mock_profile, mock_recent):
        mock_recent.return_value = []
        mock_profile.return_value = {'nickname': 'REF'}
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['user'].username, 'REF')
