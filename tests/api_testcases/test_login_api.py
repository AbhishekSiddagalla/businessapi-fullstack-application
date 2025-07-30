import pytest

from django.contrib.auth.models import User
from rest_framework.test import APIClient

login_url = "/token/"

@pytest.mark.djangodb
class TestLoginAPI:

    @pytest.fixture
    def create_user(self):
        User.objects.filter(username="test_user").delete()
        return User.objects.create_user(username="test_user", password="test_password")

    @pytest.fixture
    def api_client(self):
        return APIClient()

    #valid data
    def test_api_with_valid_data(self, create_user, api_client):
        data = {
            "username": "test_user",
            "password": "test_password"
        }

        response = api_client.post(login_url, data=data, format= "json")

        assert response.status_code == 200
        assert response.data["response"] == "login successful"
        assert "token" in response.data

    #missing username
    def test_api_with_missing_username(self, create_user, api_client):
        data = {
            "password": "test_password"
        }

        response = api_client.post(login_url, data=data, format="json")

        assert response.status_code == 401
        assert response.data["error"] == "username is required"


    #missing password
    def test_api_with_missing_password(self, create_user, api_client):
        data = {
            "username": "test_user"
        }

        response = api_client.post(login_url, data=data, format="json")

        assert response.status_code == 401
        assert response.data["error"] == "password is required"


    #invalid user
    def test_api_with_invalid_user(self, create_user, api_client):
        data = {
            "username": "invalid_user",
            "password": "wrong_password"
        }

        response = api_client.post(login_url, data=data, format="json")

        assert response.status_code == 401
        assert response.data["error"] == "No user found"