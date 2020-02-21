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
                """ required parameters """
                data['to'] = personalization['to']
                """ optional """
                if 'subject' in personalization.keys() and  personalization['subject'] is not None:
                    data['subject'] = personalization['subject']
                if 'bcc' in personalization.keys() and   personalization['bcc'] is not None:
                    data['bcc'] = personalization['bcc']
                if 'cc' in personalization.keys() and   personalization['cc'] is not None:
                    data['cc'] = personalization['cc']
                if 'send_at' in personalization.keys() and   personalization['send_at'] is not None:
                    data['send_at'] = personalization['send_at']
                if 'headers' in personalization.keys() and  personalization['headers'] is not None:
                    data['headers'] = personalization['headers']
                if 'custom_args' in personalization.keys() and   personalization['custom_args'] is not None:
                    data['custom_args'] = personalization['custom_args']
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

        """ Set email address to send to """
        if 'to' in data.keys() and data['to'] is not None:
           message.to = local_helper.getEmails(data['to'], 'to')

        """ Set CC """
        if 'cc' in data.keys() and data['cc'] is not None:
            message.cc = local_helper.getEmails(data['cc'], 'cc')
        """ Set Bcc """
        if 'bcc' in data.keys() and data['bcc'] is not None:
            message.bcc = local_helper.getEmails(data['bcc'], 'bcc')

        """ If content is set, use as email content, otherwise template must be used """
        if 'content' in data.keys() and data['content'] is not None:
            message.content = local_helper.getContent(data['content'])

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

        """ Additional Sendgrid API features """
        if 'attachments' in data.keys() and data['attachments'] is not None:
            message.attachment = local_helper.getAttachments(data['attachments'])

        if 'tracking_settings' in data.keys() and data['tracking_settings'] is not None:
            message.tracking_settings = local_helper.getEmailTrackings(data['tracking_settings'])

        if 'custom_args' in data.keys() and data['custom_args'] is not None:
            message.custom_arg = local_helper.getCustomArgs(data['custom_args'])

        if 'email_settings' in data.keys() and data['mail_settings'] is not None:
            message.mail_settings = local_helper.getMailSettings(data['mail_settings'])

        if 'sections' in data.keys() and data['sections'] is not None:
            message.section = local_helper.getSections(data['sections'])

        if 'headers' in data.keys() and data['headers'] is not None:
            message.header = local_helper.getHeaders(data['headers'])

        if 'categories' in data.keys() and data['categories'] is not None:
            message.category = local_helper.getCategory(data['categories'])

        try:
            logging.warning(message.get())
            sendgrid_client = SendGridAPIClient(data['SENDGRID_API_KEY'])
            response = sendgrid_client.send(message)
            resp.body = response.body
            resp.status = falcon.HTTP_200
        except HTTPError as error:
            print(error.to_dict)
        except Exception as error:
            resp.body = json.dumps(str(error))

