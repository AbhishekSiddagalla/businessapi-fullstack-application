import pytest

from unittest.mock import Mock, patch, MagicMock

from menu.views import CreateTemplateView
@pytest.mark.djangodb
class TestCreateTemplateView:

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

    @staticmethod
    def call_create_template_view(payload):
        request = Mock()
        request.data = payload
        view = CreateTemplateView()
        return view.post(request)

    @patch("menu.views.api_data_config")
    @patch("menu.views.os.path.getsize")
    @patch("menu.views.requests.post")
    def test_valid_payload(self, mock_post, mock_get_size, mock_api_data,payload):
        mock_api_data.api_version = "v22.0"
        mock_api_data.app_id = "123456"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = "access_token"
        mock_get_size.return_value = 2048

        #mocking response
        mock_post.side_effect = [
            MagicMock(status_code=200, json= lambda: {"id": "session_id"}),
            MagicMock(status_code=200, json=lambda: {"h": "header_handle"}),
            MagicMock(status_code=200, json=lambda: {"response": "template created successfully"})
        ]

        response = self.call_create_template_view(payload)
        print(response)

        assert response.status_code == 200
        assert response.data["response"] == "template created successfully"

    @patch("menu.views.api_data_config")
    @patch("menu.views.os.path.getsize")
    @patch("menu.views.requests.post")
    def test_with_expired_token(self, mock_post, mock_get_size, mock_api_data, payload):
        mock_api_data.api_version = "v22.0"
        mock_api_data.app_id = "123456"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = "expired_token"
        mock_get_size.return_value = 2048

        # mocking response
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=200, json=lambda: {"h": "header_handle"}),
            MagicMock(status_code=401, json=lambda: {"error": "invalid token"})
        ]

        response = self.call_create_template_view(payload)
        print(response.data)

        assert response.status_code == 401
        assert response.data["error"] == "invalid token"

    def test_with_missing_name_field(self, payload):
        del payload["name"]
        response = self.call_create_template_view(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid name"


    def test_with_missing_components(self, payload):
        del payload["components"]
        response = self.call_create_template_view(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid components"

    @patch("menu.views.api_data_config")
    @patch("menu.views.os.path.getsize")
    @patch("menu.views.requests.post")
    def test_with_media_upload_failure(self, mock_post, mock_get_size, mock_api_data, payload):
        mock_api_data.api_version = "v22.0"
        mock_api_data.app_id = "123456"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = "access_token"
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=400, json=lambda: {"error": "media upload failed"}),
            MagicMock(status_code=400, json=lambda: {"error": "header handle fetch failed "}),
            MagicMock(status_code=400, json=lambda: {"error": "invalid header handle"})
        ]

        response = self.call_create_template_view(payload)

        assert response.status_code == 400
        assert "error" in response.data

    @patch("menu.views.api_data_config")
    @patch("menu.views.os.path.getsize")
    @patch("menu.views.requests.post")
    def test_with_header_handle_failure(self, mock_post, mock_get_size, mock_api_data, payload):
        mock_api_data.api_version = "v22.0"
        mock_api_data.app_id = "123456"
        mock_api_data.whatsapp_business_account_id = "9876543210"
        mock_api_data.api_access_token = "access_token"
        mock_get_size.return_value = 2048

        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "session_id"}),
            MagicMock(status_code=400, json=lambda: {"error": "header handle fetch failed "}),
            MagicMock(status_code=400, json=lambda: {"error": "invalid header handle"})
        ]

        response = self.call_create_template_view(payload)

        assert response.status_code == 400
        assert "error" in response.data