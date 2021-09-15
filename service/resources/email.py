""" Email """
import os
import json
import falcon
import sendgrid
from sendgrid.helpers.mail import (Mail, From, Subject, TemplateId, Asm, GroupId, GroupsToDisplay, BatchId)
from python_http_client.exceptions import HTTPError
from .helpers.helpers import HelperService
from .hooks import validate_access

@falcon.before(validate_access)
class EmailService():
    """ Email service """
    def on_post(self, req, resp):
        """ Implement POST """
        data = json.loads(req.bounded_stream.read())

        self.send_email(data, resp)

    @staticmethod
    def send_email(data, resp):
        """ Sends the email """
        #Construct required outgoing email parameters """
        message = Mail()

        #One line settings """
        message.from_email = From(data['from']['email'], data['from']['name'])
        message.subject = Subject(data['subject'])

        if 'asm' in data.keys() and data['asm'] is not None and data['asm']['group_id'] != '':
            message.asm = Asm(GroupId(data['asm']['group_id']),
                GroupsToDisplay(data['asm']['groups_to_display']))

        func_switcher = {
            "to": HelperService.get_emails,
            "cc": HelperService.get_emails,
            "bcc": HelperService.get_emails,
            "content": HelperService.get_content,
            "attachments": HelperService.get_attachments,
            "custom_args": HelperService.get_custom_args
            # "section": HelperService.get_sections,
            # "header": HelperService.get_headers,
            # "category": HelperService.get_category
        }

        message.to = func_switcher.get("to")(data['to'], 'to')
        if 'cc' in data.keys():
            message.cc = func_switcher.get("cc")(data['cc'], 'cc')
        if 'bcc' in data.keys():
            message.bcc = func_switcher.get("bcc")(data['bcc'], 'bcc')
        if 'content' in data.keys():
            message.content = func_switcher.get("content")(data['content'])
        if 'attachments' in data.keys():
            message.attachment = func_switcher.get("attachments")(data['attachments'])
        if 'custom_args' in data.keys():
            message.custom_arg = func_switcher.get("custom_args")(data['custom_args'])
        # if 'section' in data.keys():
        #     message.section = func_switcher.get("section")(data['sections'])
        # if 'header' in data.keys():
        #     message.header = func_switcher.get("header")(data['headers'])
        # if 'category' in data.keys():
        #     message.category = func_switcher.get("category")(data['categories'])

        #pylint: disable=broad-except
        try:
            #logging.warning(message.get())
            sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            response = sendgrid_client.send(message)

            resp.body = response.body
            resp.status = falcon.HTTP_200
        except Exception as error:
            print("send exception: {0}".format(error))
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(str(error))
