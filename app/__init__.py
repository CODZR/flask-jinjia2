from flask import Flask
from flask_cors import CORS
from .slack.views import slack_blueprint

APP_NAME = "flask-jinjia2"

app = Flask(__name__)
app.register_blueprint(slack_blueprint)

CORS(app, resources=r"/*")


@app.route("/", methods=["GET"])
def index():
    return "ok"
