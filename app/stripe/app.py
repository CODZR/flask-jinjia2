import json
import os
import stripe
from flask_cors import CORS

# This is your test secret API key.
stripe.api_key = 'sk_test_80PRE7i1wnVMXGukAzvGUFgk009F4Jwvps'

from flask import Flask, render_template, jsonify, request


app = Flask(__name__, static_folder='public',
            static_url_path='', template_folder='public')

CORS(app, resources=r'/*')


def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400


@app.route('/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        'clientSecret': 'dafdjaklf'
    })
@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='usd',
            # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
            automatic_payment_methods={
                'enabled': True,
            },
            # payment_method_types=["paypal"],
            # payment_method_options={"paypal": {"preferred_locale": "fr-BE"}},
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

if __name__ == '__main__':
    app.run(port=4242)