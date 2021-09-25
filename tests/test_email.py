""" Tests for email module """
from unittest.mock import patch
import pytest
from tests import mocks
from service.resources.email import generate_template_content

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
