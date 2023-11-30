import os
from flask import Response

from app import APP_NAME


SLACK_RESPOND_MESSAGE_QUEUE_NAME = f"{APP_NAME}-slack-respond-message"

EMPTY_RESPONSE = Response(status=204)
