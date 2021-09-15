EMAIL_POST = {
    'subject': 'unit test',
    'to': [{
        'email': 'recipient@sf.gov',
        'name': 'recipient'
    }],
    'from': {
        'email': 'sender@sf.gov',
        'name': 'sender'
    },
    'content': [{
        'type': 'text/plain',
        'value': 'Hello world!'
    }],
    'attachments': [{
        'content': 'YmFzZTY0IHN0cmluZw==',
        'filename': 'file1.txt',
        'type': 'text/plain'
    },{
        'filename': 'test.pdf',
        'path': 'https://www.sf.gov/test.pdf',
        'type': 'application/pdf'
    }],
    'cc': [{
        'email': 'cc-recipient@sf.gov',
        'name': 'cc-recipient'
    }],
    'bcc': [{
        'email': 'bcc-recipient@sf.gov',
        'name': 'bcc-recipient'
    }],
    'custom_args': {
        'foo': 'bar',
        'hello': 'world'
    },
    'asm': {
        'group_id': 1,
        'groups_to_display': [1, 2]
    }

}