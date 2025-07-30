import pytest
from unittest.mock import patch, Mock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

templates_list_url = "/api/v1/menu/templates-list/"

@pytest.mark.djangodb
class TestTemplatesListAPI:

    @staticmethod
    def jwt_token(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def create_user(self):
        User.objects.filter(username="test_user").delete()
        return User.objects.create_user(username="test_user", password="1234")


    @patch("menu.views.requests.get")
    def test_templates_list_api_with_valid_request(self, mock_get, create_user, api_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION= f"Bearer {token}")

        response = api_client.get(templates_list_url)

        assert response.status_code == 200
        assert response.data["response"] == "templates retrieved successfully"


    @patch("menu.views.requests.get")
    def test_templates_list_api_with_missing_token(self, mock_get, api_client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        response = api_client.get(templates_list_url)

        assert response.status_code == 401
        assert response.data["error"] == "invalid token"


    @patch("menu.views.requests.get")
    def test_templates_list_api_with_no_permission(self, mock_get, api_client, create_user):
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        response = api_client.get(templates_list_url)

        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

