import json

from flask import Blueprint, request

# from app import APP_NAME


from .slack import handlers as slack_handlers

is_dev = True


slack_blueprint = Blueprint(
    "slack",
    __name__,
    url_prefix="/slack",
)


@slack_blueprint.route("/events", methods=["POST"])
def slack_event_handler():
    assert request is not None
    return slack_handlers.handle_webhook_event(request, is_dev=is_dev)
