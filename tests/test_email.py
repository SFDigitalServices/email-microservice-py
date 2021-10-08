""" Tests for email module """
from unittest.mock import patch
import pytest
from tests import mocks
from service.resources.email import generate_template_content, utc_to_pacific, multiselect_dict_to_list, uploads_to_list

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

def test_utc_to_pacific():
    """ test conversion of utc datetime string to pacific """
    date_string = utc_to_pacific(mocks.UTC_DATETIME_STRING)
    assert date_string == mocks.PACIFIC_DATETIME_STRING

def test_multiselect_dict_to_list():
    """ test conversion of multiselect to list """
    team = multiselect_dict_to_list(mocks.TEAM_MEMBERS)
    assert team == ["agent"]

def test_uploads_to_list():
    """ test conversion of formio uploads to list """
    uploads_list = uploads_to_list(mocks.UPLOADS)
    assert uploads_list == ["https://foo.s3.amazonaws.com/fake_file-3a3144b5-1050-4ceb-8bdc.pdf", "https://foo.s3.amazonaws.com/fake_file-3a3144b5-1050-4ceb-8bdc2.pdf"]
