import os

from flask import Blueprint, jsonify, request
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App

from .ai.views import slack_ai_blueprint


bot_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

slack_handler = SlackRequestHandler(bot_app)


slack_blueprint = Blueprint(
    "slack",
    __name__,
    url_prefix="/slack",
)

slack_blueprint.register_blueprint(slack_ai_blueprint)


@slack_blueprint.route("/", methods=["GET"])
def test():
    return jsonify({"hello": "slack"})


# @slack_blueprint.route("/events", methods=["POST"])
# def slack_events():
#     return slack_handler.handle(request)
