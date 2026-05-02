"""
Тесты для создания вопросов
"""

from unittest.mock import patch

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AskQuestionViewTests(TestCase):
    fixtures = ["db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="REF")
        self.client.force_login(self.user)

    def test_get_returns_form(self):
        url = reverse("ask")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_empty_fields(self):
        url = reverse("ask")
        response = self.client.post(url, {"title": "", "content": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заполните все поля")

    def test_post_valid_data(self):
        url = reverse("ask")
        response = self.client.post(
            url,
            {
                "title": "Test title",
                "content": "Test content",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_post_redirects_to_question_detail(self):
        url = reverse("ask")
        response = self.client.post(
            url,
            {
                "title": "Test title",
                "content": "Test content",
                "subject": "general",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.url, r"^/question/\d+/$")


class ProfileViewTests(TestCase):
    fixtures = ["db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="REF")
        self.client.force_login(self.user)

    @patch("main.views_features.profile_views.get_profile")
    @patch("main.views_features.profile_views.get_user_activities")
    def test_profile_ok_status(self, mock_activities, mock_profile):
        mock_profile.return_value = {"nickname": "REF"}
        mock_activities.return_value = []
        response = self.client.get(reverse("profile", kwargs={"username": "REF"}))
        self.assertEqual(response.status_code, 200)

    @patch("main.views_features.profile_views.get_profile")
    @patch("main.views_features.profile_views.get_user_activities")
    def test_profile_uses_profile_template(self, mock_activities, mock_profile):
        mock_profile.return_value = {"nickname": "REF"}
        mock_activities.return_value = []
        response = self.client.get(reverse("profile", kwargs={"username": "REF"}))
        self.assertTemplateUsed(response, "profile.html")

    @patch("main.views_features.profile_views.get_profile")
    @patch("main.views_features.profile_views.get_user_activities")
    def test_profile_context_has_profile_user(self, mock_activities, mock_profile):
        mock_profile.return_value = {"nickname": "REF"}
        mock_activities.return_value = []
        response = self.client.get(reverse("profile", kwargs={"username": "REF"}))
        self.assertEqual(response.context["profile_user"].username, "REF")

    @patch("main.views_features.profile_views.get_profile")
    @patch("main.views_features.profile_views.get_user_activities")
    def test_profile_context_has_current_user(self, mock_activities, mock_profile):
        mock_profile.return_value = {"nickname": "REF"}
        mock_activities.return_value = []
        response = self.client.get(reverse("profile", kwargs={"username": "REF"}))
        self.assertEqual(response.context["current_user"].username, "REF")

    @patch("main.views_features.profile_views.get_profile")
    @patch("main.views_features.profile_views.get_user_activities")
    def test_profile_calls_get_profile_with_user_id(
        self, mock_activities, mock_profile
    ):
        mock_profile.return_value = {"nickname": "REF"}
        mock_activities.return_value = []
        self.client.get(reverse("profile", kwargs={"username": "REF"}))
        mock_profile.assert_called_once_with(self.user.id)

    @patch("main.views_features.profile_views.get_profile")
    @patch("main.views_features.profile_views.get_user_activities")
    def test_profile_calls_get_user_activities_with_limit(
        self, mock_activities, mock_profile
    ):
        mock_profile.return_value = {"nickname": "REF"}
        mock_activities.return_value = []
        self.client.get(reverse("profile", kwargs={"username": "REF"}))
        mock_activities.assert_called_once_with(self.user.id, limit=50)

    def test_profile_404_for_missing_user(self):
        response = self.client.get(
            reverse("profile", kwargs={"username": "missing-user"})
        )
        self.assertEqual(response.status_code, 404)

    def test_profile_404_template(self):
        response = self.client.get(
            reverse("profile", kwargs={"username": "missing-user"})
        )
        self.assertTemplateUsed(response, "404.html")
