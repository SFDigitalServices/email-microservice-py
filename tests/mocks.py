""" mocks """

EMAIL_POST = {
    "subject": "unit test",
    "to": [{
        "email": "recipient@sf.gov",
        "name": "recipient"
    }],
    "from": {
        "email": "sender@sf.gov",
        "name": "sender"
    },
    "content": [{
        "type": "text/plain",
        "value": "Hello world!"
    }],
    "attachments": [{
        "content": "YmFzZTY0IHN0cmluZw==",
        "filename": "file1.txt",
        "type": "text/plain"
    },{
        "filename": "test.pdf",
        "path": "https://www.sf.gov/test.pdf",
        "type": "application/pdf",
        "headers": {
            "api-key": "123ABC"
        }
    }],
    "cc": [{
        "email": "cc-recipient@sf.gov",
        "name": "cc-recipient"
    }],
    "bcc": [{
        "email": "bcc-recipient@sf.gov",
        "name": "bcc-recipient"
    }],
    "custom_args": {
        "foo": "bar",
        "hello": "world"
    },
    "asm": {
        "group_id": 1,
        "groups_to_display": [1, 2]
    }
}

TEMPLATE_PARAMS = {
        "url": "",
        "replacements": {
            "what_knights_say": "ni"
        }
    }

EMAIL_HTML = "<h1>Knights that say {{ what_knights_say }}!</h1>"

UTC_DATETIME_STRING = "2021-09-30T20:56:58.000Z"
PACIFIC_DATETIME_STRING = "Sep 30, 2021 1:56:58 PM"

TEAM_MEMBERS = {
    "": False,
    "agent": True,
    "engineer": False,
    "architect": False,
    "contractor": False,
    "authorized agent": False,
    "AUTHORIZED AGENT-OTHERS": False,
    "agentWithPowerOfAttorney": False
}

UPLOADS = [
    {
        "acl": "private",
        "key": "formio-live/fake_file-3a3144b5-1050-4ceb-8bdc.pdf",
        "url": "https://foo.s3.amazonaws.com/fake_file-3a3144b5-1050-4ceb-8bdc.pdf",
        "name": "fake_file-3a3144b5-1050-4ceb-8bdc.pdf",
        "size": 13264,
        "type": "application/pdf",
        "bucket": "bucket",
        "storage": "s3",
        "originalName": "fake_file.pdf"
    },
    {
        "acl": "private",
        "key": "formio-live/fake_file-3a3144b5-1050-4ceb-8bdc2.pdf",
        "url": "https://foo.s3.amazonaws.com/fake_file-3a3144b5-1050-4ceb-8bdc2.pdf",
        "name": "fake_file-3a3144b5-1050-4ceb-8bdc2.pdf",
        "size": 13264,
        "type": "application/pdf",
        "bucket": "bucket",
        "storage": "s3",
        "originalName": "fake_file2.pdf"
    }
]

EMAIL_MULTIPLE = {
    "subject": "unit test",
    "to": [
        {
        "email": "recipient1@sf.gov"
        },
        {
        "email": "recipient2@sf.gov",
        "name": "recipient2"
        }
    ],
    "from": {
        "email": "sender@sf.gov",
        "name": "sender"
    },
    "content": [{
        "type": "text/plain",
        "value": "Hello world!"
    }],
    "cc": [
        {
        "email": "cc-recipient1@sf.gov",
        "name": "cc-recipient1"
        },
        {
        "email": "cc-recipient2@sf.gov",
        "name": "cc-recipient2"
        },
        {
        "email": "cc-recipient3@sf.gov",
        "name": "cc-recipient3"
        },
        {
        "email": "cc-recipient4@sf.gov"
        },
        {
        "email": "cc-recipient5@sf.gov",
        "name": "cc-recipient5"
        }
    ],
    "bcc": [{
        "email": "bcc-recipient@sf.gov"
    }]
}
