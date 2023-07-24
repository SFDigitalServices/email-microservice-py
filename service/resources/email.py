""" Email """
import os
import json
import traceback
import urllib.request
import mimetypes
from copy import deepcopy
from dateutil.parser import parse
from dateutil import tz
import falcon
import sendgrid
from sendgrid.helpers.mail import (Mail, From, Subject, Asm, GroupId, GroupsToDisplay, Personalization, To, Cc, Bcc)
from jinja2 import Template
from jinja2.filters import FILTERS, pass_environment
from bs4 import BeautifulSoup
from service.resources.db import HistoryModel
from .helpers.helpers import HelperService
from .hooks import validate_access

# pylint: disable=unused-argument

@falcon.before(validate_access)
class EmailService():
    """ Email service """
    def on_post(self, req, resp):
        """ Implement POST """
        # pylint: disable=broad-except,no-member
        history_event = HistoryModel()
        try:
            data = json.loads(req.bounded_stream.read())
            print(f"req: { data }")
            history_event.request = deepcopy(data)

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

        message = generate_message(data)

        #logging.warning(message.get())
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)

        print(f"response: {response.body}")
        print(f"status: {response.status_code}")
        resp.text = response.body
        resp.status = falcon.HTTP_200   # pylint: disable=no-member

        return [c.get() for c in message.contents]

def generate_message(data):
    """Construct required outgoing email parameters"""
    message = Mail()

    #One line settings """
    message.from_email = From(data['from']['email'], data['from']['name'])
    message.subject = Subject(data['subject'])

    if 'asm' in data.keys() and data['asm'] is not None and data['asm']['group_id'] != '':
        message.asm = Asm(GroupId(data['asm']['group_id']),
            GroupsToDisplay(data['asm']['groups_to_display']))

    func_switcher = {
        "content": HelperService.get_content,
        "attachments": HelperService.get_attachments,
        "custom_args": HelperService.get_custom_args
    }

    personalization = Personalization()

    for idx, email in enumerate(data['to']):
        personalization.add_to(To(email.get('email'), email.get('name', None), p=idx))

    data_keys = data.keys()
    if 'cc' in data_keys:
        for idx, email in enumerate(data['cc']):
            personalization.add_cc(Cc(email.get('email'), email.get('name', None), p=idx))
    if 'bcc' in data_keys:
        for idx, email in enumerate(data['bcc']):
            personalization.add_bcc(Bcc(email.get('email'), email.get('name', None), p=idx))
    if 'template' in data_keys and not 'content' in data_keys:
        data['content'] = generate_template_content(data['template'])
        data_keys = data.keys()
    if 'content' in data_keys:
        message.content = func_switcher.get("content")(data['content'])
    if 'attachments' in data_keys:
        message.attachment = func_switcher.get("attachments")(data['attachments'])
    if 'custom_args' in data_keys:
        message.custom_arg = func_switcher.get("custom_args")(data['custom_args'])

    message.add_personalization(personalization)
    return message

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
        template = Template(template_content)
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

@pass_environment
def utc_to_pacific(environment, utc_string):
    """ convert utc string to America/Los_Angeles timezone string """
    utc_datetime = parse(utc_string)
    pacific_tz = tz.gettz("America/Los_Angeles")
    return utc_datetime.astimezone(pacific_tz).strftime("%b %-d, %Y %-I:%M:%S %p")

@pass_environment
def multiselect_dict_to_list(environment, dict_multiselect):
    """ return list of keys in a dictionary who's values are True """
    keys_list = []
    for key, val in dict_multiselect.items():
        if val:
            keys_list.append(key)
    return keys_list

@pass_environment
def uploads_to_list(environment, uploads_list):
    """ return list of upload url """
    return [upload.get("url") for upload in uploads_list]

FILTERS['utcToPacific'] = utc_to_pacific
FILTERS['multiSelectToList'] = multiselect_dict_to_list
FILTERS['uploadsToList'] = uploads_to_list
