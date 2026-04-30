import json
from unittest.mock import patch, MagicMock

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


class SettingsViewTests(TestCase):
    fixtures = ["db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="REF")
        self.client.force_login(self.user)

    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_get_status_ok(self, mock_profile, mock_settings):
        mock_settings.return_value = {"theme": "light"}
        mock_profile.return_value = {"nickname": "REF"}
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)

    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_get_uses_template(self, mock_profile, mock_settings):
        mock_settings.return_value = {"theme": "light"}
        mock_profile.return_value = {"nickname": "REF"}
        response = self.client.get(reverse("settings"))
        self.assertTemplateUsed(response, "settings.html")

    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_get_has_user_in_context(self, mock_profile, mock_settings):
        mock_settings.return_value = {}
        mock_profile.return_value = {}
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.context["user"].username, "REF")

    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_get_has_saved_none_without_query(
        self, mock_profile, mock_settings
    ):
        mock_settings.return_value = {}
        mock_profile.return_value = {}
        response = self.client.get(reverse("settings"))
        self.assertIsNone(response.context["saved"])

    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_get_has_saved_flag(self, mock_profile, mock_settings):
        mock_settings.return_value = {}
        mock_profile.return_value = {}
        response = self.client.get(reverse("settings") + "?saved=1")
        self.assertEqual(response.context["saved"], "1")

    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_invalid_age_status_ok(
        self, mock_profile, mock_settings, mock_validate
    ):
        mock_settings.return_value = {}
        mock_profile.return_value = {}
        mock_validate.return_value = (None, "Возраст должен быть положительным")
        response = self.client.post(
            reverse("settings"),
            {
                "age": "-5",
                "theme": "dark",
                "notifications": "on",
                "language": "ru",
                "nickname": "REF",
                "hobby": "coding",
                "main_subject": "physics",
                "email": "il_ppop@mail.ru",
            },
        )
        self.assertEqual(response.status_code, 200)

    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_invalid_age_has_errors(
        self, mock_profile, mock_settings, mock_validate
    ):
        mock_settings.return_value = {}
        mock_profile.return_value = {}
        mock_validate.return_value = (None, "Возраст должен быть положительным")
        response = self.client.post(
            reverse("settings"),
            {
                "age": "-5",
                "theme": "dark",
                "notifications": "on",
                "language": "ru",
                "nickname": "REF",
                "hobby": "coding",
                "main_subject": "physics",
                "email": "il_ppop@mail.ru",
            },
        )
        self.assertIn("errors", response.context)
        self.assertIn("age", response.context["errors"])

    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_invalid_age_error_text(
        self, mock_profile, mock_settings, mock_validate
    ):
        mock_settings.return_value = {}
        mock_profile.return_value = {}
        mock_validate.return_value = (None, "Возраст должен быть положительным")
        response = self.client.post(
            reverse("settings"),
            {
                "age": "-5",
                "theme": "dark",
                "notifications": "on",
                "language": "ru",
                "nickname": "REF",
                "hobby": "coding",
                "main_subject": "physics",
                "email": "il_ppop@mail.ru",
            },
        )
        self.assertEqual(
            response.context["errors"]["age"], "Возраст должен быть положительным"
        )

    @patch("main.views_features.profile_views.save_profile")
    @patch("main.views_features.profile_views.update_user_settings")
    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_valid_redirects(
        self,
        mock_profile,
        mock_settings,
        mock_validate,
        mock_update_settings,
        mock_save_profile,
    ):
        mock_settings.return_value = {"theme": "light"}
        mock_profile.return_value = {"nickname": "REF"}
        mock_validate.return_value = (20, None)
        response = self.client.post(
            reverse("settings"),
            {
                "age": "20",
                "theme": "dark",
                "notifications": "on",
                "language": "en",
                "nickname": "New REF",
                "hobby": "music",
                "main_subject": "math",
                "email": "il_ppop@mail.ru",
            },
        )
        self.assertEqual(response.status_code, 302)

    @patch("main.views_features.profile_views.save_profile")
    @patch("main.views_features.profile_views.update_user_settings")
    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_redirect_location(
        self,
        mock_profile,
        mock_settings,
        mock_validate,
        mock_update_settings,
        mock_save_profile,
    ):
        mock_settings.return_value = {"theme": "light"}
        mock_profile.return_value = {"nickname": "REF"}
        mock_validate.return_value = (20, None)
        response = self.client.post(
            reverse("settings"),
            {
                "age": "20",
                "theme": "dark",
                "notifications": "on",
                "language": "en",
                "nickname": "New REF",
                "hobby": "music",
                "main_subject": "math",
                "email": "il_ppop@mail.ru",
            },
        )
        self.assertEqual(response.url, "/settings/?saved=1")

    @patch("main.views_features.profile_views.save_profile")
    @patch("main.views_features.profile_views.update_user_settings")
    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_updates_settings(
        self,
        mock_profile,
        mock_settings,
        mock_validate,
        mock_update_settings,
        mock_save_profile,
    ):
        mock_settings.return_value = {"theme": "light"}
        mock_profile.return_value = {"nickname": "REF"}
        mock_validate.return_value = (20, None)
        self.client.post(
            reverse("settings"),
            {
                "age": "20",
                "theme": "dark",
                "notifications": "on",
                "language": "en",
                "nickname": "New REF",
                "hobby": "music",
                "main_subject": "math",
                "email": "il_ppop@mail.ru",
            },
        )
        mock_update_settings.assert_called_once()

    @patch("main.views_features.profile_views.save_profile")
    @patch("main.views_features.profile_views.update_user_settings")
    @patch("main.views_features.profile_views.validate_positive_integer")
    @patch("main.views_features.profile_views.get_user_settings")
    @patch("main.views_features.profile_views.get_profile")
    def test_settings_post_saves_profile(
        self,
        mock_profile,
        mock_settings,
        mock_validate,
        mock_update_settings,
        mock_save_profile,
    ):
        mock_settings.return_value = {"theme": "light"}
        mock_profile.return_value = {"nickname": "REF"}
        mock_validate.return_value = (20, None)
        self.client.post(
            reverse("settings"),
            {
                "age": "20",
                "theme": "dark",
                "notifications": "on",
                "language": "en",
                "nickname": "New REF",
                "hobby": "music",
                "main_subject": "math",
                "email": "il_ppop@mail.ru",
            },
        )
        mock_save_profile.assert_called_once()

    def test_settings_login_required_redirects(self):
        self.client.logout()
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 302)
