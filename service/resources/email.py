""" Email """
import os
import json
import traceback
import urllib.request
import mimetypes
from dateutil.parser import parse
from dateutil import tz
import falcon
import sendgrid
from sendgrid.helpers.mail import (Mail, From, Subject, Asm, GroupId, GroupsToDisplay)
from jinja2 import DictLoader, Environment, select_autoescape
from bs4 import BeautifulSoup
from service.resources.db import HistoryModel
from .helpers.helpers import HelperService
from .hooks import validate_access

@falcon.before(validate_access)
class EmailService():
    """ Email service """
    def on_post(self, req, resp):
        """ Implement POST """
        # pylint: disable=broad-except,no-member
        history_event = HistoryModel()
        try:
            data = json.loads(req.bounded_stream.read())
            history_event.request = data

            history_event.email_content = self.send_email(data, resp)
            history_event.result = resp.text
        except Exception as error:
            print(f"EmailService exception: {error}")
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500   # pylint: disable=no-member
            resp.text = json.dumps(str(error))

            history_event.result = resp.text
        finally:
            self.session.add(history_event)
            self.session.commit()

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

        #logging.warning(message.get())
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)

        print(f"response: {response.body}")
        print(f"status: {response.status_code}")
        resp.text = response.body
        resp.status = falcon.HTTP_200   # pylint: disable=no-member

        return [c.get() for c in message.contents]

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
        if not isinstance(template_content, str):
            template_content = template_content.decode("utf-8")

        loader = DictLoader({
            'template': template_content
        })
        env = Environment(
            loader=loader,
            autoescape=select_autoescape()
        )
        # provide custom filters to the template
        env.filters = {
            'utcToPacific': utc_to_pacific
        }
        template = env.get_template('template')
        html_content = template.render(template_params['replacements'])

        result.append({
            "type": mimetypes.types_map['.html'],
            "value": html_content
        })

        soup = BeautifulSoup(html_content, features="html.parser")
        result.append({
            "type": mimetypes.types_map['.txt'],
            "value": soup.get_text()
        })

    return result

def utc_to_pacific(utc_string):
    """ convert utc string to America/Los_Angeles timezone string """
    utc_datetime = parse(utc_string)
    pacific_tz = tz.gettz("America/Los_Angeles")
    return utc_datetime.astimezone(pacific_tz).strftime("%b %-d, %Y %-I:%M:%S %p")
