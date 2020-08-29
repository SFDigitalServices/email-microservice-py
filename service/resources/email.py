""" Email """
import json
import falcon
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, From, Subject, TemplateId, Asm, GroupId, GroupsToDisplay, BatchId)
from python_http_client.exceptions import HTTPError
from .helpers.helpers import HelperService
from .hooks import validate_access

@falcon.before(validate_access)
class EmailService():
    """ Email service """
    def on_post(self, req, resp):
        """ Implement POST """
        data = json.loads(req.stream.read())

        if 'personalizations' in data.keys() and data['personalizations'] is not None:
            for personalization in data['personalizations']:
                # map fields from personalization to main email """
                for p_key, p_value in personalization.items():
                    data[p_key] = p_value
                self.send_email(data, resp)
        else:
            self.send_email(data, resp)

    @staticmethod
    def send_email(data, resp):
        """ Sends the email """
        #Construct required outgoing email parameters """
        message = Mail()

        #One line settings """
        message.from_email = From(data['from']['email'], data['from']['name'])
        message.subject = Subject(data['subject'])

        if 'send_at' in data.keys() and data['send_at'] != '':
            message.send_at = data['send_at']
        if 'asm' in data.keys() and data['asm'] is not None and data['asm']['group_id'] != '':
            message.asm = Asm(GroupId(data['asm']['group_id']),
                              GroupsToDisplay(data['asm']['groups_to_display']))

        if 'batch_id' in data.keys() and data['batch_id'] != '':
            message.batch_id = BatchId(data['batch_id'])

        #If template id is specified, set dynamic data for the template
        if 'template_id' in data.keys() and data['template_id'] != "":
            message.template_id = TemplateId(data['template_id'])
            template_data = {}
            template_data.update(data['dynamic_template_data'])
            message.dynamic_template_data = template_data

        func_switcher = {
            "to": HelperService.get_emails,
            "cc": HelperService.get_emails,
            "bcc": HelperService.get_emails,
            "content": HelperService.get_content,
            "attachment": HelperService.get_attachments,
            "tracking_settings": HelperService.get_email_trackings,
            "custom_arg": HelperService.get_custom_args,
            "section": HelperService.get_sections,
            "header": HelperService.get_headers,
            "category": HelperService.get_category
        }

        message.to = func_switcher.get("to")(data['to'], 'to')
        if 'cc' in data.keys():
            message.cc = func_switcher.get("cc")(data['cc'], 'cc')
        if 'bcc' in data.keys():
            message.bcc = func_switcher.get("bcc")(data['bcc'], 'bcc')
        if 'content' in data.keys():
            message.content = func_switcher.get("content")(data['content'])
        if 'attachment' in data.keys():
            message.attachment = func_switcher.get("attachment")(data['attachments'])
        if 'tracking_settings' in data.keys():
            message.tracking_settings = func_switcher.get("tracking_settings")(data['tracking_settings'])
        if 'custom_arg' in data.keys():
            message.custom_arg = func_switcher.get("custom_arg")(data['custom_args'])
        if 'section' in data.keys():
            message.section = func_switcher.get("section")(data['sections'])
        if 'header' in data.keys():
            message.header = func_switcher.get("header")(data['headers'])
        if 'category' in data.keys():
            message.category = func_switcher.get("category")(data['categories'])

        #pylint: disable=broad-except
        try:
            #logging.warning(message.get())
            sendgrid_client = SendGridAPIClient(data['SENDGRID_API_KEY'])
            response = sendgrid_client.send(message)
            resp.body = response.body
            resp.status = falcon.HTTP_200
        except HTTPError as error:
            print(error.to_dict)
        except Exception as error:
            resp.body = json.dumps(str(error))
