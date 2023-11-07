from flask import Flask


def create_app():
    app = Flask(__name__)
    
    # from .test.app import test_oa as test_blueprint
    from .stripe.app import stripe as stripe_blueprint
    print(stripe_blueprint)

    app.register_blueprint(stripe_blueprint)

    return app
