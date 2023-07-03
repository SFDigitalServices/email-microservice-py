""" Tests for email module """
from unittest.mock import patch
import pytest
from python_http_client.exceptions import HTTPError
from service.resources.db import HistoryModel
from tests import mocks
from tests.fixtures import db_session # pylint: disable=unused-import
from tasks import generate_template_content, utc_to_pacific, multiselect_dict_to_list, uploads_to_list, send_email, ERR_MSG_MAX_RETRIES

# pylint: disable=redefined-outer-name,unused-argument
@patch('urllib.request.urlopen')
def test_generate_template_content(mock_urlopen):
    """ test generate_template_content function """

    # Required parameters
    with pytest.raises(KeyError):
        generate_template_content({'url': 'https://www.foo.com'})
    with pytest.raises(KeyError):
        generate_template_content({'replacements': {'foo': 'bar'}})

    mock_urlopen.return_value.__enter__.return_value.read.return_value = str.encode(mocks.EMAIL_HTML)
    results = generate_template_content({
        'url': 'https://some.place.com',
        'replacements': {
            'what_knights_say': 'ni'
        }
    })

    assert results[0]['type'] == 'text/html'
    assert results[0]['value'] == '<h1>Knights that say ni!</h1>'
    assert results[1]['type'] == 'text/plain'
    assert results[1]['value'] == 'Knights that say ni!'

    # make sure builtin replace filter is working
    mock_urlopen.return_value.__enter__.return_value.read.return_value = str.encode("{{ str_val | replace('hi', 'hello') }} world!")
    results = generate_template_content({
        'url': 'https://some.place.net',
        'replacements': {
            'str_val': 'hi'
        }
    })
    assert results[0]['type'] == 'text/html'
    assert results[0]['value'] == 'hello world!'
    assert results[1]['type'] == 'text/plain'
    assert results[1]['value'] == 'hello world!'

def test_utc_to_pacific():
    """ test conversion of utc datetime string to pacific """
    date_string = utc_to_pacific(None, mocks.UTC_DATETIME_STRING)
    assert date_string == mocks.PACIFIC_DATETIME_STRING

def test_multiselect_dict_to_list():
    """ test conversion of multiselect to list """
    team = multiselect_dict_to_list(None, mocks.TEAM_MEMBERS)
    assert team == ["agent"]

def test_uploads_to_list():
    """ test conversion of formio uploads to list """
    uploads_list = uploads_to_list(None, mocks.UPLOADS)
    assert uploads_list == ["https://foo.s3.amazonaws.com/fake_file-3a3144b5-1050-4ceb-8bdc.pdf", "https://foo.s3.amazonaws.com/fake_file-3a3144b5-1050-4ceb-8bdc2.pdf"]

@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_send_email_task(mock_sendgrid_client, mock_urlopen, db_session):
    """ test send_email """
    mock_sendgrid_client.return_value.send.return_value.body = "sendgrid response goes here"
    mock_sendgrid_client.return_value.send.return_value.status = 200
    mock_urlopen.return_value.__enter__.return_value.read.side_effect = [mocks.EMAIL_HTML, b"fake_data", b"fake_data"]

    params = mocks.EMAIL_POST.copy()
    del params['content']
    params['template'] = mocks.TEMPLATE_PARAMS

    history = HistoryModel(request=params)
    db_session.add(history)
    db_session.commit()

    send_email.s(history.id).apply()

    db_session.refresh(history)
    assert history.result == "sendgrid response goes here"
    assert len(history.email_content) == 2
    assert history.processed_timestamp is not None

    db_session.delete(history)

@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_send_email_task_generic_error(mock_sendgrid_client, mock_urlopen, db_session):
    """ test generic error when calling sendgrid_client.send() """
    mock_sendgrid_client.return_value.send.side_effect = Exception("generic send error")
    mock_urlopen.return_value.__enter__.return_value.read.side_effect = [mocks.EMAIL_HTML, b"fake_data", b"fake_data"]

    params = mocks.EMAIL_POST.copy()
    del params['content']
    params['template'] = mocks.TEMPLATE_PARAMS

    history = HistoryModel(request=params)
    db_session.add(history)
    db_session.commit()

    send_email.s(history.id).apply()

    db_session.refresh(history)
    assert history.result == ERR_MSG_MAX_RETRIES
    assert history.email_content is None
    assert history.processed_timestamp is None

    db_session.delete(history)
    db_session.commit()

@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_send_email_task_sendgrid_error(mock_sendgrid_client, mock_urlopen, db_session):
    """ test sendgrid error when calling sendgrid_client.send() """
    print("test_send_email_task_sendgrid_error")
    mock_sendgrid_client.return_value.send.side_effect = raise_http_error
    mock_urlopen.return_value.__enter__.return_value.read.side_effect = [mocks.EMAIL_HTML, b"fake_data", b"fake_data"]

    params = mocks.EMAIL_POST.copy()
    del params['content']
    params['template'] = mocks.TEMPLATE_PARAMS

    history = HistoryModel(request=params)
    db_session.add(history)
    db_session.commit()

    send_email.s(history.id).apply()

    db_session.refresh(history)
    assert history.result == ERR_MSG_MAX_RETRIES
    assert history.email_content is None
    assert history.processed_timestamp is None

    db_session.delete(history)
    db_session.commit()

@pytest.mark.parametrize('test_input', [[{}], [{'name': 'Name'}], [{'email': 'Email'}]])
@patch('urllib.request.urlopen')
@patch('sendgrid.SendGridAPIClient')
def test_send_email_task_invalid_email_obj(mock_sendgrid_client, mock_urlopen, test_input, db_session):
    """ test send_email """
    mock_sendgrid_client.return_value.send.return_value.body = "sendgrid response goes here"
    mock_sendgrid_client.return_value.send.return_value.status = 200
    mock_urlopen.return_value.__enter__.return_value.read.side_effect = [mocks.EMAIL_HTML, b"fake_data", b"fake_data"]

    params = mocks.EMAIL_POST.copy()
    del params['content']
    params['template'] = mocks.TEMPLATE_PARAMS
    params['cc'] = test_input

    history = HistoryModel(request=params)
    db_session.add(history)
    db_session.commit()

    send_email.s(history.id).apply()

    db_session.refresh(history)
    assert history.result == "sendgrid response goes here"
    assert len(history.email_content) == 2
    assert history.processed_timestamp is not None

    db_session.delete(history)

def raise_http_error(arg):
    """ raise HTTPError """
    print("raise HTTPError")
    raise HTTPError(
        400,
        'sendgrid error reason',
        'sendgrid error body',
        None
    )
