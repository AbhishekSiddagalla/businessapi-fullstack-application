import pytest
from unittest.mock import Mock
from django.contrib.auth.models import User
from menu.views import LoginView


@pytest.fixture
def create_user():
    # create test user
    User.objects.filter(username="test_user").delete()
    return User.objects.create_user(username="test_user", password="test_password123")

@pytest.mark.djangodb
class TestLoginView:

    @staticmethod
    def call_login_api(request):
        view = LoginView()
        return view.post(request)

    #testing with valid user credentials
    def test_with_valid_credentials(self, create_user):
        #mock the request with valid credentials
        request = Mock()
        request.data = {
            "username": "test_user",
            "password": "test_password123"
        }

        response = self.call_login_api(request)

        assert response.status_code == 200
        assert response.data["response"] == "login successful"
        assert "token" in response.data

    #tesing with invalid username
    def test_with_missing_username(self):
        request= Mock()
        request.data = {
            "username": "",
            "password": "test_password123"
        }

        response = self.call_login_api(request)

        assert response.status_code == 401
        assert response.data["error"] == "username is required"

    def test_with_missing_password(self):
        request= Mock()
        request.data = {
            "username": "test_user",
            "password": ""
        }

        response = self.call_login_api(request)

        assert response.status_code == 401
        assert response.data["error"] == "password is required"

    def test_with_invalid_user(self):
        request= Mock()
        request.data = {
            "username": "invalid_user",
            "password": "invalid_password"
        }

        response = self.call_login_api(request)

        assert response.status_code == 401
        assert response.data["error"] == "No user found"