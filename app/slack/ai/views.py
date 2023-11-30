from flask import Blueprint, jsonify


slack_ai_blueprint = Blueprint(
    "slack_ai",
    __name__,
    url_prefix="/ai",
)

print(123412)


@slack_ai_blueprint.route("/", methods=["GET"])
def ai3():
    return jsonify({"hello": "ai"})
