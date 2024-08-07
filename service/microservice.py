"""Main application module"""
import os
import json
import jsend
import sentry_sdk
import falcon
from .resources.db import create_session
from .resources.email import EmailService
from .resources.welcome import Welcome

def start_service():
    """Start this service
    set SENTRY_DSN environmental variable to enable logging with Sentry
    """
    # Initialize Sentry
    sentry_sdk.init(os.environ.get('SENTRY_DSN'))
    # Initialize Falcon
    api = falcon.App(middleware=[SQLAlchemySessionManager(create_session())])
    api.add_route('/welcome', Welcome())
    api.add_route('/email', EmailService())
    api.add_sink(default_error, '')
    return api

def default_error(_req, resp):
    """Handle default error"""
    resp.status = 404
    msg_error = jsend.error('404 - Not Found')

    sentry_sdk.capture_message(msg_error)
    resp.text = json.dumps(msg_error)

class SQLAlchemySessionManager:
    """
    Create a session for every request and close it when the request ends.
    """
    # pylint: disable=invalid-name
    def __init__(self, Session):
        self.Session = Session

    def process_resource(self, req, resp, resource, params):
        # pylint: disable=unused-argument
        """attach a db session for every resource"""
        resource.session = self.Session()

    def process_response(self, req, resp, resource, req_succeeded):
        # pylint: disable=unused-argument
        """close db session for every resource"""
        if hasattr(resource, 'session'):
            resource.session.close()
