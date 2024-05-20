import os
from flask import Flask, jsonify, request, render_template, session
from flask_mail import Mail, Message
import stripe

test_items = [{"name": "earrings", "price_sgd": 5, "price_id": "price_1PIOMZ2M890h7uzkkCrpjJbU"},
              {"name": "ring", "price_sgd": 8, "price_id": "price_1PIOME2M890h7uzkQAQp4UXd"},
              {"name": "necklace", "price_sgd": 10, "price_id": "price_1PINUj2M890h7uzkpq2Dlw6b"}]

# Test secret API key:
stripe.api_key = os.environ.get("API_SECRET_KEY")

app = Flask(__name__)
app.secret_key = "Some secret key"   # Needed to use session variable
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("SENDER_EMAIL")
app.config['MAIL_PASSWORD'] = os.environ.get("SENDER_PASSWORD")

mail = Mail(app)

YOUR_DOMAIN = 'http://localhost:5000'


@app.route('/')
def home():
    return render_template('index.html', test_items=test_items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/checkout')
def checkout():
    price_id = request.args.get("price_id")
    item_name = request.args.get("item_name")

    session["price_id"] = price_id
    return render_template('checkout.html', item_name=item_name)


@app.route('/return')
def return_home():
    return render_template('return.html')


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    price_id = session.get("price_id")
    session.pop("price_id", None)
    try:
        stripe_session = stripe.checkout.Session.create(
            ui_mode='embedded',
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            return_url=YOUR_DOMAIN + '/return?session_id={CHECKOUT_SESSION_ID}',
        )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=stripe_session.client_secret)


@app.route('/session-status', methods=['GET'])
def session_status():
    stripe_session = stripe.checkout.Session.retrieve(request.args.get('session_id'))

    if stripe_session.status == 'complete':
        send_confirmation_email(stripe_session.customer_details.email)

    return jsonify(status=stripe_session.status, customer_email=stripe_session.customer_details.email)


def send_confirmation_email(customer_email):
    msg = Message('Thank you for your purchase!',
                  sender=os.environ.get("SENDER_EMAIL"),
                  recipients=[customer_email])
    # Replace orders@example.com in here and the one in return.html to a valid email.
    msg.body = ('Thank you for purchasing from Tinted Twins! '
                'Be sure to email orders@example.com if you have any questions.')
    mail.send(msg)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
