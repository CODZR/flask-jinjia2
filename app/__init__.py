from flask import Flask


def create_app():
    app = Flask(__name__)
    
    from .test.app import test_oa as test_blueprint
    print(test_blueprint)

    app.register_blueprint(test_blueprint)

    return app
