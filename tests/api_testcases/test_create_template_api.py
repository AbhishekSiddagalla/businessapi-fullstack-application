import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from menu.api_data_config import api_version

create_template_url = "/api/v1/menu/create-template/"

@pytest.mark.djangodb
class TestCreateTemplateAPI:

    @staticmethod
    def jwt_token(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def create_user(self):
        User.objects.filter(username="user").delete()
        return User.objects.create_user(username="user", password="1234")

    @pytest.fixture
    def payload(self):
        return {
            "name": "test_template",
            "category": "UTILITY",
            "language": "en_US",
            "components": [
                {"type":"HEADER", "format": "IMAGE"},
                {"type": "BODY","text": "test_body"},
                {"type": "FOOTER","text": "test_footer"},
                {"type": "BUTTONS", "buttons": [{"type":"URL","text": "feedback", "url": "www.test.domain.com"}]}
            ]
        }

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_valid_data(self, mock_get_size, mock_post, api_client, create_user, payload):
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=200, json=lambda: {"h": "header_handle"}),
            MagicMock(status_code=200, json=lambda: {"response": "template created successfully"})
        ]

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 200
        assert response.data["response"] == "template created successfully"

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_missing_token(self, mock_get_ize, mock_post, api_client, payload):
        mock_get_ize.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=200, json=lambda: {"h": "header_handle"}),
            MagicMock(status_code=401, json=lambda: {"error": "invalid token"})
        ]

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 401

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_missing_name_field(self, mock_get_size, mock_post, payload, api_client, create_user):
        del payload["name"]
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=200, json=lambda: {"h": "header_handle"}),
            MagicMock(status_code=400, json=lambda: {"error": "invalid name"})
        ]

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid name"

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_missing_components(self, mock_get_size, mock_post, payload, api_client, create_user):
        del payload["components"]
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=200, json=lambda: {"h": "header_handle"}),
            MagicMock(status_code=400, json=lambda: {"error": "invalid components"})
        ]

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid components"

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_media_upload_failure(self, mock_get_size, mock_post, payload, api_client, create_user):
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=400, json=lambda: {"error": "media upload failed"}),
            MagicMock(status_code=400, json=lambda: {"error": "header handle fetch failed"}),
            MagicMock(status_code=400, json=lambda: {"error": "invalid header handle"})
        ]

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_media_upload_session_failure(self, mock_get_size, mock_post, payload, api_client, create_user):
        mock_get_size.return_value = 2048

        mock_post.return_value = MagicMock(status_code=400, json=lambda: {"error": "media upload failed"})

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    @patch("menu.views.requests.post")
    @patch("menu.views.os.path.getsize")
    def test_create_template_api_with_header_handle_fetch_failure(self, mock_get_size, mock_post, payload, api_client, create_user):
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=400, json=lambda: {"error": "header handle fetch failed"}),
            MagicMock(status_code=400, json=lambda: {"error": "invalid header handle"})
        ]

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(create_template_url, data=payload, format="json")

        assert response.status_code == 400
        assert "error" in response.data