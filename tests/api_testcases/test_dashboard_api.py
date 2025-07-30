import pytest
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


dashboard_url = '/api/v1/menu/dashboard/'

@pytest.mark.djangodb
class TestDashboardAPI:

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

    def test_dashboard_api_with_valid_role(self, api_client, create_user):
        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        with patch("rest_framework_simplejwt.authentication.JWTAuthentication.get_user") as mock_get_user:
            setattr(create_user, "role", "user")
            mock_get_user.return_value = create_user

            response = api_client.get(dashboard_url)

            assert response.status_code == 200
            assert response.data["response"] == "welcome to dashboard"

    def test_dashboard_api_with_no_role(self,api_client):
        User.objects.filter(username="no_role").delete()
        user = User.objects.create_user(username="no_role", password="1234")
        token = self.jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.get(dashboard_url)

        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

