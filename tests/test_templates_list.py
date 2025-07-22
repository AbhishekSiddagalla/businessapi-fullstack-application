import pytest

from unittest.mock import Mock, patch

from menu.views import TemplatesListView

@pytest.mark.djangodb
class TestTemplatesList:

    @staticmethod
    def call_templates_list():
        request = Mock()
        view = TemplatesListView()
        return view.get(request)


    @patch("menu.views.api_data")
    @patch("menu.views.requests.get")
    def test_with_valid_request(self,mock_get,mock_api_data):
        # mocking api data
        mock_api_data.api_version = "V22.0"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = "test_token"

        #mocking response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"success": True}

        response = self.call_templates_list()

        assert response.status_code == 200
        assert response.data["response"] == "templates retrieved successfully"

    @patch("menu.views.requests.get")
    @patch("menu.views.api_data")
    def test_with_missing_token(self, mock_api_data, mock_get):
        mock_api_data.api_version = "V22.0"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = None

        # mocking response
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"error": "invalid token"}

        response = self.call_templates_list()

        assert response.status_code == 401
        assert response.data["error"] == "invalid token"

    @patch("menu.views.api_data")
    @patch("menu.views.requests.get")
    def test_with_expired_token(self, mock_get, mock_api_data):
        # mocking api data
        mock_api_data.api_version = "V22.0"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = ""

        # mocking response
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"error": "invalid token"}

        response = self.call_templates_list()

        assert response.status_code == 401
        assert response.data["error"] == "invalid token"