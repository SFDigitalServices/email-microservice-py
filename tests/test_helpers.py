import pytest
from sendgrid.helpers.mail import To, Cc, Bcc

from service.resources.helpers.helpers import HelperService

class TestGetEmails():
    @pytest.mark.parametrize('email_type', ['cc', 'bcc'])
    @pytest.mark.parametrize('test_input,expected', [
        ([{}], 0),
        ([{'name': 'Name'}], 0),
        ([{'email': 'test@test.com'}], 1),
        ([{'email': 'test@test.com', 'name': 'Name'}], 1),
        ([{'name': 'Name'}, {'email': 'test@test.com', 'name': 'Name'}], 1),
    ])
    def test_optional_email_types(self, email_type, test_input, expected):
        ret = HelperService.get_emails(test_input, email_type)
        assert len(ret) == expected

    @pytest.mark.parametrize('email_type', ['to', 'cc', 'bcc'])
    @pytest.mark.parametrize('test_input,expected', [
        ([{'email': 'test@test.com'}], None),
        ([{'email': 'test@test.com', 'name': 'Name'}], 'Name')
    ])
    def test_name_field_is_optional(self, email_type, test_input, expected):
        ret = HelperService.get_emails(test_input, email_type)
        assert ret[0].name == expected

    @pytest.mark.parametrize('email_type,test_input,expected', [
        ('to', [{'email': 'test@test.com'}], To),
        ('cc', [{'email': 'test@test.com'}], Cc),
        ('bcc', [{'email': 'test@test.com'}], Bcc)
    ])
    def test_appropriate_return_type(self, email_type, test_input, expected):
        ret = HelperService.get_emails(test_input, email_type)
        assert isinstance(ret[0], expected)