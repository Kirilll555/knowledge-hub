from unittest.mock import patch

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


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