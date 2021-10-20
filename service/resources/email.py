""" Email """
import json
import traceback
from copy import deepcopy
import falcon
from service.resources.db import HistoryModel
from tasks import send_email
from .hooks import validate_access

# pylint: disable=unused-argument,no-member

REQUIRED_PARAMS = ['from', 'to', 'subject']

@falcon.before(validate_access)
class EmailService():
    """ Email service """
    def on_post(self, req, resp):
        """ Implement POST """
        # pylint: disable=broad-except
        data = json.loads(req.bounded_stream.read())
        print(f"req: { data }")

        if self.validate(data, resp):
            history_event = HistoryModel()
            self.session.add(history_event)
            try:

                history_event.request = deepcopy(data)
                self.session.commit()

                send_email.apply_async(
                    args=(history_event.id,),
                    serializer='pickle')

                resp.status = falcon.HTTP_200
                resp.text = 'success'
            except Exception as error:
                print(f"EmailService.on_post exception: {error}")
                print(traceback.format_exc())
                resp.status = falcon.HTTP_500   # pylint: disable=no-member
                resp.text = json.dumps(str(error))

                history_event.result = resp.text
                self.session.commit()

    @staticmethod
    def validate(data, resp):
        """ validates the incoming request """
        missing_params = []
        for param in REQUIRED_PARAMS:
            if param not in data:
                missing_params.append(param)

        if len(missing_params) == 0:
            return True

        resp.text = f"Missing required parameters: {missing_params}"
        resp.status = falcon.HTTP_400
        return False
