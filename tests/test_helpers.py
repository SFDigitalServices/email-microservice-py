"""
Testing for the misc helper functions
"""

import pytest
from tasks import generate_message
from tests import mocks
from sendgrid.helpers.mail import To, Cc, Bcc

def test_personalization_multiple_emails():
    """test_personalization_multiple_emails"""
    post_json = mocks.EMAIL_MULTIPLE
    message = generate_message(post_json)
    assert len(post_json.get('to')) == \
            len(message.personalizations[0].tos)
    assert len(post_json.get('cc')) == \
            len(message.personalizations[0].ccs)
    assert len(post_json.get('bcc')) == \
            len(message.personalizations[0].bccs)
