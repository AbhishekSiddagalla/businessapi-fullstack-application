import pytest
from unittest.mock import patch, PropertyMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

menu_url = '/api/v1/menu/'

@pytest.mark.djangodb
class TestMenuAPI:

    @staticmethod
    def jwt_token(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def create_admin_user(self):
        User.objects.filter(username="admin").delete()
        return User.objects.create_user(username="admin", password="admin_password")



    @pytest.fixture
    def create_normal_user(self):
        User.objects.filter(username="user").delete()
        user = User.objects.create_user(username="user", password="user_password")
        user.role = "user"
        user.save()
        return user


    #admin role
    def test_menu_api_with_admin_role(self, api_client, create_admin_user):
        print(create_admin_user)
        token = self.jwt_token(create_admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        with patch("rest_framework_simplejwt.authentication.JWTAuthentication.get_user") as mock_get_user:
            setattr(create_admin_user, "role", "admin")
            mock_get_user.return_value = create_admin_user

            response = api_client.get(menu_url)

        assert response.status_code == 200
        assert set(response.data["permissions"]) == {
            "user profile settings",
            "send message",
            "template list",
            "create template",
            "reports"
        }

    def test_menu_api_with_user_role(self, api_client, create_normal_user):
        token = self.jwt_token(create_normal_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        with patch("rest_framework_simplejwt.authentication.JWTAuthentication.get_user") as mock_get_user:
            setattr(create_normal_user, "role", "user")
            mock_get_user.return_value = create_normal_user

            response = api_client.get(menu_url)


        assert response.status_code == 200
        assert set(response.data["permissions"]) == {
            "send message",
            "template list",
            "create template",
            "reports"
        }

    def test_menu_api_with_no_role(self, api_client):
        User.objects.filter(username="no_role").delete()
        user = User.objects.create_user(username="no_role", password="no_pass")
        token = self.jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer{token}")

        response = api_client.get(menu_url)

        assert response.status_code == 401
