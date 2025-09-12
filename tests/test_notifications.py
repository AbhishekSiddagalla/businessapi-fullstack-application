import pytest
from unittest.mock import MagicMock, patch
from menu.notifications import send_message_to_teams

@patch("requests.post")
def test_send_message_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_post.return_value = mock_response

    url = "https://clientservertech1.webhook.office.com/webhook/mock-id"
    message = "Hello from testing"

    response = send_message_to_teams(url,message)

    assert response["response_status"] == 200
    assert response["response"] == "OK"


@patch("requests.post")
def test_send_message_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    url = "https://clientservertech1.webhook.office.com/webhook/mock-id"
    message = "Invalid Payload"

    response = send_message_to_teams(url, message)

    assert response["response_status"] == 400
    assert response["response"] == "Bad Request"


def test_send_message_with_invalid_webhook_url():
    url = "https://dummyurl.com"
    message = None

    with pytest.raises(ValueError, match="Invalid Teams Webhook URL"):
        send_message_to_teams(url, message)
