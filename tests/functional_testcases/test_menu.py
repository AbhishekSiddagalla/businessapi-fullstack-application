import pytest
from unittest.mock import Mock
from menu.views import MenuView

@pytest.mark.django_db
class TestMenuView:

    @staticmethod
    def call_menu_api(user):
        request = Mock()
        request.user = user
        return MenuView().get(request)

    def test_with_admin_user(self):
        user = Mock()
        user.role = "admin"
        response = self.call_menu_api(user)
        assert response.status_code == 200
        assert "user profile settings" in response.data["permissions"]

    def test_with_regular_user(self):
        user = Mock()
        user.role = "user"
        response = self.call_menu_api(user)
        assert response.status_code == 200
        assert "user profile settings" not in response.data["permissions"]
        assert "send message" in response.data["permissions"]

    def test_with_missing_role(self):
        user = Mock()
        delattr(user, "role")
        response = self.call_menu_api(user)
        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

    def test_with_missing_access_token(self):
        request = Mock()
        request.user = None

        view = MenuView()
        response = view.get(request)

        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

    def test_with_expired_access_token(self):
        user = Mock()
        user.role = None
        response = self.call_menu_api(user)
        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

    def test_with_forbidden_user(self):
        # valid token but the user has no permission
        user = Mock()
        user.role = None
        response = self.call_menu_api(user)
        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

