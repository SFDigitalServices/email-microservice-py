# pylint: disable=redefined-outer-name,no-member,unused-argument
"""Tests for misc helper functions"""
from unittest.mock import patch
import service.resources.email as email
from tests import mocks

def test_personalization_multiple_emails():
    """test_personalization_multiple_emails"""
    post_json = mocks.EMAIL_MULTIPLE
    message = email.generate_message(post_json)
    assert len(post_json.get('to')) == \
            len(message.personalizations[0].tos)
    assert len(post_json.get('cc')) == \
            len(message.personalizations[0].ccs)
    assert len(post_json.get('bcc')) == \
            len(message.personalizations[0].bccs)

