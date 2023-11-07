import json
import os
import stripe

from flask import Blueprint, jsonify, request

app = Blueprint("stripe", __name__, url_prefix="/stripe",)

# This is your test secret API key.
app.api_key = 'sk_test_80PRE7i1wnVMXGukAzvGUFgk009F4Jwvps'


def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'test': 'ok'
    })

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

