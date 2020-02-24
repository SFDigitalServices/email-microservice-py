from sendgrid import SendGridAPIClient
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import (
    Mail, From, To, Cc, Bcc, Subject, SendAt, MimeType, TemplateId,
    Asm, GroupId, GroupsToDisplay, ReplyTo, BatchId)
import json
import falcon
from .helpers import helpers
from .hooks import validate_access
import sys, traceback, logging

@falcon.before(validate_access)
class EmailService():

    def on_post(self, req, resp):
        data = json.loads(req.stream.read())

        if 'personalizations' in data.keys() and data['personalizations'] is not None:
            for personalization in data['personalizations']:
                """ map fields from personalization to main email """
                for p_key, p_value in personalization.items():
                     data[p_key] = p_value
                self.sendEmail(data, resp)
        else:
            self.sendEmail(data, resp)

    def sendEmail(self, data, resp):
        local_helper = helpers.HelperService()
        """ Construct required outgoing email parameters """
        message = Mail()
 
        """ One line settings """
        message.from_email = From(data['from']['email'], data['from']['name'])
        message.subject = Subject(data['subject'])

        if 'send_at' in data.keys() and data['send_at'] is not None:
            message.send_at = data['send_at']
        if 'asm' in data.keys() and data['asm'] is not None:
            message.asm = Asm(GroupId(data['asm']['group_id']), GroupsToDisplay(data['asm']['groups_to_display']))
         
        if 'batch_id' in data.keys() and data['batch_id'] is not None:
            message.batch_id = BatchId(data['batch_id'])

        """ If template id is specified, set dynamic data for the template """
        if 'template_id' in data.keys() and data['template_id'] != "":
            message.template_id = TemplateId(data['template_id'])
            template_data = {}
            template_data.update(data['dynamic_template_data'])
            message.dynamic_template_data = template_data
    
        func_switcher = {
            "to": local_helper.getEmails,
            "cc": local_helper.getEmails,
            "bcc": local_helper.getEmails,
            "content": local_helper.getContent,
            "attachment": local_helper.getAttachments,
            "tracking_settings": local_helper.getEmailTrackings,
            "custom_arg": local_helper.getCustomArgs,
            "section": local_helper.getSections,
            "header": local_helper.getHeaders,
            "category": local_helper.getCategory
        }

        message.to = func_switcher.get("to")(data['to'], 'to')
        message.cc = func_switcher.get("cc")(data['cc'], 'cc')
        message.bcc = func_switcher.get("bcc")(data['bcc'], 'bcc')
        message.content = func_switcher.get("content")(data['content'])
        message.attachment = func_switcher.get("attachment")(data['attachments'])
        message.tracking_settings = func_switcher.get("tracking_settings")(data['tracking_settings'])
        message.custom_arg = func_switcher.get("custom_arg")(data['custom_args'])
        message.section = func_switcher.get("section")(data['sections'])
        message.header = func_switcher.get("header")(data['headers'])
        message.category = func_switcher.get("category")(data['categories'])

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

