"""
Set of helper functions to handler sendgrid email api options
"""
import base64
import urllib.request
from sendgrid.helpers.mail import (
    To, Cc, Bcc,
    CustomArg, Content, Attachment, FileName,
    FileContent, FileType)

class HelperService():
    """ Helper class for sendgrid options """
    @staticmethod
    def get_attachments(attachments):
        """ This function sets up email attachments """
        attachment_list = []

        for attachment in attachments:
            if 'path' in attachment.keys() and attachment['path'] is not None and attachment['path'] != "":
                file_path = attachment['path']
                req = urllib.request.Request(file_path)
                if attachment.get('headers'):
                    for header, header_value in attachment.get('headers').items():
                        req.add_header(header, header_value)
                with urllib.request.urlopen(req) as conn:
                    data = conn.read()
                    encoded = base64.b64encode(data).decode()
            else:
                encoded = base64.b64encode(bytes(attachment['content'], 'utf-8')).decode()

            attachment_list.append(Attachment(
                FileContent(encoded),
                FileName(attachment['filename']),
                FileType(attachment['type'])
            ))

        return attachment_list

    @staticmethod
    def get_custom_args(custom_args):
        """ This function sets up email custom args """
        custom_arg_list = []
        for custom_arg_key, custom_arg_value in custom_args.items():
            custom_arg_list.append(CustomArg(custom_arg_key, custom_arg_value))
        return custom_arg_list

    @staticmethod
    def get_emails(emails, email_type):
        """ This function sets up email type """
        email_list = []
        counter = 0
        for email in emails:
            if email_type == 'to':
                email_list.append(To(email['email'], email['name'], p=counter))
            elif email_type == 'cc':
                email_list.append(Cc(email['email'], email['name'], p=counter))
            elif email_type == 'bcc':
                email_list.append(Bcc(email['email'], email['name'], p=counter))
            counter += 1
        return email_list

    @staticmethod
    def get_content(contents):
        """ This function sets up email content """
        content_list = []
        for content in contents:
            content_list.append(Content(content['type'], content['value']))
        return content_list
