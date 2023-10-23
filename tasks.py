"""defining celery task for background processing of vaccination notifications"""
# pylint: disable=unused-argument
import os
import datetime
import traceback
import urllib.parse
import urllib.request
import mimetypes
from dateutil.parser import parse
from dateutil import tz
from kombu import serialization
import celery
from python_http_client.exceptions import HTTPError
import sendgrid
from sendgrid.helpers.mail import (Mail, From, To, Cc, Bcc, Personalization, Subject, Asm, GroupId, GroupsToDisplay, TrackingSettings, ClickTracking)
from jinja2 import Environment, BaseLoader
from jinja2.filters import FILTERS, pass_environment
from jinja2.exceptions import TemplateNotFound
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

        message = generate_message(data)

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

class UrlLoader(BaseLoader):
    """ Load remote Jinja templates via url """
    def __init__(self, path):
        """ init """
        self.path = path

    def get_source(self, environment, template):
        """ override get_source implementation """
        url = urllib.parse.urljoin(self.path, template)
        print(f"get_source url: {url}")
        try:
            with urllib.request.urlopen(url) as conn:
                template_content = conn.read()
                if not isinstance(template_content, str):
                    template_content = template_content.decode("utf-8")
                return template_content, None, True
        except Exception as err:
            raise TemplateNotFound(template) from err

def generate_template_content(template_params):
    """ generate array of html/plain text content from template """
    result = []

    # url and replacements are required
    if 'url' not in template_params:
        raise KeyError('url value is required for email template')
    if 'replacements' not in template_params:
        raise KeyError('replacement values are required for email template')

    index = template_params['url'].rfind('/')
    path = template_params['url'][:index+1]
    filename = template_params['url'][index+1:]
    template_env = Environment(loader=UrlLoader(path))
    template = template_env.get_template(filename)
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

def generate_message(data):
    """Construct required outgoing email parameters"""
    message = Mail()

    #One line settings """
    message.from_email = From(data['from']['email'], data['from']['name'])
    message.subject = Subject(data['subject'])

    if 'asm' in data.keys() and data['asm'] is not None and data['asm']['group_id'] != '':
        message.asm = Asm(GroupId(data['asm']['group_id']),
            GroupsToDisplay(data['asm']['groups_to_display']))

    # https://docs.sendgrid.com/for-developers/sending-email/smtp-filters#filter-clicktrack
    if 'filters' in data \
        and 'clicktrack' in data['filters'] \
        and 'settings' in data['filters']['clicktrack']:

        clicktrack_settings = data['filters']['clicktrack']['settings']
        clicktrack_enable = bool(clicktrack_settings.get('enable', False))
        clicktrack_enable_text = bool(clicktrack_settings.get('enable_text', False))

        tracking_settings = TrackingSettings()
        tracking_settings.click_tracking = ClickTracking(clicktrack_enable, clicktrack_enable_text)
        message.tracking_settings = tracking_settings

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
    print(f"message: {message}")
    return message

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
