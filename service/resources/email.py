from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
import falcon
from .helpers import helpers
from .hooks import validate_access

@falcon.before(validate_access)
class EmailService():

    def on_post(self, req, resp):
        local_helper = helpers.HelperService()
        data = json.loads(req.stream.read())

        to_emails = [
            data['dynamic_template_data']['from']
        ]
        message = Mail(
            from_email=data['dynamic_template_data']['from'],
            to_emails=to_emails
            )
        message.dynamic_template_data = {
            'subject': data['dynamic_template_data']['subject'],
            'name': data['dynamic_template_data']['name'],
            'city': data['dynamic_template_data']['city'],
        }
        message.template_id = data['template_id']

        if data['file'] != None:
            message.attachment = local_helper.getAttachments(data['file'])
        try:
            sg = SendGridAPIClient(data['SENDGRID_API_KEY'])
            response = sg.send(message)
            resp.body = response.body
            resp.status = falcon.HTTP_200
        except Exception as e:
            resp.body = json.dumps(str(e))
