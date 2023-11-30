from flask import Blueprint, jsonify, request
from .ai.views import slack_ai_blueprint

slack_blueprint = Blueprint(
    "slack",
    __name__,
    url_prefix="/slack",
)

slack_blueprint.register_blueprint(slack_ai_blueprint)


@slack_blueprint.route("/", methods=["GET"])
def test():
    return jsonify({"hello": "slack"})
