from flask import Flask
from flask_cors import CORS

APP_NAME = "flask-jinjia2"

from .bot.views import slack_blueprint

app = Flask(__name__)
app.register_blueprint(slack_blueprint)

CORS(app, resources=r"/*")


@app.route("/", methods=["GET"])
def index():
    return "ok"
