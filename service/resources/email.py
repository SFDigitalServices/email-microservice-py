""" Email """
import os
import json
import traceback
import urllib.request
import falcon
import sendgrid
from sendgrid.helpers.mail import (Mail, From, Subject, Asm, GroupId, GroupsToDisplay)
from jinja2 import Template
from bs4 import BeautifulSoup
from .helpers.helpers import HelperService
from .hooks import validate_access

@falcon.before(validate_access)
class EmailService():
    """ Email service """
    def on_post(self, req, resp):
        """ Implement POST """
        # pylint: disable=broad-except
        try:
            data = json.loads(req.bounded_stream.read())
            self.send_email(data, resp)
        except Exception as error:
            print(f"EmailService exception: {error}")
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500   # pylint: disable=no-member
            resp.text = json.dumps(str(error))

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
        data_keys = data.keys()
        if 'cc' in data_keys:
            message.cc = func_switcher.get("cc")(data['cc'], 'cc')
        if 'bcc' in data_keys:
            message.bcc = func_switcher.get("bcc")(data['bcc'], 'bcc')
        if 'template' in data_keys and not 'content' in data_keys:
            data['content'] = generate_template_content(data['template'])
            data_keys = data.keys()
        if 'content' in data_keys:
            message.content = func_switcher.get("content")(data['content'])
        if 'attachments' in data_keys:
            message.attachment = func_switcher.get("attachments")(data['attachments'])
        if 'custom_args' in data_keys:
            message.custom_arg = func_switcher.get("custom_args")(data['custom_args'])
        # if 'section' in data_keys:
        #     message.section = func_switcher.get("section")(data['sections'])
        # if 'header' in data_keys:
        #     message.header = func_switcher.get("header")(data['headers'])
        # if 'category' in data_keys:
        #     message.category = func_switcher.get("category")(data['categories'])

        #logging.warning(message.get())
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)

        resp.text = response.body
        resp.status = falcon.HTTP_200   # pylint: disable=no-member

def generate_template_content(template_params):
    """ generate array of html/plain text content from template """
    result = []

    # url and replacements are required
    if 'url' not in template_params:
        raise KeyError('url value is required for email template')
    if 'replacements' not in template_params:
        raise KeyError('replacement values are required for email template')

    with urllib.request.urlopen(template_params['url']) as conn:
        template_content = conn.read()
        template = Template(template_content)
        html_content = template.render(template_params['replacements'])

        result.append({
            "type": "text/html",
            "value": html_content
        })

        soup = BeautifulSoup(html_content, features="html.parser")
        result.append({
            "type": "text/plain",
            "value": soup.get_text()
        })

    return result
