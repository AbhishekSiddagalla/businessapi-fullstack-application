import pytest
from unittest.mock import patch, Mock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

send_message_url = "/api/v1/menu/send-message/"

@pytest.mark.djangodb
class TestSendMessageAPI:

    @staticmethod
    def jwt_token(user):
        refresh = RefreshToken.for_user(user)
        return refresh.access_token

    @pytest.fixture
    def create_user(self):
        User.objects.filter(username="test_user").delete()
        return User.objects.create_user(username="test_user", password="1234")

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def payload(self):
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

    @patch("menu.views.requests.post")
    def test_send_message_api_with_valid_payload(self, mock_post, create_user, api_client, payload):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(send_message_url, data=payload, format="json")
        print(response)
        assert response.status_code == 200
        assert response.data["response"] == "message sent successfully"


    @patch("menu.views.requests.post")
    def test_send_message_api_with_missing_token(self, mock_post, api_client, payload):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 401
        assert response.data["error"] == "invalid token"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_no_role(self,mock_post, api_client, payload):
        mock_response = Mock()
        mock_response.status_code = 403
        mock_post.return_value = mock_response

        User.objects.filter(username="no_role").delete()
        user = User.objects.create_user(username="no_role", password="1234")

        token = self.jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 403
        assert response.data["error"] == "permission denied"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_invalid_phone_number(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload["to"] = ""

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid or incorrect phone number"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_invalid_template_name(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload["template"]["name"] = ""

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid template name"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_unsupported_language(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION= f"Bearer {token}")

        payload["template"]["language"] = ""

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "unsupported language format"


    @patch("menu.views.requests.post")
    def test_send_message_api_with_missing_components(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload["template"]["components"] = ""

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid message components"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_missing_headers(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload["template"]["components"][0]["parameters"] = []

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid header params"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_missing_body(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload["template"]["components"][1]["parameters"] = []

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid body params"

    @patch("menu.views.requests.post")
    def test_send_message_api_with_missing_footer(self, mock_post, api_client, create_user, payload):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        token = self.jwt_token(create_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload["template"]["components"][2]["parameters"] = []

        response = api_client.post(send_message_url, data=payload, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "invalid footer params"