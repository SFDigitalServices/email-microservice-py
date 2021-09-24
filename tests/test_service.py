# pylint: disable=redefined-outer-name,no-member,unused-argument
"""Tests for microservice"""
import json
from unittest.mock import patch
import jsend
import pytest
import falcon
from falcon import testing
import service.microservice
from tests import mocks

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])
    monkeypatch.setenv("SENDGRID_API_KEY", "abc123")

@pytest.fixture
def mock_env_no_access_key(monkeypatch):
    """ mock environment with no access key """
    monkeypatch.delenv("ACCESS_KEY", raising=False)

def test_welcome(client, mock_env_access_key):
    # pylint: disable=unused-argument
    # mock_env_access_key is a fixture and creates a false positive for pylint
    """Test welcome message response"""
    response = client.simulate_get('/welcome')
    assert response.status_code == 200

    expected_msg = jsend.success({'message': 'Welcome'})
    assert json.loads(response.content) == expected_msg

    # Test welcome request with no ACCESS_KEY in header
    client_no_access_key = testing.TestClient(service.microservice.start_service())
    response = client_no_access_key.simulate_get('/welcome')
    assert response.status_code == 403

def test_welcome_no_access_key(client, mock_env_no_access_key):
    # pylint: disable=unused-argument
    # mock_env_no_access_key is a fixture and creates a false positive for pylint
    """Test welcome request with no ACCESS_key environment var set"""
    response = client.simulate_get('/welcome')
    assert response.status_code == 403


def test_default_error(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """Test default error response"""
    response = client.simulate_get('/some_page_that_does_not_exist')

    assert response.status_code == 404

    expected_msg_error = jsend.error('404 - Not Found')
    assert json.loads(response.content) == expected_msg_error

@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_email(mock_sendgrid_client, mock_urlopen, client, mock_env_access_key):
    """Test email endpoint"""
    print("test_email")
    mock_sendgrid_client.return_value.send.return_value.body = "sendgrid response goes here"
    mock_sendgrid_client.return_value.send.return_value.status = 200
    mock_urlopen.return_value.__enter__.return_value.read.return_value = b"fake_data"

    response = client.simulate_post('/email', json=mocks.EMAIL_POST)

    assert response.status == falcon.HTTP_200

@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_email_template(mock_sendgrid_client, mock_urlopen, client, mock_env_access_key):
    """Test email endpoint"""
    print("test_email_template")
    mock_sendgrid_client.return_value.send.return_value.body = "sendgrid response goes here"
    mock_sendgrid_client.return_value.send.return_value.status = 200
    mock_urlopen.return_value.__enter__.return_value.read.side_effect = [mocks.EMAIL_HTML, b"fake_data", b"fake_data"]

    params = mocks.EMAIL_POST.copy()
    del params['content']
    params['template'] = mocks.TEMPLATE_PARAMS
    response = client.simulate_post('/email', json=params)

    assert response.status == falcon.HTTP_200

@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_email_error(mock_sendgrid_client, mock_urlopen, client, mock_env_access_key):
    """Test email endpoint"""
    print("test_email_error")
    mock_sendgrid_client.return_value.send.side_effect = Exception("Error!")
    mock_urlopen.return_value.__enter__.return_value.read.return_value = b"fake_data"

    response = client.simulate_post('/email', json=mocks.EMAIL_POST)

    assert response.status == falcon.HTTP_500
