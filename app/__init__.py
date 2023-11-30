from flask import Flask


def create_app():
    app = Flask(__name__)

    from .slack.views import slack_blueprint

    app.register_blueprint(slack_blueprint)

    return app
