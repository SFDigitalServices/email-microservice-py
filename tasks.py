"""defining celery task for background processing of vaccination notifications"""
# pylint: disable=unused-argument
import os
import datetime
import traceback
import urllib.request
import mimetypes
from dateutil.parser import parse
from dateutil import tz
from kombu import serialization
import celery
from python_http_client.exceptions import HTTPError
import sendgrid
from sendgrid.helpers.mail import (Mail, From, Subject, Asm, GroupId, GroupsToDisplay)
from jinja2 import Template
from jinja2.filters import FILTERS, pass_environment
from bs4 import BeautifulSoup
import celeryconfig
from service.resources.helpers.helpers import HelperService
from service.resources.db import create_session, HistoryModel

LOCAL_TZ = tz.gettz("America/Los_Angeles")
MAX_RETRIES = 10
ERR_MSG_MAX_RETRIES = "Exhausted number of retries"

serialization.register_pickle()
serialization.enable_insecure_serializers()

# pylint: disable=invalid-name
celery_app = celery.Celery('email-microservice')
celery_app.config_from_object(celeryconfig)
# pylint: enable=invalid-name

# celery task note - don't use retry_kwargs={'max_retries': MAX_RETRIES}
# because it doesn't properly set the self.max_retries variable
@celery_app.task(name="tasks.send_email",
                bind=True,
                autoretry_for=(Exception,),
                retry_backoff=True,
                retry_jitter=True,
                max_retries=MAX_RETRIES)
def send_email(self, record_id):
    # pylint: disable=no-member,too-many-arguments,too-many-statements
    """ send out single email """
    print(f"task:working on id - {record_id}")
    print(f"attempt no: {self.request.retries}")

    session = None
    db_session = None
    record = None

    try:
        session = create_session()
        db_session = session()

        record = db_session.query(HistoryModel).filter(HistoryModel.id == record_id).one()
        data = record.request

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

        record.email_content = [c.get() for c in message.contents]
        record.result = response.body
        record.processed_timestamp = datetime.datetime.now(LOCAL_TZ)
        db_session.commit()
    except HTTPError as err:
        print(f"send_grid error: {err.to_dict}")
    except Exception as err: # pylint: disable=broad-except
        print(f"task Error: {err}")
        print(traceback.format_exc())
        if self.request.retries >= self.max_retries:
            print(ERR_MSG_MAX_RETRIES)
            rollback(db_session, record)
        raise err
    finally:
        db_session.close()
        print(f"task:finished with id - {record_id}")

def rollback(db_session, record):
    """ try to reset the record """
    db_session.rollback()

    if record is not None:
        # set queue_timestamp to Null
        # so this record can be picked up again
        record.result = ERR_MSG_MAX_RETRIES
        db_session.commit()

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
