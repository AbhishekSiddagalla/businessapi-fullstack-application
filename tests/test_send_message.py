import pytest
from unittest.mock import Mock, patch

from menu.views import SendMessageView

@pytest.fixture
def payload():
    return {
        "messaging_product": "whatsapp",
        "to": "0123456789",
        "type": "template",
        "template": {
            "name": "test_template",
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "header",
                    "parameters": [{"type": "text", "text": "test header"}]
                },
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": "test body"}]
                },
                {
                    "type": "footer",
                    "parameters": [{"type": "text", "text": "test footer"}]
                }
            ]
        }
    }

@pytest.mark.djangodb
class TestSendMessageView:

    @staticmethod
    def call_send_message_api(payload):
        request = Mock()
        request.data = payload
        view = SendMessageView()
        return view.post(request)

    @patch("menu.views.api_data")
    @patch("menu.views.requests.post")
    def test_with_valid_payload(self, mock_post, mock_api_data, payload):
        #mocking API data
        mock_api_data.api_version = "v22.0"
        mock_api_data.to_phone_number = "0123456789"
        mock_api_data.api_access_token = "test_token"

        #mocking response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        response = self.call_send_message_api(payload)

        assert response.status_code == 200
        assert response.data["response"] == "message sent successfully"

    @patch("menu.views.api_data")
    @patch("menu.views.requests.post")
    def test_with_missing_access_token(self, mock_post, mock_api_data, payload):
        # mocking API data
        mock_api_data.api_version = "v22.0"
        mock_api_data.to_phone_number = "0123456789"
        mock_api_data.api_access_token = None

        # mocking response
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"error": "Invalid token"}

        response = self.call_send_message_api(payload)

        assert response.status_code == 401
        assert response.data["error"] == "Invalid token"

    @patch("menu.views.api_data")
    @patch("menu.views.requests.post")
    def test_with_expired_access_token(self, mock_post, mock_api_data, payload):
        # mocking API data
        mock_api_data.api_version = "v22.0"
        mock_api_data.to_phone_number = "0123456789"
        mock_api_data.api_access_token = "expired_token"

        # mocking response
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"error": "Invalid token"}

        response = self.call_send_message_api(payload)

        assert response.status_code == 401
        assert response.data["error"] == "Invalid token"

    @patch("menu.views.api_data")
    @patch("menu.views.requests.post")
    def test_with_forbidden_access(self, mock_post, mock_api_data, payload):
        # mocking API data
        mock_api_data.api_version = "v22.0"
        mock_api_data.to_phone_number = "0123456789"
        mock_api_data.api_access_token = "dummy_token"

        # mocking response
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"error": "permission denied"}

        response = self.call_send_message_api(payload)

        assert response.status_code == 401
        assert response.data["error"] == "permission denied"

    def test_with_missing_phone_number(self, payload):
        payload["to"] = ""
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid or incorrect phone number"

    def test_with_missing_template_name(self,payload):
        payload["template"]["name"] = ""
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid template name"

    def test_with_missing_language_code(self, payload):
        payload["template"]["language"] = ""
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "unsupported language format"

    def test_with_missing_components(self,payload):
        payload["template"]["components"] = ""
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid message components"

    def test_with_missing_header_params(self,payload):
        payload["template"]["components"][0]["parameters"] = []
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid header params"

    def test_with_missing_body_params(self,payload):
        payload["template"]["components"][1]["parameters"] = ""
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid body params"

    def test_with_missing_footer_params(self,payload):
        payload["template"]["components"][2]["parameters"] = []
        response = self.call_send_message_api(payload)

        assert response.status_code == 400
        assert response.data["error"] == "invalid footer params"
