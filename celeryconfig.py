"""celery configuration file"""
# pylint: disable=invalid-name

import os

# use local time
enable_utc = False

## Broker settings.
broker_url = os.environ['REDIS_URL']

# hard timeout after 45secs
# soft timeout after 30secs
task_time_limit = 45
task_soft_time_limit = 30

# redis priority messaging
# https://docs.celeryproject.org/en/latest/userguide/routing.html#redis-message-priorities
broker_transport_options = {
    'queue_order_strategy': 'priority',
}

# List of modules to import when the Celery worker starts.
imports = ('tasks',)

task_serializer = 'pickle'
accept_content = ['pickle', 'application/x-python-serialize', 'json', 'application/json']
